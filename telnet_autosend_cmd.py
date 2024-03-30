'''
Created on July 6, 2023
@author: Brandon Lewien
A quick implementation of querying Edge inverter on a set
timer.

Refer to README.md on how to run
'''
import argparse
import datetime
import telnetlib
import time
import sys
import os


#QPIRI Input voltage range is O which is index 72 of QPIRI return string
#0: Appliance
#1: UPS

#Output source priority is P which is index 74 of QPIRI return string
#0: UtilitySolarBat
#1: SolarUtilityBat
#2: SolarBatUtility


QPIRI_VOLTAGE_RANGE             = 72
QPIRI_OUTPUT_SRC_PRIORITY_RANGE = 74
TELNET_COMMAND                  = "QPIRI"
DELAY_S                         = .5
READ_TIMEOUT_S                  = 3
def get_serial_inverter():
    '''
    Gets the comport from argument
    '''
    parser = argparse.ArgumentParser(
        description="A script that grabs the comport from argument")

    parser.add_argument('-s', '--serial',
                        type=str, required=True, help='The serial specified')
    opts = parser.parse_args()

    return opts.serial

def date_data_print(read_data):
    '''
    Prints date and data to stdout
    '''
    print(str(datetime.datetime.now()) + " " + read_data)
    # print(read_data)

def fetch_voltage_range(read_data):
    '''
    Decodes UPS or APL from QPIRI command and prints
    '''
    try:
        if read_data[QPIRI_VOLTAGE_RANGE] == '1':
            date_data_print("UPS")
        elif read_data[QPIRI_VOLTAGE_RANGE] == '0':
            date_data_print("APL")
        else:
            date_data_print("Error reading")
    except Exception:
        date_data_print("Error reading")

def fetch_output_source_priority(read_data):
    '''
    Decodes SUB, USB, or SBU from QPIRI command and prints
    '''
    try:
        if read_data[QPIRI_OUTPUT_SRC_PRIORITY_RANGE] == '0':
            date_data_print("UtilitySolarBat")
        elif read_data[QPIRI_OUTPUT_SRC_PRIORITY_RANGE] == '1':
            date_data_print("SolarUtilityBat")
        elif read_data[QPIRI_OUTPUT_SRC_PRIORITY_RANGE] == '2':
            date_data_print("SolarBatUtility")
    except Exception:
        date_data_print("Error reading")

class TelnetEdge:
    '''
    Telnet interface to send commands to Edge Inverter
    '''
    def __init__(self):
        self.tn = telnetlib.Telnet("edge-" + get_serial_inverter() + ".local", 23)

    def telnet_write(self, command):
        '''
        Writes commands followed by newline
        '''
        self.tn.write(command.encode() + b'\n')
    def telnet_read(self):
        '''
        Reads returns followed by newline unless timer elapsed
        '''
        tn_read = self.tn.read_until(b'\n', READ_TIMEOUT_S)
        return tn_read.decode()
    def telnet_close(self):
        '''
        Safely closes telnet
        '''
        self.tn.close()



if __name__ == '__main__':
    print("Quit with Ctrl+C\n")
    try:
        telnetInverter = TelnetEdge()
    except Exception:
        print("Telnet cannot open serial number provided")
        try:
            print("Closing script\n")
            sys.exit(0)
        except SystemExit:
            print("Closing script\n")
            os._exit(0)
    while True:
        # Write and read indefinitely until quit
        try:
            telnetInverter.telnet_write('QPIRI')
            telnet_data = telnetInverter.telnet_read()
            #print(telnet_data) # Print all the data
            

            fetch_output_source_priority(telnet_data)
            fetch_voltage_range(telnet_data)
            time.sleep(DELAY_S)
        except KeyboardInterrupt:
            print('Interrupted')
            telnetInverter.telnet_close()
            try:
                print("Closing script\n")
                sys.exit(0)
            except SystemExit:
                print("Closing script\n")
                os._exit(0)
