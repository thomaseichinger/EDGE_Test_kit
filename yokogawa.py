import msvcrt
import time
from datetime import datetime as dt
import sys
import wt1600 as yoko
import os


term = '\n'
chunksize = 20480
try:
    s = yoko.init('192.168.128.204')
except:
    print("Failed to inialize using socket with FTP")
    try:
        s = yoko.init('192.168.128.204', True)
    except:
        print("Failed to inialize using socket with no_FTP")
        sys.exit()

try:
    yoko.query(s, ('*RST"' + term))
    yoko.query(s, (':RATE 500MS' + term))
    yoko.query(s, (':NUMERIC:FORMAT ASCII;NORMAL:PRESET 2;NUMBER 255'))
    yoko.query(s, (':COMMunicate:HEADer OFF' + term))
    yoko.query(s, (':STATUS:FILTER1 FALL' + term ))
    yoko.query(s, (':STATUS:EESR?' + term), 4, chunksize)
    #clear the response queue
    s.recv(chunksize)
except Exception as e:
    print("Error while trying to communicate with Yokogawa")
    print(e)
    s.close()
    sys.exit()

filename= 'Yokogawa_' + str(dt.now().strftime("%Y%m%d.%H%M%S"))
if not os.path.exists('./'+filename):
    os.mkdir('./'+filename)
for j in range(1,7):
    # Open a text file in append and read mode
    with open('./'+filename +'/ch'+str(j)+ ".csv", "a+") as f:
        f.write("Timestamp,URMS,UMN,UDC,UAC,IRMS,IMN,IDC,IAC,P,S,Q,LAMB,PHI,FU,FI")

print("Press Enter to end program...")
while True:
    for j in range(1,7):
        # Open a text file in append and read mode
        with open('./'+filename +'/ch'+str(j)+ ".csv", "a+") as f:
            f.write("\n"+str(dt.now().strftime("%Y%m%d.%H%M%S")))
            f.write(str(yoko.get_data(s,j)))
            #print(data)
            # Write to the end of the file
            #f.write(str(data))
    #takes roughly .6secs to query and write all 6 elements
    #sleeping .4secs to create 1 sec interval between query of the same element
    time.sleep(.4)
    if msvcrt.kbhit():
        if msvcrt.getwche() == '\r':
            break


print("Closing socket interface to Yokogawa...")
s.close()
time.sleep(5)


