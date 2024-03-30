import urllib3
import json
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import telnetlib
import time

# Global setup
http = urllib3.PoolManager()
SERIAL_NUMBERS = ['4000100104', '4000100323', '4000100247', '4000100142']
ITERATIONS = 1
UPS = "PGR01"
APPLIANCE = "PGR00"


def send_telnet_command(serial, command):
    """
    Sends a Telnet command to an inverter and prints the acknowledgement.

    Parameters:
    - serial (str): The serial number of the inverter.
    - command (str): The command to send (e.g., "PGR01" or "PGR00").
    """
    try:
        with telnetlib.Telnet(f"edge-{serial}.local", 23) as tn:
            tn.write(command.encode() + b'\r\n')
            ack = tn.read_until(b"\n", 3).decode().strip()  # Read acknowledgment
            #print(f"Acknowledgement: {ack}")
    except Exception as e:
        print(f"Error: Failed to connect or send command to inverter with serial {serial}. {e}")
    return ack

def query_input_voltage_range(pcu_ids):
    result_list = []  # Initialize an empty list to store the returned values
    
    for pcu_id in pcu_ids:
        returned_value = send_telnet_command(pcu_id, 'QPIRI')  # Call the function and store the returned value

        if returned_value[72] == "0":
            result_list.append('appliance')  # Append the returned value to the result_list
        else:
            result_list.append('ups')  # Append the returned value to the result_list
    print("QPIRI_VOLTAGE_RANGE", result_list)
    return result_list  # Return the list containing all returned values

def set_target_and_current_mode():
    result_array = query_input_voltage_range(SERIAL_NUMBERS)
    #current_mode = None  # Assuming this needs to be calculated from result_array

    if all(result == "appliance" for result in result_array):
        target_mode = UPS
        target_mode_name = 'ups'
        current_mode = APPLIANCE
        current_mode_name = 'appliance'
    else:
        target_mode = APPLIANCE
        target_mode_name = 'appliance'
        current_mode = UPS
        current_mode_name = 'ups'

    print("Target Mode Command:", target_mode)
    print("Target Mode Name:", target_mode_name)
    print("Current Mode Command:", current_mode)
    print("Current Mode Name:", current_mode_name)
    return target_mode, target_mode_name, current_mode, current_mode_name

def calculate_query_delay():
    cmd_sent_timestamp = datetime.datetime.now()
    result_array = query_input_voltage_range(SERIAL_NUMBERS)
    detect_time = datetime.datetime.now()
    query_delay = (detect_time - cmd_sent_timestamp).total_seconds()
    print("Query Delay", query_delay)
    return query_delay

def calculate_propagation_delay(cmd_sent_timestamp, current_mode, current_mode_name, target_mode, target_mode_name):
    SN1_flag = True
    SN2_flag = True
    SN3_flag = True
    SN4_flag = True
    mode = []
    delays= []

    mode = query_input_voltage_range(SERIAL_NUMBERS)
   
    return delays

def write_to_file(data, filename):
    with open(filename, 'a') as f:
        f.write(','.join(map(str, data)) + '\n')

def calculate_average_delay(data):
    return sum(data) / len(data)

if __name__ == '__main__':
    
   # write_to_file(SERIAL_NUMBERS, 'pcm_delays_telnet.csv')
        calculate_query_delay()

    #for i in range(ITERATIONS):
        #target_mode, target_mode_name, current_mode, current_mode_name = set_target_and_current_mode()

        # Change mode for the first device in SERIAL_NUMBERS
        #target_device = SERIAL_NUMBERS[0]
        #print(f"Changing mode for device {target_device} from {current_mode} to {target_mode}")
        #send_telnet_command(target_device, target_mode)
        #cmd_sent_timestamp = datetime.datetime.now()
        #pcm_delays = calculate_propagation_delay(cmd_sent_timestamp, current_mode, current_mode_name, target_mode, target_mode_name)
        #print("PCM Delays:", pcm_delays)
       