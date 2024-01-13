import time
import datetime as dt
import pandas as pd
import logging
import threading
from datetime import datetime
import sys
from queue import Queue
import socket

#Queue for gridsim_thread
gridsim_queue=Queue(maxsize=0)

test='SI001'


##Definition of variables present in the test.
##Presence of instruments
testncycles=1
gridsim_present=1


term = '\n'

def query(msg: bytes, debug = False):
    cmd = bytes((msg+term).encode('utf-8'))
    s.send(cmd)
    if debug: print("trying to send " +str(cmd))
    data = bytes(''.encode('utf-8'))
    data += s.recv(4096)
    if debug: print("received " + str(data.encode('utf-8')))
    return data

#Grid Simulator object
if gridsim_present==1:
    print('Stablishing SCPI connection with grid sim...')
    try:
        s=socket.socket()
        s.connect(('192.168.128.245', 1234))
        data = bytes(''.encode('utf-8'))
        data = query('*IDN?')
        if 'MX45' not in str(data): 
            print('Error while trying to establish SCPI connection')
            sys.exit()
        print("Successfully established connection with MX45")          
    except Exception as e:
        print('Error while trying to establish SCPI connection')
        print(e)
        sys.exit()

vr = 300
freq = 50
volts = 230
slew = 1000
try:
    '''
    if(str(vr) not in str(query('VOLT:RANG?'))): 
        query('VOLT:RANG ' + str(vr))
        print("Successfully changed voltage range")
    print(query('VOLT:RANG?'))
    if('AC' not in str(query('MODE?'))): 
        query('MODE AC')
        print("Succesfully changed mode")
    if(str(freq) not in str(query('FREQ?'))):  
        query('FREQ ' + str(freq))
        print("Succesfully changed Frequency")
    print(query('FREQ?'))
    if(str(slew) not in str(query('VOLT:SLEW:IMMEDIATE?'))):  
        query('VOLT:SLEW ' + str(slew))
        print("Successfully changed voltage slew rate")
    print(query('VOLT:SLEW:IMMEDIATE?'))
'''
    query('OUTP 1')
    #prints output volts
    print(query('MEAS:VOLT:AC?'))
    query('VOLT ' + str(volts))
    query('inst:coup all')
    query('OUTP:IMM 0')
    time.sleep(5)
    #prints current volt value
    print(query('VOLT?'))
    #re-enables local interface
    query('++loc')
except Exception as e:
    print("Error while trying to communicate with MX45")
    print(e)
    s.close()
    sys.exit()

input("Press enter to continue...")
s.close()