#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Run the program with 'python.exe relayScript.py -[1|0] [1-8]'
-1 == closed (ON)
-0 == open (OFF)
1-8 == relay input numbers

Zola SF Lab Relay
1 == MX45/Grid_Sim
2 == N/A
3 == Aux Load
4 == N/A
5 == N/A
6 == N/A
7 == N/A
8 == N/A
'''


import socket
import time
import sys

def flipper(command:int, relayNum:int):
    s = socket.socket()         # create socket 
    host = '192.168.128.200'        # set ip
    port = 502                 # Set port
    #     |   PADDING   |
    #     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] 
    cmd = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 

    cmd[5] = 0x06
    cmd[6] = 0x01
    cmd[7] = 0x05
    s.connect((host, port))     # connect serve
    cmd[8] = 0
    cmd[9] = (int(relayNum)-1)  # this value for relay address
    cmd[10] = int(command)  # this value to command relay
    cmd[11]= 0 

    buffersize=255
    print(bytearray(cmd))
    s.send(bytearray(cmd))
    data = bytes(''.encode('utf-8'))
    data += s.recv(buffersize)
    print("data: ")
    print(data)
    time.sleep(0.2)
    s.close()     

def main():
    args = sys.argv[1:]
    if (len(args) != 2 or int(args[1]) < 1 or int(args[1]) > 8) and args[0] != '-gridflip':
        print("Incorrect args try again: relayScript.py [-1|-0] [1-8]")
        sys.exit()
    if args[0] == '-1': #close relay
        flipper(0xFF,args[1])
    elif args[0] == '-0':   #open relay
        flipper(0x00, args[1])
    elif args[0] == '-f':   #flip relay
        flipper(0x55,args[1])
    elif args[0] == '-gridflip':
        for i in range(0,200):
            flipper(0x55, 1)
            time.sleep(5)

if __name__ == "__main__":
    main()