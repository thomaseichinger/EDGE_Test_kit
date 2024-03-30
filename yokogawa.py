import msvcrt
import time
from datetime import datetime as dt
import sys
import wt1600 as yoko
import os

term = '\n'
chunksize = 20480

# Access the command-line argument
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("No filename provided")
    sys.exit()

for i in range(0,5):
    try:
        s = yoko.init('192.168.128.204')
        break
    except:
        print("Failed to inialize using socket with FTP")
        try:
            s = yoko.init('192.168.128.204', True)
            break
        except:
            print("Failed to inialize using socket with no_FTP")
    i+=1
if(i==4):
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

folderName= 'Yokogawa_' + filename + str(dt.now().strftime("DATE_%Y_%m_%d.TIME_%H_%M_%S"))
if not os.path.exists('./'+folderName):
    os.mkdir('./'+folderName)
for j in range(1,7):
    # Open a text file in append and read mode
    with open('./'+folderName +'/ch'+str(j)+ ".csv", "a+") as f:
        f.write("Timestamp,URMS,UMN,UDC,UAC,IRMS,IMN,IDC,IAC,P,S,Q,LAMB,PHI,FU,FI")
#sys.stdout.readline("Successfully connected to Yokogawa")

print("Successfully connected to Yokogawa", flush=True)
#sys.fflush(sys.stdout)

while True:
    for j in range(1,7):
        # Open a text file in append and read mode
        with open('./'+folderName +'/ch'+str(j)+ ".csv", "a+") as f:
            # The ISO 8601 format is "YYYY-MM-DDTHH:MM:SS"
            f.write("\n" + dt.now().strftime("%Y-%m-%dT%H:%M:%S"))
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