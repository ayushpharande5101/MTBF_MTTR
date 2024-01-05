import time
from pymodbus.client import ModbusTcpClient
import datetime
import pyodbc

# Establish a connection to the SQL Server database
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=AYUSHP-DELL\\SQLEXPRESS03;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

if conn:
    print("Connected")
else:
    print("Not Connected")

IP_Address1 = '127.0.0.1'
client = ModbusTcpClient(IP_Address1)
print(client.connect())

# Initial Modbus read
Z = client.read_holding_registers(0, 1)
print(Z.registers[0])

while True:
    # Update the Modbus read inside the loop
    Z = client.read_holding_registers(0, 1)

    if Z.registers[0] == 1:
        a = datetime.time()
        b = None  # Set DownTime to None when the condition is not met
        time.sleep(2)

    elif Z.registers[0] == 0:
        a = None
        b = datetime.time()
        time.sleep(2)

    # Check if the table exists and create it if it doesn't
    table_exists_query = ("IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'MTTR_MTBH') "
                          "CREATE TABLE MTTR_MTBH (UpTime DATETIME, DownTime DATETIME, AverageTime REAL);")

    cursor.execute(table_exists_query)

    # Specify the correct table_name based on your conditions
    table_name = 'master.dbo.MTTR_MTBH'  # Change this based on your logic

    # Insert data into the specified table
    columns = ['UpTime', 'DownTime']
    values = (a, b)
    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?, ?)"
    cursor.execute(SQLCommand, values)

    # Commit the changes to the database
    conn.commit()
