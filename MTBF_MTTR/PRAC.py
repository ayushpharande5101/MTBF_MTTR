import time
from pymodbus.client import ModbusTcpClient
import pyodbc
import datetime

connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                            'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                            'Trusted_Connection=yes;')

if connection:
    print("Connected Successfully")
else:
    print("Failed to connect")

cursor = connection.cursor()

A = [0]
B = [0]
A1 = [0]  # MTBF
A2 = [0]  # MTTR
A3 = [0]  # failure_count
A4 = [0]  # TOTAL_UPTIME
A5 = [0]  # TOTAL_DOWN
A6 = [0]  # TOTAL_PRODUCTION_TIME

def none_insert_data(cursor, values):

    table_name = 'MTBF_MTTR.dbo.[DATA_UPDATE]'

    columns = ['SHIFT','DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
                   'TOTAL_PRODUCTION_TIME', 'TOTAL_PIECES', 'REJECTED_PIECES','GOOD_PIECES',
                   'IDEAL_RUN_RATE', 'AVAILABILITY', 'PERFORMANCE', 'QUALITY', 'OVERALL_OEE']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor.execute(SQLCommand, values)
    connection.commit()  # Commit changes to the database

DATETIME = datetime.datetime.now()
values = (0, DATETIME, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
none_insert_data(cursor, values)

def update_data(cursor, values):
    sql = """UPDATE MTBF_MTTR.dbo.DATA_UPDATE
             SET 
                SHIFT = ?,
                DATETIME = ?,
                MTBF = ?,
                MTTR = ?,
                TOTAL_FAILURES = ?,
                TOTAL_UPTIME = ?,
                TOTAL_DOWNTIME = ?,
                TOTAL_PRODUCTION_TIME = ?,
                TOTAL_PIECES = ?,
                REJECTED_PIECES = ?,
                GOOD_PIECES = ?,
                IDEAL_RUN_RATE = ?,
                AVAILABILITY = ?,
                PERFORMANCE = ?,
                QUALITY = ?,
                OVERALL_OEE = ?"""

    cursor.execute(sql, values)
    connection.commit()  # Commit changes to the database

def insert_data(cursor, values):
    table_name = 'MTBF_MTTR.dbo.[DATA_INSERT]'

    columns = ['SHIFT','DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
               'TOTAL_PRODUCTION_TIME','TOTAL_PIECES','REJECTED_PIECES','GOOD_PIECES',
               'IDEAL_RUN_RATE','AVAILABILITY','PERFORMANCE','QUALITY','OVERALL_OEE']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor.execute(SQLCommand, values)
    connection.commit()  # Commit changes to the database

def read_modbus_data(client):
    Z = client.read_holding_registers(0, 5)
    return Z.registers[0] == 1, Z.registers[1]

def insert_data1(cursor):
    table_name = 'MTBF_MTTR.dbo.[DATA_INSERT]'
    shift = 1

    while shift <= 3:
        if shift == 3:
            shift = 1
            time.sleep(1)
    columns = ['SHIFT']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?)"

    values = (shift)
    cursor.execute(SQLCommand, values)
    connection.commit()  # Commit changes to the database

def main():
    IP_Address1 = '127.0.0.1'
    client = ModbusTcpClient(IP_Address1)
    print(client.connect())

    failure_count = 0

    cursor = connection.cursor()
    uptime_start_time = None
    downtime_start_time = None

    while True:
        Z = client.read_holding_registers(0, 10)
        if Z.registers[0] == 1:
            production_start_time = time.time()
            shift = 0
            last_insert_time = time.time()
            while True:
                client.read_holding_registers(0, 10)
                end_time = time.time()
                production_time = end_time - production_start_time
                print(f"Production Time: {production_time}")
                A5.append(production_time)

                Z = client.read_holding_registers(0, 10)
                if Z.registers[0] == 1:
                    client.write_registers(1,0)
                    if uptime_start_time is None:
                        uptime_start_time = time.time()
                        downtime_start_time = None
                    uptime = end_time - uptime_start_time
                    print(f"Uptime: {uptime}")
                    A3.append(uptime)

                    if failure_count == 0:
                        MTBF = 0
                        A1.append(MTBF)
                    else:
                        MTBF = production_time/ failure_count
                        A1.append(MTBF)

                elif Z.registers[0] == 0:
                    # client.write_registers(1, 1)
                    if Z.registers[1] == 0:
                        failure_count += 1
                        client.write_registers(1,1)

                    if downtime_start_time is None:
                        downtime_start_time = time.time()
                        uptime_start_time = None
                    downtime = end_time - downtime_start_time
                    print(f"Downtime: {downtime}")
                    A4.append(downtime)

                    if failure_count == 0:
                        MTTR = 0
                        A2.append(MTTR)
                    else:
                        MTTR = downtime / failure_count
                        A2.append(MTTR)

                print(f"FAILURE_COUNT: ",failure_count)

                TOTAL_PIECES = Z.registers[2]  # min
                IDEAL_RUNRATE = Z.registers[3]
                REJECTED_PIECES = Z.registers[4]

                GOOD_PIECES = TOTAL_PIECES - REJECTED_PIECES

                if A5[-1] == 0:
                    AVAILABILITY = 0
                else:
                    AVAILABILITY = A3[-1]/A5[-1]
                if A3[-1] == 0:
                    PERFORMANCE = 0
                else:
                    PERFORMANCE = (TOTAL_PIECES / A3[-1]) / IDEAL_RUNRATE

                QUALITY = GOOD_PIECES / TOTAL_PIECES

                OVERALL_OEE = (AVAILABILITY * PERFORMANCE * QUALITY) * 100
                shift += 1
                if shift>3:
                    shift = 1

                current_time = time.time()
                if current_time - last_insert_time >= 10:# Check if 10 minutes (600 seconds) have passed
                    DATETIME = datetime.datetime.now()
                    values = (shift,DATETIME, A1[-1], A2[-1], failure_count, A3[-1], A4[-1], A5[-1], TOTAL_PIECES, REJECTED_PIECES,
                              GOOD_PIECES,IDEAL_RUNRATE, AVAILABILITY, PERFORMANCE, QUALITY, OVERALL_OEE)
                    insert_data(cursor, values)
                    if insert_data(cursor,values):
                        print("DATA INSERTED")
                    else:
                        print("DATA NOT_INSERTED")

                    update_data(cursor, values)
                    if update_data(cursor, values):
                        print("DATA INSERTED")
                    else:
                        print("DATA NOT_INSERTED")

                    # insert_data1(cursor)
                    # last_insert_time = current_time  # Update the last insertion time
                    # if last_insert_time == current_time:
                    last_insert_time = current_time  # Update the last insertion time
                    if last_insert_time == current_time:

                        if __name__ == "__main__":
                            main()
                        time.sleep(2)
        else:
            print("START THE MACHINE")
            time.sleep(1)

if __name__ == "__main__":
    main()