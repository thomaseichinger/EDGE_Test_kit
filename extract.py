import time

with open("Yokogawa_20240214.153317 - Sheet1.csv") as inp:
    data = inp.read().splitlines()
    i=0
    while i < len(data):
        for j in range(1,7):
            with open('ch'+str(j)+ ".csv", "a+") as f:
                f.write(str(data[(i)] + '\n'))
                i+=1
