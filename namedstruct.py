#!/usr/bin/python3
#
#   namedstruct.py
#
#   allow the fields of a struct to be accessed by name
#
import struct
import operator

__all__ = ['namedstruct']

#
#   namedstruct( name, 'fmt1:name1 fmt2:name2 ...' )
#
#       blank name is a field to skip
#
#
class namedstruct:
    # holds the field definitions
    # use unpack to create an instance of namedstructunpacked that holds the decoded data
    def __init__( self, name, field_info ):
        self.__name = name
        self.__field_name_to_getter = {}
        self.__name_to_index = {}
        self.__all_fmt = []

        all_fmt = []
        index = 0
        for fmt_name in field_info.split():
            fmt, name = fmt_name.split( ':' )

            try:
                struct.calcsize( fmt )

            except struct.error as e:
                raise ValueError( 'index %d name %r fmt %r %s' % (index, name, fmt, e) )

            repeat = self.__getRepeatCount( fmt )
            self.__all_fmt.append( (fmt, name, repeat) )

            all_fmt.append( fmt )
            if name != '' :
                if repeat == 1:
                    getter = operator.itemgetter( index )
                else:
                    getter = operator.itemgetter( slice( index, index + repeat ) )

                self.__field_name_to_getter[ name ] = getter
                self.__name_to_index[ name ] = (fmt, index, index + repeat)

            index += repeat

        self.__struct_fmt_string = ''.join( all_fmt )

    def __getRepeatCount( self, fmt ):
        if fmt[0] in '@=<>!':
            fmt = fmt[1:]

        if fmt[-1] == 's':
            return 1

        repeat = fmt[0:-1]

        if len(repeat) == 0:
            return 1

        return int(repeat)

    def unpack( self, encoded_buffer ):
        return namedstructunpacked(
                    self.__name,
                    self.__field_name_to_getter,
                    self.__all_fmt,
                    self.__struct_fmt_string,
                    encoded_buffer )

    def packer( self, unpacked_data=None ):
        nsp = namedstructpacker(
                    self.__name,
                    self.__name_to_index,
                    self.__all_fmt,
                    self.__struct_fmt_string,
                    )
        if unpacked_data is not None:
            nsp.init_from( unpacked_data )

        return nsp

    def __repr__( self ):
        return 'namedstruct<name:%s fmt:%s>' % (self.__name, self.__struct_fmt_string)

    def __len__( self ):
        return struct.calcsize( self.__struct_fmt_string )

class namedstructunpacked:
    def __init__( self, name, field_name_to_getter, all_fmt, struct_fmt_string, encoded_buffer ):
        self.__name = name
        self.__field_name_to_getter = field_name_to_getter
        self.__all_fmt = all_fmt

        self.__struct_fmt_string = struct_fmt_string

        self.__encoded_buffer = encoded_buffer
        self.__decoded_buffer = struct.unpack( self.__struct_fmt_string, self.__encoded_buffer )

    def __repr__( self ):
        return ('namedstructunpacked<name:%s fmt:%s size:%d>%r' %
                (self.__name, self.__struct_fmt_string, len(self), self.__decoded_buffer))

    def dump( self, write, comment='' ):
        if comment != '':
            comment = ' - ' + comment

        write( 'Dump of struct "%s"%s' % (self.__name, comment) )

        all_parts = []
        all_chars = []
        for index, byte in enumerate( self.__encoded_buffer ):
            if index%16 == 0:
                all_parts.append( '%8.8x' % (index,) )
            all_parts.append( '%2.2x' % (byte, ) )
            if ord(' ') <= byte < 0x7f:
                all_chars.append( chr(byte) )
            else:
                all_chars.append( ' ' )

            if index%16 == 15:
                all_parts.reverse()
                all_parts.append( ' %s' % (''.join( all_chars),) )
                write( ' '.join( all_parts ) )
                all_parts = []
                all_chars = []

        if index%16 != 15:
            while index%16 != 15:
                all_parts.append( '  ' )
                index += 1

            all_parts.reverse()
            all_parts.append( ' %s' % (''.join( all_chars),) )
            write( ' '.join( all_parts ) )

        offset = 0
        for fmt, name, repeat in self.__all_fmt:
            if name == '':
                value = '-anonymous-'

            else:
                value = getattr( self, name )
                if type(value) == int:
                    value = '0x%X' % (value,)

                elif type(value) == bytes:
                    value = repr( value )[1:]

                else:
                    value = repr( value )

            write( '%8.8x %4s %14s  %s' % (offset, fmt, value, name) )
            offset += struct.calcsize( fmt )

        write( 'size = 0x%8.8x' % (offset,) )

    def __getattr__( self, name ):
        return self.__field_name_to_getter[ name ]( self.__decoded_buffer )

    def __len__( self ):
        return len( self.__encoded_buffer )

