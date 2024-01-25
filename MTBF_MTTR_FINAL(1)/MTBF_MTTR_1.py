import time
from pymodbus.client import ModbusTcpClient
import pyodbc
import datetime
import sys
import os
from pylogix import PLC
# from datetime import datetime

connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                            'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                            'Trusted_Connection=yes;')

if connection:
    print("Connected Successfully")
else:
    print("Failed to connect")

cursor = connection.cursor()

A1 = [0]  # MTBF
A2 = [0]  # MTTR
A3 = [0]  # UPTIME
A4 = [0]  # DOWNTIME
A5 = [0]  # PRODUCTION_TIME

global G
G = [1]

def none_insert_data(cursor, values):
    table_name = 'MTBF_MTTR.dbo.[DATA_UPDATE]'

    columns = ['SHIFT', 'DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
               'TOTAL_PRODUCTION_TIME', 'TOTAL_PIECES', 'REJECTED_PIECES', 'GOOD_PIECES',
               'IDEAL_RUN_RATE', 'AVAILABILITY', 'PERFORMANCE', 'QUALITY', 'OVERALL_OEE']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor.execute(SQLCommand, values)
    connection.commit()  # Commit changes to the database

values = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
none_insert_data(cursor, values)

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

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
    connection.commit()

def reset_variables():
    global failure_count, uptime_start_time, downtime_start_time, last_insert_time1
    failure_count = 0
    uptime_start_time = None
    downtime_start_time = None
    last_insert_time1 = time.time()

def insert_data(cursor, values):
    table_name = 'MTBF_MTTR.dbo.[DATA_INSERT]'

    columns = ['SHIFT', 'DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
               'TOTAL_PRODUCTION_TIME', 'TOTAL_PIECES', 'REJECTED_PIECES', 'GOOD_PIECES',
               'IDEAL_RUN_RATE', 'AVAILABILITY', 'PERFORMANCE', 'QUALITY', 'OVERALL_OEE']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor.execute(SQLCommand, values)
    connection.commit()  # Commit changes to the database

Z1 = [0]

def main(G):

    failure_count = 0
    cursor = connection.cursor()

    uptime_start_time = None
    downtime_start_time = None
    last_uptime_value = 0
    last_downtime_value = 0

    production_start_time = time.time()
    data_inserted1 = False

    while True:
        with PLC() as comm:
            comm.IPAddress = '192.168.10.20'
            Z1 = comm.Read('MACHINE_AVAILABILITY')
            Z2 = comm.Read('FAILURE_BIT')
            Z3 = comm.Read('SHIFT_LENGTH')
            Z4 = comm.Read('IDEAL_RUN_RATE')
            Z5 = comm.Read('TOTAL_PIECES')
            Z6 = comm.Read('REJECTED_PIECES')
            Z7 = comm.Read('SHORT_BREAK')
            Z8 = comm.Read('MEAL_BREAK')
            Z9 = comm.Read('ACTUAL_DOWNTIME')


            MACHINE_AVAILABILTY = Z1.Value
            FAILURE_BIT = Z2.Value
            SHIFT_LENGTH = Z3.Value
            IDEAL_RUN_RATE = Z4.Value
            TOTAL_PIECES = Z5.Value
            REJECTED_PIECES = Z6.Value
            SHORT_BREAK = Z7.Value
            MEAL_BREAK = Z8.Value
            ACTUAL_DOWNTIME = Z9.Value

            print(SHIFT_LENGTH)
            print(SHORT_BREAK)
            print(MEAL_BREAK)

            end_time = time.time()
            production_time = (end_time - production_start_time) / 60
            print(f"Production Time: {production_time}")
            A5.append(production_time)

            if MACHINE_AVAILABILTY == True:
                if uptime_start_time is None:
                    uptime_start_time = time.time()
                    downtime_start_time = None
                    last_uptime_value = A3[-1]  # Store the last known Uptime value
                uptime = last_uptime_value + (end_time - uptime_start_time) / 60
                print(f"Uptime: {uptime}")
                A3.append(uptime)

                if failure_count == 0:
                    MTBF = 0
                    A1.append(MTBF)
                else:
                    MTBF_1 = production_time / failure_count
                    MTBF = round(MTBF_1,2)
                    A1.append(MTBF)

            elif ACTUAL_DOWNTIME == True:
                if downtime_start_time is None:
                    downtime_start_time = time.time()
                    uptime_start_time = None
                    last_downtime_value = A4[-1]  # Store the last known Downtime value
                downtime = last_downtime_value + (end_time - downtime_start_time) / 60
                print(f"Downtime: {downtime}")
                A4.append(downtime)

            if MACHINE_AVAILABILTY == False:
                print("INTERNAL DOWNTIME")

            elif ACTUAL_DOWNTIME == False:
                print("")

            if FAILURE_BIT == True:
                failure_count += 1
                comm._write_tag('FAILURE_BIT',False)

                if failure_count == 0:
                    MTTR = 0
                    A2.append(MTTR)
                else:
                    MTTR_1 = A4[-1] / failure_count
                    MTTR = round(MTTR_1,2)
                    A2.append(MTTR)

            print(f"FAILURE_COUNT: ", failure_count)

            TOTAL_BREAK_TIME = SHORT_BREAK + MEAL_BREAK

            GOOD_PIECES = TOTAL_PIECES - REJECTED_PIECES

            if A5[-1] == 0:
                AVAILABILITY = 0
            else:
                AVAILABILITY = A3[-1] / A5[-1]

            print(AVAILABILITY)

            if A3[-1] == 0:
                PERFORMANCE = 0
            else:
                if IDEAL_RUN_RATE == 0:
                    PERFORMANCE = 0
                else:
                    PERFORMANCE1 = (TOTAL_PIECES / A3[-1]) / IDEAL_RUN_RATE
                    if PERFORMANCE1 >= 1:
                        PERFORMANCE = 1
                    else:
                        PERFORMANCE = PERFORMANCE1

            if TOTAL_PIECES == 0:
                QUALITY = 0

            else:
                QUALITY = GOOD_PIECES / TOTAL_PIECES

            OVERALL_OEE = (AVAILABILITY * PERFORMANCE * QUALITY) * 100

            IDEAL_RUN_RATE = (Z4.Value)/60
            print(IDEAL_RUN_RATE)

            # iteration += 1
            if production_time >= (SHIFT_LENGTH - TOTAL_BREAK_TIME) and not data_inserted1:
                DATETIME = datetime.datetime.now()
                values = (G[-1], DATETIME, A1[-1], A2[-1], failure_count, A3[-1], A4[-1], A5[-1], TOTAL_PIECES,
                          REJECTED_PIECES,
                          GOOD_PIECES, Z4.Value, AVAILABILITY, PERFORMANCE, QUALITY, OVERALL_OEE)

                insert_data(cursor, values)
                update_data(cursor, values)

                data_inserted1 = True
                if data_inserted1 == True:
                    shift = G[-1] + 1
                    G.append(shift)
                    if shift > 3:
                        G = G[:1]
                    if __name__ == "__main__":
                        main(G)

            time.sleep(1)

if __name__ == "__main__":
    main(G)