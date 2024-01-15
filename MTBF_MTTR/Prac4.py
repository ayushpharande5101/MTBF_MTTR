import datetime

now = datetime.datetime.now()

hour = now.strftime("%I")
minute = now.strftime("%M")

print(f"The hour is {hour} and the minute is {minute}")