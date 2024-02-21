# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 17:19:35 2020
@author: Joshua Perry

An interface library for the WT1600 over ethernet.  

"""
import socket
import time
import re
import sys


FTP_SETUP = ':FILE:DRIVE ND0'
MEM_SETUP = ':STOR:DIR MEM'
SAVE_FTP = ':STATUS:EESR?;:STORE:MEMORY:CONVERT:EXECUTE;:COMMUNICATE:WAIT 64;:STATUS:EESR?'
CLEAR = ':STORE:MEMORY:INIT'
START = ':STOR:START'
STOP = ':STOR:STOP'
SAVE_DIRECTION = STOP + ';' + CLEAR +';:STOR:DIR FILE'
MEM_WORKAROUND = MEM_SETUP + ';' + CLEAR + ';:STOR:DIR FILE' #fix this nonsense


#names = []
names = ['URMS','UMN','UDC','UAC','IRMS','IMN','IDC','IAC','P','S','Q','LAMB','PHI','FU','FI']
'''for i in range(1,7):
    for x in _names:
        names.append(x + '_' + str(i))'''

def query(interface, cmd_str, b_expect=4, buffersize=20480, debug=False):
    #Basic query, returns response as bytes
    framesize = len(cmd_str)
    frame0 = bytes([0x80]) + bytes([0x00]) + bytes([(framesize >> 8) & 0xFF]) + bytes([framesize & 0xFF])
    frame1=   cmd_str.encode('utf-8')
    if debug:print('Trying to send', frame0+frame1)
    interface.send(frame0+frame1)
    b_recv=0
    data = bytes()
    while '\\n' not in str(data) and b_recv < b_expect:
        data += interface.recv (buffersize)
        if len(data) == b_expect and data[3] != 0x00:
            data+=interface.recv(buffersize)
        if debug: print('Received data:', bytearray(data))
        #print(str(data))
        b_recv+=len(data)
        if debug: print('b_rec, len(data)', b_recv, len(data))
    return data    



def init(IP='192.168.128.204', PORT=10001, no_ftp=False):
    USER = 'anonymous'
    PW = ''    
    #print ('Set power meter to record measurement results')
    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.settimeout(5)
    server_address=(IP, PORT)
    try:
        s.connect(server_address)
    except:
        print("Failed to connect to socket")
    retries = 5
    for i in range(retries):
        try:
            resp = query(s, USER)
            if 'username' in str(resp): msg = USER
            elif 'password' in str(resp): msg = PW
            elif 'server is ready' in str(resp): 
                if not no_ftp: 
                    print('Comms up, setting ftp')
                    query(s, FTP_SETUP)
                print('Connection established to WT1600')
                return s 
            resp = query(s, msg)
        except socket.timeout:
            print('Connection timed out, retrying {} of {}'.format(i+1, retries))
            continue
        print('Did not connect, retry {} of {}'.format(i+1, retries))   
    print('WT1600 communication initilization failed')
    s.close()
    sys.exit()

def get_data(interface, element=1):
    '''
    Get a single element's data
    '''
    start_num = (element-1) * 15
    data = ''
    #data = {}
    j = 0
    for i in range(start_num, start_num+15):
        msg = ':NUMERIC:NORMAL:VALUE? {}'.format(i+1)
        resp = query(interface, msg)
        try:
            #data.append(float(resp[4:]))
            #print(str(resp[4:]))
            #print(float(resp[4:]))
            data+=(',' + str(float(resp[4:])))
        except ValueError as e:
            try:
                #print(str(resp[5:]))
                #print(float(resp[5:]))
                data+= (',' + str(float(resp[5:])))
            except ValueError as e:
                print (e, i, resp)
            continue  
    #print(data)      
    return data