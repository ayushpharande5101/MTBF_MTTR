
TOTAL_PRODUCTION_TIME = 60
TOTAL_NUMBER_OF_FAILURES = 4
TOTAL_AMOUNT_OF_DOWNTIME = 3

MTBF = TOTAL_PRODUCTION_TIME/TOTAL_NUMBER_OF_FAILURES
print(f'MTBF :', MTBF)

MTTR = TOTAL_AMOUNT_OF_DOWNTIME/TOTAL_NUMBER_OF_FAILURES
print(f'MTTR :', MTTR)

