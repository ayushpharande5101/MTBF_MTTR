import time
from pymodbus.client import ModbusTcpClient
import pyodbc
import datetime
import sys
import os
from pylogix import PLC
# from datetime import datetime

IP_Address1 = '127.0.0.1'
client = ModbusTcpClient(IP_Address1)
print(client.connect())

connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                            'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                            'Trusted_Connection=yes;')

if connection:
    print("Connected Successfully")
else:
    print("Failed to connect")

cursor = connection.cursor()

Z = client.read_holding_registers(0,10)

A1 = [0] #MTBF
A2 = [0] #MTTR
A3 = [0] #UPTIME
A4 = [0] #DOWNTIME
A5 = [0] #PRODUCTION_TIME

def none_insert_data(cursor, values):

    table_name = 'MTBF_MTTR.dbo.[DATA_UPDATE]'

    columns = ['SHIFT','DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
                   'TOTAL_PRODUCTION_TIME', 'TOTAL_PIECES', 'REJECTED_PIECES','GOOD_PIECES',
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
    connection.commit()  # Commit changes to the database


def reset_variables():
    global failure_count, uptime_start_time, downtime_start_time, last_insert_time1
    failure_count = 0
    uptime_start_time = None
    downtime_start_time = None
    last_insert_time1 = time.time()

def insert_data(cursor, values):
    table_name = 'MTBF_MTTR.dbo.[DATA_INSERT]'

    columns = ['SHIFT','DATETIME', 'MTBF', 'MTTR', 'TOTAL_FAILURES', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME',
               'TOTAL_PRODUCTION_TIME','TOTAL_PIECES','REJECTED_PIECES','GOOD_PIECES',
               'IDEAL_RUN_RATE','AVAILABILITY','PERFORMANCE','QUALITY','OVERALL_OEE']

    SQLCommand = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

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
    last_insert_time1 = time.time()


    Z = client.read_holding_registers(0, 100)
    # if Z.registers[0] == 1:
    production_start_time = time.time()
    shift = 0
    last_insert_time = time.time()
    n = 0
    iteration = 0

    data_inserted1 = False

    M = 0
    while True:
        client.read_holding_registers(0, 100)
        end_time = time.time()
        production_time = end_time - production_start_time
        print(f"Production Time: {production_time}")
        A5.append(production_time)

        Z = client.read_holding_registers(0, 100)
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
            if IDEAL_RUNRATE == 0:
                PERFORMANCE = 0
            else:

                PERFORMANCE = (TOTAL_PIECES / A3[-1]) / IDEAL_RUNRATE

        if TOTAL_PIECES == 0:
            QUALITY = 0
        else:
            QUALITY = GOOD_PIECES / TOTAL_PIECES

        OVERALL_OEE = (AVAILABILITY * PERFORMANCE * QUALITY) * 100

        iteration += 1

        # Assuming Current_time_1 is a datetime object
        Current_time_1 = datetime.datetime.now()
        target_time1 = Current_time_1.replace(hour=13, minute=9, second=0, microsecond=0)

        if Current_time_1 >= target_time1 and not data_inserted1:
            DATETIME = datetime.datetime.now()
            values = (1, DATETIME, A1[-1], A2[-1], failure_count, A3[-1], A4[-1], A5[-1], TOTAL_PIECES,
                        REJECTED_PIECES,
                        GOOD_PIECES, IDEAL_RUNRATE, AVAILABILITY, PERFORMANCE, QUALITY, OVERALL_OEE)

            insert_data(cursor, values)
            update_data(cursor, values)

            data_inserted1 = True
        if data_inserted1 == True:
            IP_Address1 = '127.0.0.1'
            client = ModbusTcpClient(IP_Address1)
            print(client.connect())

            failure_count = 0

            cursor = connection.cursor()
            uptime_start_time = None
            downtime_start_time = None
            last_insert_time1 = time.time()

            Z = client.read_holding_registers(0, 10)
            # if Z.registers[0] == 1:
            production_start_time = time.time()
            shift = 0
            last_insert_time = time.time()
            n = 0
            iteration = 0

            data_inserted2 = False

            while True:
                client.read_holding_registers(0, 10)
                end_time = time.time()
                production_time = end_time - production_start_time
                print(f"Production Time: {production_time}")
                A5.append(production_time)

                Z = client.read_holding_registers(0, 10)
                if Z.registers[0] == 1:
                    client.write_registers(1, 0)
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
                        MTBF = production_time / failure_count
                        A1.append(MTBF)

                elif Z.registers[0] == 0:
                    # client.write_registers(1, 1)
                    if Z.registers[1] == 0:
                        failure_count += 1
                        client.write_registers(1, 1)

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

                print(f"FAILURE_COUNT: ", failure_count)

                TOTAL_PIECES = Z.registers[2]  # min
                IDEAL_RUNRATE = Z.registers[3]
                REJECTED_PIECES = Z.registers[4]

                GOOD_PIECES = TOTAL_PIECES - REJECTED_PIECES

                if A5[-1] == 0:
                    AVAILABILITY = 0
                else:
                    AVAILABILITY = A3[-1] / A5[-1]
                if A3[-1] == 0:
                    PERFORMANCE = 0
                else:
                    if IDEAL_RUNRATE == 0:
                        PERFORMANCE = 0
                    else:

                        PERFORMANCE = (TOTAL_PIECES / A3[-1]) / IDEAL_RUNRATE

                if TOTAL_PIECES == 0:
                    QUALITY = 0
                else:
                    QUALITY = GOOD_PIECES / TOTAL_PIECES

                OVERALL_OEE = (AVAILABILITY * PERFORMANCE * QUALITY) * 100

                iteration += 1

                    # Assuming Current_time_1 is a datetime object
                Current_time_2 = datetime.datetime.now()
                target_time2 = Current_time_2.replace(hour=13, minute=10, second=0, microsecond=0)

                if Current_time_2 >= target_time2 and not data_inserted2:
                    DATETIME = datetime.datetime.now()
                    values = (2, DATETIME, A1[-1], A2[-1], failure_count, A3[-1], A4[-1], A5[-1], TOTAL_PIECES,
                              REJECTED_PIECES,
                              GOOD_PIECES, IDEAL_RUNRATE, AVAILABILITY, PERFORMANCE, QUALITY, OVERALL_OEE)

                    insert_data(cursor, values)
                    update_data(cursor, values)

                    data_inserted2 = True
                    if data_inserted2 == True:
                        IP_Address1 = '127.0.0.1'
                        client = ModbusTcpClient(IP_Address1)
                        print(client.connect())

                        failure_count = 0

                        cursor = connection.cursor()
                        uptime_start_time = None
                        downtime_start_time = None
                        last_insert_time1 = time.time()

                        Z = client.read_holding_registers(0, 10)
                        # if Z.registers[0] == 1:
                        production_start_time = time.time()
                        shift = 0
                        last_insert_time = time.time()
                        n = 0
                        iteration = 0

                        data_inserted3 = False

                        while True:
                            client.read_holding_registers(0, 10)
                            end_time = time.time()
                            production_time = end_time - production_start_time
                            print(f"Production Time: {production_time}")
                            A5.append(production_time)

                            Z = client.read_holding_registers(0, 10)
                            if Z.registers[0] == 1:
                                client.write_registers(1, 0)
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
                                    MTBF = production_time / failure_count
                                    A1.append(MTBF)

                            elif Z.registers[0] == 0:
                                # client.write_registers(1, 1)
                                if Z.registers[1] == 0:
                                    failure_count += 1
                                    client.write_registers(1, 1)

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

                            print(f"FAILURE_COUNT: ", failure_count)

                            TOTAL_PIECES = Z.registers[2]  # min
                            IDEAL_RUNRATE = Z.registers[3]
                            REJECTED_PIECES = Z.registers[4]

                            GOOD_PIECES = TOTAL_PIECES - REJECTED_PIECES

                            if A5[-1] == 0:
                                AVAILABILITY = 0
                            else:
                                AVAILABILITY = A3[-1] / A5[-1]
                            if A3[-1] == 0:
                                PERFORMANCE = 0
                            else:
                                if IDEAL_RUNRATE == 0:
                                    PERFORMANCE = 0
                                else:

                                    PERFORMANCE = (TOTAL_PIECES / A3[-1]) / IDEAL_RUNRATE

                            if TOTAL_PIECES == 0:
                                QUALITY = 0
                            else:
                                QUALITY = GOOD_PIECES / TOTAL_PIECES

                            OVERALL_OEE = (AVAILABILITY * PERFORMANCE * QUALITY) * 100

                                # Assuming Current_time_1 is a datetime object
                            Current_time_3 = datetime.datetime.now()
                            target_time3 = Current_time_3.replace(hour=13, minute=11, second=0, microsecond=0)

                            if Current_time_3 >= target_time3 and not data_inserted3:
                                DATETIME = datetime.datetime.now()
                                values = (
                                3, DATETIME, A1[-1], A2[-1], failure_count, A3[-1], A4[-1], A5[-1], TOTAL_PIECES,
                                REJECTED_PIECES,
                                GOOD_PIECES, IDEAL_RUNRATE, AVAILABILITY, PERFORMANCE, QUALITY, OVERALL_OEE)

                                insert_data(cursor, values)
                                update_data(cursor, values)

                                data_inserted3 = True
                                if data_inserted3 == True:
                                    time.sleep(60)
                                    if __name__ == "__main__":
                                        main()

        time.sleep(1)

if __name__ == "__main__":
    main()
