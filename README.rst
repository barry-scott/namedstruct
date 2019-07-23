Module namedstruct
------------------

namedstruct encapsulates struct.unpack() and struct.pack() with results accessed by name.

Classes
-------

  class namedstruct.namedstruct

    __init__( description, struct_definition )

        The *description* is used to title a dump of unpacked data.

        *struct_definition* is a single string that defines the type and name of each field
        as a space seperated list.
        Each field's type and name are seperated by a ":". If the name is left blank that
        field cannot be accessed by name, useful
        for padding fields. If a field's type has a repeat count the value returned with
        be a tuple of all the fields parts.

    len()

        Returns the size of the struct.

    unpack( bytes )

        Unpack the *bytes* into a namestruct.namestructresults object used to access the decoded fields.

    packer( from_unpacked=None )

        Return a namedstructpacker object that can be used to pack the fields into a buffer.
        The optional from_unpacked will initialise the fields from a previously unpacked
        buffer.

  class namedstruct.namedstructresults

    .*name*

       Returns the value of the field called name.

    dump( writer )

       Using the writer function to output a formatted dump of the whole struct.

  class namedstruct.namedstructpacker

    .*name* = value

        Assign a value to the named field

    init_from( from_unpacked )

        Assign each field from a previous unpacked buffer's namedstructresults.

    pack()

        Pack the fields and return the bytes buffer.

Example
-------

::

  import namedstruct

  # Windows EXE files start with a DOS header
  struct_windows_exe_header = namedstruct.namedstruct( 'DOS header', '<'
    '2s:dos_magic '
    'h:lastsize '
    'h:nblocks '
    'h:nreloc '
    'h:hdrsize '
    'h:minalloc '
    'h:maxalloc '
    'H:ss '
    'H:sp '
    'h:checksum '
    'H:ip '
    'H:cs '
    'h:relocpos '
    'h:noverlay '
    '4H:reserved1 '
    'h:oem_id '
    'h:oem_info '
    '10H:reserved2 '
    'L:pe_offset'
    )

  dos_image = open( 'c:\\windows\\system32\\cmd.exe', 'rb' ).read()
  header = struct_windows_exe_header.unpack( dos_image[0:len(struct_windows_exe_header)] )

  if debug:
    header.dump( print )

  print( 'dos_magic %r' % (header.dos_magic,) )
  print( 'PE header offer: 0x%8.8x' % (header.pe_offset,) )

