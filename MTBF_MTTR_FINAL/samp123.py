from pylogix import PLC

comm = PLC()

comm.IPAddress = '192.168.10.20'


TagValue0 = comm.Read('FAILURE_BIT')
# TagValue1 = comm.Read('Tag02')
# TagValue2 = comm.Read('Tag03')
##
print("Tag00:", TagValue0)

TagValue0 = comm.Write('FAILURE_BIT',False)
# print("Tag02:", TagValue1)
# print("Tag03:", TagValue2