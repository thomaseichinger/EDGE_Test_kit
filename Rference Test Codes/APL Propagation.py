import urllib3
import json
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import telnetlib
import time


# Global setup
http = urllib3.PoolManager()
SERIAL_NUMBERS = ['4000100104', '4000100323', '4000100247', '4000100142']
TARGET_PCM = ['4000100104']
CHANGE_DELAY_S = 0.5
WAIT_TIME_S = 0  # Adjust according to the requirement
ITERATIONS = 100
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
        print(f"Connecting to inverter with serial: {serial}...")
        with telnetlib.Telnet(f"edge-{serial}.local", 23) as tn:
            print(f"Sending command '{command}'...")
            tn.write(command.encode() + b'\r\n')
            ack = tn.read_until(b"\n", 3).decode().strip()  # Read acknowledgment
            print(f"Acknowledgement: {ack}")
    except Exception as e:
        print(f"Error: Failed to connect or send command to inverter with serial {serial}. {e}")


    
def query_single_pcu(pcu_id):
    """
    Queries and returns the input voltage range for a single PCU ID with a timestamp.
    
    Parameters:
    pcu_id (str): The PCU ID to query.
    
    Returns:
    tuple: A tuple containing the PCU ID, input voltage range, and a timestamp.
    """
    http = urllib3.PoolManager()
    url = f'http://edge-{pcu_id}:4000/api/device/status'
    try:
        resp = http.request('GET', url)
        edge_status = json.loads(resp.data)
        input_voltage_range = edge_status['data']['status']['ratings'][1]['input_voltage_range']
        # Include microseconds in the timestamp and format to show tenths of a second
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
        return (pcu_id, input_voltage_range, timestamp)
    except Exception as e:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
        return (pcu_id, str(e), timestamp)

def query_input_voltage_range(pcu_ids):
    """
    Queries and prints the input voltage range for a list of PCU IDs with timestamps including tenths of a second
    using concurrent requests to speed up the process. It also returns the results in an array.
    
    Parameters:
    pcu_ids (list): A list of PCU IDs to query.
    
    Returns:
    list: A list of tuples each containing the PCU ID, input voltage range, and a timestamp.
    """
    results = []
    with ThreadPoolExecutor(max_workers=len(pcu_ids)) as executor:
        future_to_pcu = {executor.submit(query_single_pcu, pcu_id): pcu_id for pcu_id in pcu_ids}
        for future in as_completed(future_to_pcu):
            result = future.result()
            pcu_id, input_voltage_range, timestamp = result
            #if "Failed" in input_voltage_range:
            #    print(f"[{timestamp}] Failed to query PCU {pcu_id}: {input_voltage_range}")
            #else:
             #   print(f"[{timestamp}] PCU {pcu_id}: Input Voltage Range = {input_voltage_range}")
            results.append(result)
    return results


def set_target_and_current_mode():
    result_array = query_input_voltage_range(SERIAL_NUMBERS)
    current_mode = None  # Assuming this needs to be calculated from result_array

    if result_array[0][1] == 'appliance' and  result_array[1][1] == 'appliance' and  result_array[1][1] == 'appliance' and  result_array[2][1] == 'appliance': 
        target_mode = UPS
        target_mode_name = 'ups'
        current_mode = APPLIANCE
        current_mode_name = 'appliance'
    else:
        target_mode = APPLIANCE
        target_mode_name = 'appliance'
        current_mode = UPS
        current_mode_name = 'ups'

    return target_mode, target_mode_name, current_mode, current_mode_name

def calculate_query_delay():
    cmd_sent_timestamp = datetime.datetime.now()
    result_array = query_input_voltage_range(SERIAL_NUMBERS)
    detect_time = datetime.datetime.now()
    query_delay = (detect_time - cmd_sent_timestamp).total_seconds()
    return query_delay

def average_query_delay(num_samples):
    total_delay = 0
    for _ in range(num_samples):
        total_delay += calculate_query_delay()
    return total_delay / num_samples    

def calculate_propagation_delay(cmd_sent_timestamp, current_mode, target_mode):
    SN1_flag = True
    SN2_flag = True
    SN3_flag = True
    SN4_flag = True
    
    print("Querying Input Voltage Mode")

    while SN1_flag or SN2_flag or SN3_flag or SN4_flag:
        result_array= query_input_voltage_range(SERIAL_NUMBERS)
        #print(result_array)
        #time.sleep(1)
       

        if result_array[0][1] == target_mode and SN1_flag:
            SN1_time =  datetime.datetime.now()
            SN1_delay = (SN1_time - cmd_sent_timestamp).total_seconds()
            print(f"Delay for {result_array[0][0]} is {SN1_delay}")   
            SN1_flag = False

        if result_array[1][1] == target_mode and SN2_flag:
            SN2_time =  datetime.datetime.now()
            SN2_delay = (SN2_time - cmd_sent_timestamp).total_seconds()
            print(f"Delay for {result_array[1][0]} is {SN2_delay}")   
            SN2_flag = False 

        if result_array[2][1] == target_mode and SN3_flag:
            SN3_time =  datetime.datetime.now()
            SN3_delay = (SN3_time - cmd_sent_timestamp).total_seconds()
            print(f"Delay for {result_array[2][0]} is {SN3_delay}")   
            SN3_flag = False

        if result_array[3][1] == target_mode and SN4_flag:
            SN4_time =  datetime.datetime.now()
            SN4_delay = (SN4_time - cmd_sent_timestamp).total_seconds()
            print(f"Delay for {result_array[3][0]} is {SN4_delay}")   
            SN4_flag = False 
    return SN1_delay, SN2_delay, SN3_delay, SN4_delay

    



if __name__ == '__main__':

    average_delay = average_query_delay(2)  # Calculate average of n samples
    print("Average query delay:", average_delay)
    target_mode, target_mode_name, current_mode, current_mode_name = set_target_and_current_mode()
    print("Target Mode Command:", target_mode)
    print("Target Mode Name:", target_mode_name)
    print("Current Mode Command:", current_mode)
    print("Current Mode Name:", current_mode_name)

    # Change mode for the first device in SERIAL_NUMBERS
    target_device = SERIAL_NUMBERS[0]
    print(f"Changing mode for device {target_device} from {current_mode} to {target_mode}")
    send_telnet_command(target_device, target_mode)
    cmd_sent_timestamp = datetime.datetime.now()
    all_pcm_delay = calculate_propagation_delay(cmd_sent_timestamp, current_mode_name, target_mode_name )

    
    
    