class namedstructpacker(object):
    def __init__( self, name, name_to_index, all_fmt, struct_fmt_string ):
        self.__name = name
        self.__name_to_index = name_to_index
        self.__all_fmt = all_fmt
        self.__struct_fmt_string = struct_fmt_string

        self.__values = []
        for name, fmt, repeat in self.__all_fmt:
            if repeat:
                self.__values.extend( [0]*repeat )
            else:
                if fmt.endswith('s'):
                    self.__values.append( b'' )
                else:
                    self.__values.append( 0 )

    def __repr__( self ):
        return ('namedstructpacker<name:%s fmt:%s size:%d>%r' %
                (self.__name, self.__struct_fmt_string, len(self)))

    def init_from( self, unpacked_data ):
        for name in self.__name_to_index:
            setattr( self, name, getattr( unpacked_data, name ) )

    def __getattr__( self, name ):
        if name.startswith( '_namedstructpacker__' ):
            return self.__dict__[ name ]

        elif name in self.__name_to_index:
            fmt, lo, hi = self.__name_to_index[ name ]

            if lo+1 == hi:
                return self.__values[ lo ]

            else:
                return self.__values[lo:hi]

        else:
            raise AttributesError( name )

    def __setattr__( self, name, value ):
        if name.startswith( '_namedstructpacker__' ):
            self.__dict__[ name ] = value

        elif name in self.__name_to_index:
            fmt, lo, hi = self.__name_to_index[ name ]

            if fmt[-1] == 's' and type( value ) is not bytes:
                raise ValueError( '%s expecting bytes not %r' % (name, value) )

            if lo+1 == hi:
                self.__values[ lo ] = value

            else:
                if len(value) != (hi-lo):
                    raise AttributeError( name )

                self.__values[lo:hi] = value
        else:
            raise AttributeError( name )

    def dump( self, write ):
        write( 'Dump of packer "%s"' % (self.__name,) )
        for name in self.__name_to_index:
            fmt, lo, hi = self.__name_to_index[ name ]
            print( '%r[%d:%d] = %r' % (fmt, lo, hi, self.__values[lo:hi]) )

    def pack( self ):
        return struct.pack( *[self.__struct_fmt_string] + self.__values )

    def __len__( self ):
        return struct.calcsize( self.__struct_fmt_string )

if __name__ == '__main__':
    ns = namedstruct( 'onetwo', 'H:first 1H:first2 2b: 2B:second 6s:third' )

    print( ns )
    data = ns.unpack( b'\x01\x83\x23\x12\x99\x45\xfe\xaaHelloW' )
    print( repr( data  ) )
    print( 'first', repr( data.first ) )
    print( 'first2', repr( data.first2 ) )
    print( 'second', repr( data.second ) )
    print( 'third', repr( data.third ) )
    data.dump( print )

    packer = ns.packer()
    packer.first = 19
    packer.first2 = 23
    packer.second = (2,5)
    packer.third = b'xyz'

    print( 'second: %r' % (packer.second,) )

    print( 'buf %r' % (packer.pack(),) )
