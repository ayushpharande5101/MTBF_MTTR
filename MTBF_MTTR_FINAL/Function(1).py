import time
from pymodbus.client import ModbusTcpClient
import pyodbc
import datetime
import sys
import os

# def function1():
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

data_inserted = False

while True:
    client.read_holding_registers(0, 100)
    end_time = time.time()
    production_time = end_time - production_start_time
    print(f"Production Time: {production_time}")
    A5.append(production_time)

    Z = client.read_holding_registers(0, 100)
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
    shift += 1
    iteration += 1

    if shift > 3:
        shift = 1

    # Assuming Current_time_1 is a datetime object
    Current_time_1 = datetime.datetime.now()
    target_time = Current_time_1.replace(hour=10, minute=44, second=0, microsecond=0)

    if Current_time_1 >= target_time and not data_inserted:
        DATETIME = datetime.datetime.now()
        values = (1, DATETIME, A1[-1], A2[-1], failure_count, A3[-1], A4[-1], A5[-1], TOTAL_PIECES,
                  REJECTED_PIECES,
                  GOOD_PIECES, IDEAL_RUNRATE, AVAILABILITY, PERFORMANCE, QUALITY, OVERALL_OEE)

        insert_data(cursor, values)
        update_data(cursor, values)

        data_inserted1 = True