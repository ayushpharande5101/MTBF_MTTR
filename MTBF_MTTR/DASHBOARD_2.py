import time

def shift():

    shift = 1
    while True:
        if shift > 3:
            shift = 1
        print(shift)
        time.sleep(2)
        shift += 1

shift()