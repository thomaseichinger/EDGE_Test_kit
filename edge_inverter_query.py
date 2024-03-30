import argparse
import datetime
import telnetlib
import time
import sys
import os

# Hardcoded list of serial numbers for the inverters
SERIAL_NUMBERS = ['4000100104', '4000100323', '4000100247', '4000100142']

QPIRI_VOLTAGE_RANGE = 72
QPIRI_OUTPUT_SRC_PRIORITY_RANGE = 74
#TELNET_COMMAND = "QPIRI"
DELAY_S = .5
READ_TIMEOUT_S = 3

def date_data_print(read_data):
    '''
    Prints date and data to stdout
    '''
    print(str(datetime.datetime.now()) + " " + read_data)

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
    def __init__(self, serial):
        self.tn = telnetlib.Telnet(f"edge-{serial}.local", 23)

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

    for serial in SERIAL_NUMBERS:
        try:
            print(f"Connecting to inverter with serial: {serial}")
            telnetInverter = TelnetEdge(serial)
            telnetInverter.telnet_write("PGR01")
            telnet_data = telnetInverter.telnet_read()
            print("Response after setting voltage command")
            print(telnet_data)
            telnetInverter.telnet_write("QPIRI")
            telnet_data = telnetInverter.telnet_read()
            print("Response after setting voltage command inquiry")
            print(telnet_data)
            fetch_voltage_range(telnet_data)

            #fetch_output_source_priority(telnet_data)
        except Exception as e:
            print(f"Failed to connect to inverter with serial {serial}: {e}")
        finally:
            telnetInverter.telnet_close()
            print(f"Closing connection to inverter with serial: {serial}\n")
        # Delay between connections to different inverters, if needed
        time.sleep(DELAY_S)
