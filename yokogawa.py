import msvcrt
import time
from datetime import datetime as dt
import sys
import wt1600 as yoko

_names = ['URMS','UMN','UDC','UAC','IRMS','IMN','IDC','IAC','P','S','Q','LAMB','PHI','FU','FI']


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


# Open a text file in append and read mode
with open("Yokogawa_" + str(dt.now().strftime("%Y%m%d.%H%M%S")) + ".txt", "a+") as f:
    while True:
        for j in range(1,7):
            data = []
            data = str( dt.now())
            data+=(str(yoko.get_data(s,j)) + "\n")
            # Write to the end of the file
            f.writelines(data)
        #takes roughly .6secs to query and write all 6 elements
        #sleeping .4secs to create 1 sec interval between query of the same element
        time.sleep(.4)
        if msvcrt.kbhit():
            if msvcrt.getwche() == '\r':
                break


input("Press Enter to continue...")
print("Closing socket interface to Yokogawa...")
s.close()
time.sleep(5)


