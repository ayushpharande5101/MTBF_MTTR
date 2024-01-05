import pyodbc
import datetime

try:
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                                'Trusted_Connection=yes;')
    cursor = conn.cursor()

    # Ensure that 'ID' is the correct column name in your table
    # Ensure that 'ID' is the correct column name in your table
    # Ensure that 'ID' is the correct column name in your table
    # Ensure that 'ID' is the correct column name in your table
    sql = """UPDATE MTBF_MTTR.dbo.Table_3
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

    A = datetime.datetime.now()
    params = (A, 11, 313, 316, 144, 1155, 9119,1130,9811,1100,112,113,145,617)
    cursor.execute(sql, params)
    conn.commit()

    print("1 row updated successfully")

except (Exception, pyodbc.DatabaseError) as error:
    print(error)

finally:
    if conn:
        cursor.close()
        conn.close()
#
# finally:
#     if connection:
#         cursor.close()
#         connection.close()