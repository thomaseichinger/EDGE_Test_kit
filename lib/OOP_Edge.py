import serial
import time

class edge_unit:
    def __init__(self,COMPORT):
        self.comport='COM'+str(COMPORT)
        self.bus=None
        self.inquiry_cmd=['QPI','QID','QSID','QVFW','QVFW3','QPIRI','QFLAG','QPIGS','QPIGS2','QPGSn','QMOD','QPIWS','QID','QMCHGCR','QMUCHGCR','QMDCHGCR','QOPPT','QCHPT','QT','QBEQI','QMN','QGMN']
        self.inquiry_cmd_crc=['QET','QEYyyyy','QEMyyyymm','QEDyyyymmdd','QLT','QLYyyyy','QLMyyyymm','QLDyyyymmdd','PBMS','QBMS','QDOP','QULC','QULT','QWDT','QTVR']

        self.create_connection()

    def bytes(self,num):
        return hex(num >> 8), hex(num & 0xFF)

    def create_connection(self):
        self.bus = serial.Serial(self.comport, timeout=1,baudrate=9600)

    def writer(self,cmd):
        crc=str(self.crc_calc(cmd))
        self.bus.write(str.encode(cmd+"\n \r"))
        time.sleep(0.1)

    def reader(self):
        # Read input until received \r unless timeout
        read_data = self.bus.read_until(b'\r')
        # Then print received
        #print(f"{read_data}\n")
        return f"{read_data}"
        # Flush the buffer to rinse and repeat
        self.bus.flush()
    
    def query(self,cmd):
        try:
            self.bus.flushInput()
            self.writer(cmd)
            time.sleep(0.1)
            output=self.reader()
            #print(output)
            return output
        except Exception as e:
            print(e)
            return ''
    def crc_calc(self,message):
        '''
        CRC-16-CITT poly, the CRC scheme used by xmodem protocol
        Poly    Init    RefIn   RefOut  XorOut
        ------  ------  -----   ------  ------
        0x1021  0x0000  false   false   0x0000
        Taken from:
            http://www.ross.net/crc/download/crc_v3.txt
        Checked with:
            https://crccalc.com/
            and Voltronic's supplied function
        '''

        poly = 0x1021
        #16bit operation register, initialized to zeros
        reg = 0x0000
        #pad the end of the message with the size of the poly
        message += '\x00\x00'
        #for each bit in the message
        for byte in message:
            mask = 0x80
            while mask > 0:
                #left shift by one
                reg<<=1
                #input the next bit from the message into the right hand side of the op reg
                if ord(byte) & mask:
                    reg += 1
                mask>>=1
                #if a one popped out the left of the reg, xor reg w/poly
                if reg > 0xffff:
                    #eliminate any one that popped out the left
                    reg &= 0xffff
                    #xor with the poly, this is the remainder
                    reg ^= poly

        return reg

##
###We create the unit
##eu=edge_unit(3)
##print('QDI')
##eu.query('QDI')
##
##print('QMCHGCR')
##eu.query('QMCHGCR')
##
##print('QMUCHGCR')
##eu.query('QMUCHGCR')
##
##print('QMDCHGCR')
##eu.query('QMDCHGCR')
##
##
##for i in range(80):
##    print("")
##    print("-----------------------------")
##    print('Command sent:','MUCHGC0'+"{:02d}".format(i))
##    eu.query('MUCHGC0'+"{:02d}".format(i))
##    time.sleep(0.3)
##    print('QDI')
##    eu.query('QDI')
##    time.sleep(0.3)
##    print('QPIGS')
##    eu.query('QPIGS')
##    time.sleep(0.3)
##    print("-----------------------------")
##    print("")
##for i in range(80):
##    print("")
##    print("-----------------------------")
##    print('Command sent:','MNCHGC0'+"{:03d}".format(i))
##    eu.query('MNCHGC0'+"{:03d}".format(i))
##    time.sleep(0.3)
##    print('QDI')
##    eu.query('QDI')
##    time.sleep(0.3)
##    print('QPIGS')
##    eu.query('QPIGS')
##    time.sleep(0.3)
##    print("-----------------------------")
##    print("")
##
###INQUIRY TESTING SECTION
###INQUIRY TESTING SECTION
###INQUIRY TESTING SECTION
##inquiry_cmd=['QPI','QID','QSID','QVFW','QVFW3','QPIRI','QFLAG','QPIGS','QPIGS2','QPGSn','QMOD','QPIWS','QID','QMCHGCR','QMUCHGCR','QMDCHGCR','QOPPT','QCHPT','QT','QBEQI','QMN','QGMN']
##inquiry_cmd_crc=['QET','QEYyyyy','QEMyyyymm','QEDyyyymmdd','QLT','QLYyyyy','QLMyyyymm','QLDyyyymmdd','PBMS','QBMS','QDOP','QULC','QULT','QWDT','QTVR']
##inquiry=inquiry_cmd+inquiry_cmd_crc
##inq_dic={}
##print(inquiry)
##print("")
####
###We query the unit ID and QPI
##for cmd in inquiry:
##    print(cmd,str.encode(cmd+"\n \r"))
##    if 'yyyymmdd' in cmd:
##        print('CMD required yyyymmdd')
##        inq_dic.update({cmd[:-8]+'20220118':eu.query(cmd[:-8]+'20220118')})
##    elif 'yyyymm' in cmd:
##        print('CMD required yyyymm')
##        inq_dic.update({cmd[:-6]+'202201':eu.query(cmd[:-6]+'202201')})
##    elif 'yyyy' in cmd:
##        print('CMD required yyyy')
##        inq_dic.update({cmd[:-4]+'2022':eu.query(cmd[:-4]+'2022')})
##    else:
##        inq_dic.update({cmd:eu.query(cmd)})
##
##print(inq_dic)
##
###To export any df.
##import pandas as pd
##keys=inq_dic.keys()
##values=[inq_dic[x] for x in keys]
##keys=[x for x in keys]
##enc_cmd=[str.encode(x) for x in keys]
##dec_val=[str(str(x).split("\\")[0][3:]) for x in values]
##dfdic={'cmd':keys,'enc_cmd':enc_cmd,'val':values,'dec_val':dec_val}
##df=pd.DataFrame.from_dict(dfdic)
##df.to_csv('./Voltronics_Protocol_Inquiry_CMDs.csv')



#SETTINGS COMMAND TESTING SECTION
#SETTINGS COMMAND TESTING SECTION
#SETTINGS COMMAND TESTING SECTION


