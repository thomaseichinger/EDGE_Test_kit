import sys
import socket
from datetime import datetime as dt
import os
import sys
if sys.platform == 'win32':
    import msvcrt

term = '\n'

class SCPI_interface:
    def __init__(self, ip, port: int, idn):
        self.ip = ip
        self.port = port
        self.idn = idn
        self.s = socket.socket()
    
    def query(self, msg: str, response = True):
        cmd = bytes((msg+term).encode('utf-8'))
        self.s.send(cmd)
        data = bytes()
        if response == False:
            return 'Empty String'
        data += self.s.recv(1024)
        return str(data)
    
    def connect(self):
        try:
            self.s.connect((self.ip, self.port))
            data = bytes(''.encode('utf-8'))
            data = self.query('*IDN?', True)
            if self.idn not in str(data): 
                print('Error while trying to establish SCPI connection')
                sys.exit()
            print("Successfully established connection with " + self.idn + ' ' + self.ip + ':' + str(self.port))         
        except Exception as e:
            print('Error while trying to establish SCPI connection with ' + self.idn + ' ' + self.ip + ':' + str(self.port))
            print(e)
            sys.exit()

    def close(self):
        try:
            self.s.close()
        except Exception as e:
            print('Error while trying to close SCPI connection with ' + self.idn + ' ' + self.ip + ':' + str(self.port))
            print(e)
            sys.exit()
        


def main():
    instrument=SCPI_interface('192.168.128.191', 30000, 'ITECH')
    instrument.connect()
    instrument.log()
    '''
    print("Source:FUNCTION:mode?: " + instrument.query('Source:FUNCTION:mode?'))
    print("*CLS: " + instrument.query('*CLS', False))
    print("Source:FUNCTION:Mode Fixed: " + instrument.query('Source:FUNCTION:Mode Fixed', False))
    print("Voltage?: " + instrument.query('Voltage?'))
    print("Voltage 350: " + instrument.query('Voltage 350', False))
    print("Voltage?: " + instrument.query('Voltage?'))
    print("Current?: " + instrument.query('Current?'))
    print("Current 15: " + instrument.query('Current 15', False))
    print("Current?: " + instrument.query('Current?'))
    print("FETCH:CURRENT?: " + instrument.query('FETCH:CURRENT?'))
    print("FETCH:VOLTAGE?: " + instrument.query('FETCH:VOLTAGE?'))
    print("Output:State?: " + instrument.query('Output:State?'))
    print("Output:State 1: " + instrument.query('Output:State 1', False))
    print("Output:State?: " + instrument.query('Output:State?'))
    print("Output:State 0: " + instrument.query('Output:State 0', False))
    print("Output:State?: " + instrument.query('Output:State?'))
    '''
    instrument.close()

if __name__ == "__main__":
    main()
 
