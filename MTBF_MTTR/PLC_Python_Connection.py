import time

from pymodbus.client import ModbusTcpClient
import datetime
import pyodbc

def connection():
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                          'Database = TAPR102_1;'
                          'Trusted_Connection=yes;')

    return conn

if connection():
    print("Connected")
else:
    print("Not Connected")

IP_Address1 = '192.0.0.1'
client = ModbusTcpClient(IP_Address1)
print(client.connect())

Z = client.read_holding_registers(0,1)
print(Z.registers[0])

A = datetime.datetime.now()

while True:
    if Z.registers[0] == 1:
        print(A)
        time.sleep(2)

    elif Z.registers[0] == 0:
        print(A)
        time.sleep(2)
