#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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

    print(bytearray(cmd))
    s.send(bytearray(cmd))
    time.sleep(0.2)
    s.close()     

def main():
    args = sys.argv[1:]
    if len(args) != 2 or int(args[1]) < 1 or int(args[1]) > 8:
        print("Incorrect args try again: relayScript.py [-c|-o] [1-8]")
        sys.exit()
    if args[0] == '-c': #close relay
        flipper(0xFF,args[1])
    elif args[0] == '-o':   #open relay
        flipper(0x00, args[1])
    elif args[0] == '-f':   #flip relay
        flipper(0x55,args[1])         

if __name__ == "__main__":
    main()

