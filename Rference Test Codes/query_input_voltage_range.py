import urllib3
import json
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            if "Failed" in input_voltage_range:
                print(f"[{timestamp}] Failed to query PCU {pcu_id}: {input_voltage_range}")
            else:
                print(f"[{timestamp}] PCU {pcu_id}: Input Voltage Range = {input_voltage_range}")
            results.append(result)
    return results

# Example usage:
edge_pcu = ['4000100158', '4000100104', '4000100323', '4000100247', '4000100142']
result_array = query_input_voltage_range(edge_pcu)
print(result_array)
