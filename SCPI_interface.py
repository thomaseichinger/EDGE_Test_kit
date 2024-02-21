import sys
import datetime as dt
import socket

term = '\n'

class SCPI_interface:
    def __init__(self, ip, port: int, idn):
        self.ip = ip
        self.port = port
        self.idn = idn
        self.s = socket.socket()
    
    def query(self, msg: bytes, debug = False):
        cmd = bytes((msg+term).encode('utf-8'))
        self.s.send(cmd)
        if debug: print("trying to send " +str(cmd))
        data = bytes(''.encode('utf-8'))
        data += self.s.recv(4096)
        if debug: print("received " + str(data.encode('utf-8')))
        return data
    
    def connect(self):
        try:
            self.s.connect((self.ip, self.port))
            data = bytes(''.encode('utf-8'))
            data = self.query('*IDN?')
            if self.idn not in str(data): 
                print('Error while trying to establish SCPI connection')
                sys.exit()
            print("Successfully established connection with " + self.idn + ' ' + self.ip + ':' + str(self.port))         
        except Exception as e:
            print('Error while trying to establish SCPI connection with ' + self.idn + ' ' + self.ip + ':' + str(self.port))
            print(e)
            sys.exit()

'''
def main():
    instrument=SCPI_interface('192.168.128.243', 30000, 'ITECH')
    instrument.connect()
    print(instrument.query('FETCH:CURRENT?'))
    print(instrument.query('FETCH:VOLTAGE?'))

if __name__ == "__main__":
    main()
'''  
