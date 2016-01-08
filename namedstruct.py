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
    # use unpack to create an instance of namedstructresult that holds the decoded data
    def __init__( self, name, field_info ):
        self.__name = name
        self.__field_name_to_getter = {}
        self.__all_fmt = []

        all_fmt = []
        index = 0
        for fmt_name in field_info.split():
            fmt, name = fmt_name.split( ':' )

            try:
                struct.calcsize( fmt )

            except struct.error as e:
                raise ValueError( 'index %d name %r fmt %r %s' % (index, name, fmt, e) )

            repeat = self.getRepeatCount( fmt )
            self.__all_fmt.append( (fmt, name) )

            all_fmt.append( fmt )
            if name != '' :
                if repeat == 1:
                    getter = operator.itemgetter( index )
                else:
                    getter = operator.itemgetter( slice( index, index + repeat ) )

                self.__field_name_to_getter[ name ] = getter

            index += repeat

        self.__struct_fmt_string = ''.join( all_fmt )

    def getRepeatCount( self, fmt ):
        if fmt[0] in '@=<>!':
            fmt = fmt[1:]

        if fmt[-1] == 's':
            return 1

        repeat = fmt[0:-1]

        if len(repeat) == 0:
            return 1

        return int(repeat)

    def unpack( self, encoded_buffer ):
        return namedstructresult( 
                    self.__name,
                    self.__field_name_to_getter,
                    self.__all_fmt,
                    self.__struct_fmt_string,
                    encoded_buffer )

    def __repr__( self ):
        return 'namedstruct<name:%s fmt:%s>' % (self.__name, self.__struct_fmt_string)

    def __len__( self ):
        return struct.calcsize( self.__struct_fmt_string )

class namedstructresult:
    def __init__( self, name, field_name_to_getter, all_fmt, struct_fmt_string, encoded_buffer ):
        self.__name = name
        self.__field_name_to_getter = field_name_to_getter
        self.__all_fmt = all_fmt

        self.__struct_fmt_string = struct_fmt_string

        self.__encoded_buffer = encoded_buffer
        self.__decoded_buffer = struct.unpack( self.__struct_fmt_string, self.__encoded_buffer )

    def __repr__( self ):
        return ('namedstructresult<name:%s fmt:%s size:%d>%r' %
                (self.__name, self.__struct_fmt_string, len(self), self.__decoded_buffer))

    def dump( self, write ):
        write( 'Dump of struct "%s"' % (self.__name,) )

        all_parts = []
        for index, byte in enumerate( self.__encoded_buffer ):
            if index%16 == 0:
                all_parts.append( '%8.8x' % (index,) )
            all_parts.append( '%2.2x' % (byte, ) )

            if index%16 == 15:
                all_parts.reverse()
                write( ' '.join( all_parts ) )
                all_parts = []

        offset = 0
        for fmt, name in self.__all_fmt:
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

