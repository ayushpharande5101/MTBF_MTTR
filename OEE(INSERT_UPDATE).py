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

    columns = ['DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
                   'TOTAL_PRODUCTION_TIME', 'TOTAL_PIECES', 'REJECTED_PIECES',
                   'IDEAL_RUN_RATE', 'AVAILABILITY', 'PERFORMANCE', 'QUALITY', 'OVERALL_OEE']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor.execute(SQLCommand, values)
    connection.commit()  # Commit changes to the database

DATETIME = datetime.datetime.now()
values = (DATETIME, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0)
none_insert_data(cursor, values)
def update_data(cursor, values):
    sql = """UPDATE MTBF_MTTR.dbo.DATA_UPDATE
             SET 
                DATETIME = ?,
                MTBF = ?,
                MTTR = ?,
                TOTAL_FAILURES = ?,
                TOTAL_UPTIME = ?,
                TOTAL_DOWNTIME = ?,
                TOTAL_PRODUCTION_TIME = ?,
                TOTAL_PIECES = ?,
                REJECTED_PIECES = ?,
                IDEAL_RUN_RATE = ?,
                AVAILABILITY = ?,
                PERFORMANCE = ?,
                QUALITY = ?,
                OVERALL_OEE = ?"""

    cursor.execute(sql, values)
    connection.commit()  # Commit changes to the database

def insert_data(cursor, values):
    table_name = 'MTBF_MTTR.dbo.[DATA_INSERT]'

    columns = ['DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
               'TOTAL_PRODUCTION_TIME','TOTAL_PIECES','REJECTED_PIECES',
               'IDEAL_RUN_RATE','AVAILABILITY','PERFORMANCE','QUALITY','OVERALL_OEE']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor.execute(SQLCommand, values)
    connection.commit()  # Commit changes to the database

def read_modbus_data(client):
    Z = client.read_holding_registers(0, 5)
    return Z.registers[0] == 1, Z.registers[1]

def main():
    IP_Address1 = '127.0.0.1'
    client = ModbusTcpClient(IP_Address1)
    print(client.connect())

    START_TIME = 1
    START_TIME1 = 0
    n = 1
    failure_count = 0  # Counter for failures

      # Variable to store the last insertion time
    while True:
        Z = client.read_holding_registers(0, 5)
        if Z.registers[0] == 1:
            last_insert_time = time.time()
            while True:
                connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                            'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                                            'Trusted_Connection=yes;')

                TOTAL_PRODUCTION_TIME = n
                n = n + 1
                print(f"TOTAL_PRODUCTION_TIME == ", TOTAL_PRODUCTION_TIME)
                A6.append(TOTAL_PRODUCTION_TIME)
                Z = client.read_holding_registers(0, 5)

                if Z.registers[0] == 1:
                    client.write_registers(1, 0)
                    CURRENT_TIME = START_TIME
                    START_TIME += 1
                    A.append(CURRENT_TIME)

                    if len(A) >= 1:
                        x = len(A) - 1
                        TOTAL_UPTIME = A[x] - 0
                        print(f"TOTAL_UPTIME == {TOTAL_UPTIME} SEC")
                        A4.append(TOTAL_UPTIME)

                elif Z.registers[0] == 0:
                    if Z.registers[1] == 0:
                        client.write_registers(1, 1)
                        print(f"FAILURE COUNT: ", failure_count)
                        failure_count += 1
                        A3.append(failure_count)

                    CURRENT_TIME = START_TIME1 + 1
                    START_TIME1 += 1
                    B.append(CURRENT_TIME)

                    if len(B) >= 1:
                        y = len(B) - 1
                        TOTAL_DOWN = B[y] - 0
                        print(f"TOTAL_DOWNTIME == {TOTAL_DOWN} SEC")
                        A5.append(TOTAL_DOWN)

                        MTTR = TOTAL_DOWN / failure_count
                        A2.append(MTTR)
                        print(f'MTTR :', MTTR)
                    else:
                        continue
                time.sleep(1)

                if failure_count == 0:
                    MTBF = 0
                    A1.append(MTBF)
                else:
                    MTBF = TOTAL_PRODUCTION_TIME / failure_count
                    print(f'MTBF :', MTBF)
                    print(failure_count)
                    A1.append(MTBF)

                TOTAL_PIECES = Z.registers[2]  # min
                IDEAL_RUNRATE = Z.registers[3]
                REJECTED_PIECES = Z.registers[4]

                GOOD_PIECES = TOTAL_PIECES - REJECTED_PIECES

                AVAILABILITY = A4[-1] / A6[-1]
                PERFORMANCE = (TOTAL_PIECES / A4[-1]) / IDEAL_RUNRATE
                QUALITY = GOOD_PIECES / TOTAL_PIECES

                OVERALL_OEE = (AVAILABILITY * PERFORMANCE * QUALITY) * 100

                print(OVERALL_OEE)

                current_time = time.time()
                if current_time - last_insert_time >= 5:  # Check if 10 minutes (600 seconds) have passed
                    DATETIME = datetime.datetime.now()
                    values = (DATETIME, A1[-1], A2[-1], A3[-1], A4[-1], A5[-1], A6[-1],TOTAL_PIECES,REJECTED_PIECES,IDEAL_RUNRATE,
                              AVAILABILITY,PERFORMANCE,QUALITY,OVERALL_OEE)
                    insert_data(cursor, values)
                    update_data(cursor, values)
                    last_insert_time = current_time  # Update the last insertion time
                    if last_insert_time == current_time:
                        if __name__ == "__main__":
                            main()

        else:
            print("START THE MACHINE")
            time.sleep(1)

if __name__ == "__main__":
    main()