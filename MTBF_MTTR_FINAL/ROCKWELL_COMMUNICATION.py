"""
Read a list of tags at once

Reading lists and arrays is much more efficient than
reading them individually. You can create a list of tags
and pass it to .Read() to read them  all in one packet.
The values returned will be in the same order as the tags
you passed to Read()

NOTE:  Packets have a ~500 byte limit, so you have to be cautions
about not exceeding that or the read will fail.  It's a little
difficult to predict how many bytes your reads will take up because
the packet will depend on the length of the tag name and the
reply will depend on the data type.  Strings are a lot longer than
DINT's for example.

I'll usually read no more than 5 strings at once, or 10 DINTs
"""
from pylogix import PLC

with PLC() as comm:
    comm.IPAddress = '192.168.10.20'
    # ret = comm.Read('shift')
    ret = comm.Write('shift', 20)

    A = ret.Value
    A1 = bool(A)
    print(A)
    print(A1)