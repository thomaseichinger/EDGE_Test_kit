#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import socket
import time
 
s = socket.socket()         # create socket 
host = '192.168.128.200'        # set ip
port = 502                 # Set port
#     |   PADDING   |
#     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] 
cmd = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

'''
01	Read relay status
03	Read the address and version
05	Write a single relay
06	Set baud rate and address
0F	Write all relays

ch1 == grid
ch2 == gen
ch3 == load

cmd[5] = 0x06  #Byte length
cmd[6] = 0x01  #Device address
cmd[7] = 0x05  #command
cmd[8] = 0     #relay address
cmd[9] = 1     #0x[8][9]
cmd[10]= 0xFF    #0xFF00 == relay on
cmd[11]= 00    #0x0000 == relay off
               #0x5500 == relay flip
'''
cmd[5] = 0x06
cmd[6] = 0x01
cmd[7] = 0x05
s.connect((host, port))     # connect serve
cmd[8] = 0
cmd[9] = 0  #change this value for relay address
cmd[10] = 0x55  #change this value to command relay
cmd[11]= 0 

print(bytearray(cmd))
req = (s.send(bytearray(cmd)))
print(req)
print(s.recv_into)
rec = (s.recv_into(bytearray(cmd)))

print(bytearray(cmd))
print(rec)
time.sleep(0.2)
s.close()                   # Close the connection