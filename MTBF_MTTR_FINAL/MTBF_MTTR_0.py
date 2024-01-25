from pylogix import PLC

com = PLC()

com.IPAddress = '192.168.10.20'


ret = com.Write('SHIFT_LENGTH',21)


print(ret.Value)