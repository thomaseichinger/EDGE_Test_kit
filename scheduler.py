import time
import datetime as dt
import pandas as pd
import logging
import sys
import os
import subprocess
from subprocess import Popen, PIPE
import urllib3
import json
from SCPI_interface import SCPI_interface
from pvsim import pv_sim
from multiprocessing import Process
import csv


# filename='Test_0.1.csv'
filename='ETR002/ETC003.csv'

gridsim_present=1
# edge_pcu=[
#     '4000100158',
#     '4000100104',
#     '4000100323',
#     '4000100247',
#     '4000100142'
# ]

edge_pcu=[
    '4000100388',
    '4000100237'
]
master_pcu = edge_pcu[0]

pv_ips=[
    '192.168.128.243',
    '192.168.128.219',
    '192.168.128.211',
    '192.168.128.191',
    '192.168.128.185'
]

gridsim_ips = { 
                'NHR9410': '192.168.128.101',   #NHR9410
                'MX45': '192.168.128.245'       #MX45
}

gridsim_name = "NHR9410"

fields_per_device = [
    'output_source_priority',   #ratings
    'charger_source_priority',  #ratings
    'input_voltage_range',      #ratings
    'ac_output_voltage',        #general_status
    'ac_output_frequency',      #general_status
    'max_ac_charging_current',  #ratings
    'ac_input_current',         #general_status2
    'battery_charging_current', #general_status
    'ac_input_active_power',    #general_status2
    'ac_output_current',        #general_status2
    'ac_output_active_power',   #general_status
    'pv1_input_current',        #general_status
    'mode',                     #mode
    'fault_mode'                #QPGSn raw command
]
fieldnames = [
    'step',
    'time', 
    'pv1_input_current_sum', 
    'pv1_input_current_avg'
]

http1 = urllib3.PoolManager()

outfile=os.path.basename(filename)
outdir=os.path.dirname(filename) + '/' + os.path.splitext(outfile)[0]

#Create directory for test case.
if not os.path.exists('./'+outdir):
    os.makedirs('./'+outdir)

#Create logger object.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler('./'+outdir+'/'+outfile+str(dt.datetime.now().strftime("DATE_%Y_%m_%d.TIME_%H_%M_%S"))+".log"),
        logging.StreamHandler(sys.stdout)
    ]
)

#Create CSV write object
csv_filename_and_path = "./"+outdir+"/"+outfile+str(dt.datetime.now().strftime("DATE_%Y_%m_%d.TIME_%H_%M_%S"))+".csv"
csvfile = open(csv_filename_and_path, 'w', newline='')

try:
    pv1=pv_sim(pv_ips[0], 30000, 'ITECH')
    pv1.connect()
    pv2=SCPI_interface(pv_ips[1], 30000, 'ITECH')
    pv2.connect()
    pv3=SCPI_interface(pv_ips[2], 30000, 'ITECH')
    pv3.connect()
    pv4=SCPI_interface(pv_ips[3], 30000, 'ITECH')
    pv4.connect()
    pv5=SCPI_interface(pv_ips[4], 30000, 'ITECH')
    pv5.connect()
    if gridsim_name == "NHR9410":
        gridsim = SCPI_interface(gridsim_ips['NHR9410'], 5025, "NH Research")
        gridsim.connect()
    elif gridsim_name == "MX45":
        gridsim=SCPI_interface(gridsim_ips['MX45'], 1234, 'MX45')
        gridsim.connect()
    else:
        logging.erro("Error, please set `gridsim_name` to NHR9410 or MX45")
        exit(23)
except Exception as e:
    logging.info("Failed to establish SCPI connections")
    logging.info(e)
    sys.exit()

def log(pv):
        filename= 'PV_Logs-' + str(dt.now().strftime("%Y%m%d.%H%M"))
        #Create directory for test case.
        if not os.path.exists('./'+filename):
            os.mkdir('./'+filename)

        with open('./'+filename +'/'+pv.ip+ ".csv", "a+") as f:
            f.write('time start,Voltage,Current')

            while True:
                pv.query('System:Clear', False)
                f.write('\n' + str(dt.now())+',')
                f.write(pv.query('Measure:Voltage?')+',')
                f.write(pv.query('Measure:Current?'))

def main():
    #filename = sys.argv[1:]
    #if sys.argv[2:]:
    #    testncycles = sys.argv[2:]
    try:
        #Import the testing sequence.
        df=pd.read_csv(str('./'+filename),header=[0])
    except Exception as e:
        print("Error while trying to open test sequence")
        print(e)
        sys.exit()
        
    try:
        env = os.environ            
        logging.info("Starting yokogawa logger")
        yokoProc = Popen(['python.exe', 'yokogawa.py', os.path.splitext(outfile)[0]], stdout=PIPE)
        logging.info("Waiting for yokogawa logger to respond")
        logging.info(yokoProc.stdout.readline(1))
        logging.info("Starting REST_API logger")
        # apiProc = Popen(['python.exe', 'REST_API.py'], stdout=PIPE)
    except Exception as e:
        print("Error while trying to open loggers")
        print(e)
        # apiProc.kill()
        yokoProc.kill()
        sys.exit()

    try:
        logging.info("resolving edge devices names")
        for pcu_id in edge_pcu:
            getDeviceStatus(pcu_id)

        testFramework(df,1)
    except Exception as e:
        print("Error while trying to open test sequence")
        print(e)

    try:
        # apiProc.kill()
        yokoProc.kill()
    except Exception as e:
        print("Error while trying to terminate loggers")
        print(e)
        sys.exit()

#Functions and threads definition.
        
def pv_sim_write(pv,o,v,a):
    print(str(pv) + " " + str(o) + " " + str(v) + " " + str(a))
    try:
        pv.query('System:Clear', False)
    except Exception as e:
        logging.info("Failed to clear PV's error queue")
        logging.info(e)
        sys.exit()

    if(v not in str(pv.query('Voltage?'))): 
        try:
            pv.query('Voltage ' + v, False) 
        except Exception as e:
            logging.info("Failed to change PV's voltage")
            logging.info(e)
            sys.exit()
    if(v in str(pv.query('Voltage?'))):
        logging.info("Successfully changed voltage to " + v)

    if(a not in str(pv.query('Current?'))): 
        try:
            pv.query('Current ' + a, False) 
        except Exception as e:
            logging.info("Failed to change PV's current")
            logging.info(e)
            sys.exit()
    if(a in str(pv.query('Current?'))):
        logging.info("Successfully changed current to " + a)

    if(o not in str(pv.query('Output:State?'))): 
        try:
            pv.query('Output:State ' + o, False) 
        except Exception as e:
            logging.info("Failed to change PV's output")
            logging.info(e)
            sys.exit()
    if(o in str(pv.query('Output:State?'))):
        logging.info("Successfully changed output to " + o)
    

def grid_sim_write(on_off,ACDC,v,f,slew):
    if gridsim_name == 'MX45':
        grid_sim_write_mx45(on_off, ACDC, v, f, slew)
    elif gridsim_name == 'NHR9410':
        grid_sim_write_nhr9410(on_off, v, f, slew)

def grid_sim_write_nhr9410(on_off, v, f, slew):
    logging.info('Setting grid sim NHR 9410 with status:' + str(on_off) + ' voltage (CH1): ' + str(v))
    logging.info('Grid Sim in AC mode, with Voltage: '+str(v)+' and Frequency: '+str(f))

    # gridsim.query('INST:NSEL 2', False)
    gridsim.query('INST:NSEL 1', False)

    if(str(360) not in str(gridsim.query('VOLT:RANG?'))):
        gridsim.query('VOLT:RANG ' + str(360), False)
        logging.info("Successfully changed voltage range to 360")
    logging.info(gridsim.query('VOLT:RANG?'))

    if(str(f) not in str(gridsim.query('FREQ?'))):  
        gridsim.query('FREQ ' + str(f), False)
        logging.info("Succesfully changed Frequency")
    logging.info(gridsim.query('FREQ?'))

    if(str(v) not in str(gridsim.query('VOLT?'))):
        gridsim.query('VOLT ' + str(v), False)
        logging.info("Succesfully changed Volts")
    logging.info(gridsim.query('VOLT?'))

    if(str(slew) not in str(gridsim.query('VOLT:SLEW?'))):  
        gridsim.query('VOLT:SLEW ' + str(slew), False)
        logging.info("Successfully changed voltage slew rate")
    logging.info(gridsim.query('VOLT:SLEW?'))

    if int(on_off)==0:
        logging.info('Grid Sim OFF')
        gridsim.query('OUTP OFF', False)
    elif int(on_off)==1:
        logging.info('Grid Sim ON')
        gridsim.query('OUTP ON', False)

def grid_sim_write_mx45(on_off, ACDC, v, f, slew):
    logging.info('Setting grid sim with status:'+str(on_off)+' Voltage (CH1): '+str(v))

    if(str(300) not in str(gridsim.query('VOLT:RANG?'))): 
        gridsim.query('VOLT:RANG ' + str(300))
        logging.info("Successfully changed voltage range to 300")
    logging.info(gridsim.query('VOLT:RANG?'))

    if ACDC=='AC':
        logging.info('Grid Sim in AC mode, with Voltage: '+str(v)+' and Frequency: '+str(f))
        #logging.info(str(on_off)+str(ACDC)+str(v)+str(f))
        if('AC' not in str(gridsim.query('MODE?'))): 
            gridsim.query('MODE AC')
            logging.info("Succesfully changed mode to AC")
        
        if(str(f) not in str(gridsim.query('FREQ?'))):  
            gridsim.query('FREQ ' + str(f))
            logging.info("Succesfully changed Frequency")
        logging.info(gridsim.query('FREQ?'))

        if(str(v) not in str(gridsim.query('VOLT ' + str(v)))):
            gridsim.query('VOLT ' + str(v))
            logging.info("Succesfully changed Volts")
        logging.info(gridsim.query('VOLT?'))
        if(str(slew) not in str(gridsim.query('VOLT:SLEW:IMMEDIATE?'))):  
            gridsim.query('VOLT:SLEW ' + str(slew))
            logging.info("Successfully changed voltage slew rate")
        logging.info(gridsim.query('VOLT:SLEW:IMMEDIATE?'))

    if int(on_off)==0:
        logging.info('Grid Sim OFF')
        gridsim.query('OUTP:IMM OFF')
    elif int(on_off)==1:
        logging.info('Grid Sim ON')
        gridsim.query('OUTP ON')

def getDeviceStatus(pcu_id):
    try:
        resp = http1.request(
        method="GET",
        url="http://edge-" + pcu_id + ":4000/api/device/status"
        )
    except Exception as e:
        logging.error("Error while querying edge-" + pcu_id)
        logging.error(e)
    try:
        resp_obj = json.loads(resp.data)
    except Exception as e:
        logging.error("Error parsing response json data.")
        logging.error(e)
    return resp_obj

def postRawCommand(cmd, pcu_id):
    return http1.request(
        method="POST",
        url="http://edge-" + pcu_id + ":4000/api/device/raw_command",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json={
            "command": cmd
        }
    )

def getGeneralStatus(pcu_id):
    resp_obj = getDeviceStatus(pcu_id)
    return resp_obj['data']['status']['general_status'][1]

def getGeneralStatus2(pcu_id):
    resp_obj = getDeviceStatus(pcu_id)
    return resp_obj['data']['status']['general_status_2'][1]

def getRatings(pcu_id):
    resp_obj = getDeviceStatus(pcu_id)
    return resp_obj['data']['status']['ratings'][1]

def getMode(pcu_id):
    resp_obj = getDeviceStatus(pcu_id)
    return resp_obj['data']['status']['mode'][1]

def getFaultMode(pcu_id):
    try:
        resp = postRawCommand("QPGS" + str(edge_pcu.index(pcu_id) + 1), master_pcu)
    except Exception as e:
        logging.error("Error while querying edge-" + pcu_id)
        logging.error(e)
    try:
        resp_obj = json.loads(resp.data)
    except Exception as e:
        logging.error("Error parsing response json data.")
        logging.error(e)
    try:
        fault_mode = str(resp_obj['response']).split()[3]
    except Exception as e:
        logging.error("Error parsing response data.")
        logging.error("pcu_id is: " + edge_pcu[i-1])
        logging.error("Data is: " + str(resp_obj))
        logging.error(e)

    return fault_mode

def exit_condition_sum_up(general_status, field=None, accumulator=None):
    if field != None:
        logging.info("acc: " + str(accumulator) + " field: " + str(general_status[field]))
        return accumulator + general_status[field]

def exit_condition(accumulator=None):
    if accumulator != None:
        return accumulator/len(edge_pcu)

def log_measurement(step, csvwriter, exit_condition_field=None):
    pv1_input_current_sum = 0
    exit_condition_accumulator = 0
    csv_dict = {
                "step": step,
                "time": dt.datetime.now().isoformat()
                }
    for pcu_id in edge_pcu:
        general_status = getGeneralStatus(pcu_id)
        general_status_2 = getGeneralStatus2(pcu_id)
        ratings = getRatings(pcu_id)
        mode = getMode(pcu_id)
        try:
            csv_dict[pcu_id + " output_source_priority"] = ratings['output_source_priority']
            csv_dict[pcu_id + " charger_source_priority"] = ratings['charger_source_priority']
            csv_dict[pcu_id + " max_ac_charging_current"] = ratings['max_ac_charging_current']
            csv_dict[pcu_id + " input_voltage_range"] = ratings['input_voltage_range']
            csv_dict[pcu_id + " mode"] = mode
            csv_dict[pcu_id + " ac_output_voltage"] = general_status['ac_output_voltage']
            csv_dict[pcu_id + " ac_output_frequency"] = general_status['ac_output_frequency']
            csv_dict[pcu_id + " battery_charging_current"] = general_status['battery_charging_current']
            csv_dict[pcu_id + " ac_output_active_power"] = general_status['ac_output_active_power']
            csv_dict[pcu_id + " ac_input_current"] = general_status_2['ac_input_current']
            csv_dict[pcu_id + " ac_input_active_power"] = general_status_2['ac_input_active_power']
            csv_dict[pcu_id + " ac_output_current"] = general_status_2['ac_output_current']
            csv_dict[pcu_id + " fault_mode"] = getFaultMode(pcu_id)
            csv_dict[pcu_id + " pv1_input_current"] = general_status['pv1_input_current']
            pv1_input_current_sum += general_status['pv1_input_current']
        except Exception as e:
            logging.error("ERROR: Exception processing data")
            logging.error(e)
        exit_condition_accumulator = exit_condition_sum_up(general_status, exit_condition_field, exit_condition_accumulator)
    csv_dict['pv1_input_current_avg'] = pv1_input_current_sum/len(edge_pcu)
    csv_dict['pv1_input_current_sum'] = pv1_input_current_sum
    csvwriter.writerow(csv_dict)
    csvfile.flush()
    return exit_condition(exit_condition_accumulator)


def checkExitCondition(step, exit_type, exit_value, csvwriter):
    if str(exit_type).lower().replace(' ','')=='timer':
        logging.info('Checking timer condition')
        starttime = time.time()
        print("Step " + str(step))
        while time.time()-starttime<exit_value:
            log_measurement(step, csvwriter, None)
            print(str(exit_value - round(time.time()-starttime)) + " ", end='')
            time.sleep(1)
        return 
    
    elif 'Bat Voltage>=' in str(exit_type):
        average_bat_v=0
        logging.info('Checking Battery voltage condition')
        while average_bat_v < exit_value:
            time.sleep(5)
            average_bat_v = log_measurement(step, csvwriter, 'battery_voltage')
            logging.info("average_bat_v: " + str(average_bat_v))
        return
    elif 'Bat Voltage<' in str(exit_type):
        average_bat_v = 101
        logging.info('Checking Battery voltage condition')
        while average_bat_v > exit_value:
            time.sleep(5)
            average_bat_v = log_measurement(step, csvwriter, 'battery_voltage')
            logging.info("average_bat_v: " + str(average_bat_v))
        return
    elif 'SOC>' in str(exit_type):
        average_SOC = 0
        logging.info('Checking Battery charge condition')
        while average_SOC < exit_value:
            time.sleep(5)
            average_SOC = log_measurement(step, csvwriter, 'battery_capacity')
            logging.info("Average SoC: " + str(average_SOC))
        return
    elif 'SOC<' in str(exit_type):
        average_SOC = 101
        logging.info('Checking Battery charge condition')
        while average_SOC > exit_value:
            time.sleep(5)
            average_SOC = log_measurement(step, csvwriter, 'battery_capacity')
            logging.info("Average SoC: " + str(average_SOC))
        return

def init_gridsim_config():
    logging.info("Checking if NHR is in HW Mode 7, bussing CH1&2")
    if "7" not in gridsim.query("CONF:HW:MODE?"):
        logging.info("Configuring HW Mode 7. Bussing CH1 and CH2")
        gridsim.query("CONF:HW:MODE 7", False)
        time.sleep(5)
        error = gridsim.query("SYST:ERR?")
        if "No error" not in error:
            print(error)
            sys.exit(23)
        else:
            print("CoNFIGURED")
    else:
        logging.info("Already configured.")


#Test framework
def testFramework(df, testncycles=1):
    init_gridsim_config()

    for k in range(testncycles):
        logging.info("")
        logging.info('Initializing test '+str(k+1))
        logging.info("")
        
        logging.info('Setting up .csv file.')
        logging.info(csv_filename_and_path)

        for pcu_id in edge_pcu:
            tmp = [pcu_id + " " + field for field in fields_per_device]
            print(str(tmp))
            fieldnames.extend(tmp)

        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        ##
        for sub_df in df.groupby('step'):
            ncycles=int(sub_df[1].iloc[0,1])
            for j in range(ncycles):
                for index,row in sub_df[1].iterrows():
                    step = row['step']             
                    if True:
                        logging.info('-------------')
                        logging.info('')
                        logging.info(dt.datetime.now().strftime("%H:%M:%S"))
                        logging.info('STEP '+str(step)+' - '+str(row['description'])+' - Iteration '+str(j+1))


                        logging.info('')
                        #GRID SIMULATOR SETUP BLOCK
                        nretries=3
                        while nretries>0:
                            try:
                                #GRID SIM
                                logging.info('Grid Sim Conditions - ON (1) / OFF (0):'+str(row['Grid sim on_off'])+' | Voltage [V]: '+str(row['GridSimV'])+' | Frequency [Hz]: '+str(row['GridSimF']))
                                grid_sim_write(str(row['Grid sim on_off']),'AC',str(row['GridSimV']),str(row['GridSimF']),str(row['slew_rate']))
                                break
                            except Exception as error:
                                print(error)
                                nretries-=1
                        if nretries==0:
                            raise

                        nretries=3
                        while nretries>0:
                            try:
                                #PV SIMS
                                logging.info('PV Sim 1 Conditions - ON (1) / OFF (0):'+str(row['PV1_O'])+' | Voltage [V]: '+str(row['PV1_V'])+' | Current [A]: '+str(row['PV1_A']))
                                pv_sim_write(pv1,str(row['PV1_O']),str(row['PV1_V']),str(row['PV1_A']))

                                logging.info('PV Sim 2 Conditions - ON (1) / OFF (0):'+str(row['PV2_O'])+' | Voltage [V]: '+str(row['PV2_V'])+' | Current [A]: '+str(row['PV2_A']))
                                pv_sim_write(pv2,str(row['PV2_O']),str(row['PV2_V']),str(row['PV2_A']))

                                logging.info('PV Sim 3 Conditions - ON (1) / OFF (0):'+str(row['PV3_O'])+' | Voltage [V]: '+str(row['PV3_V'])+' | Current [A]: '+str(row['PV3_A']))
                                pv_sim_write(pv3,str(row['PV3_O']),str(row['PV3_V']),str(row['PV3_A']))

                                logging.info('PV Sim 4 Conditions - ON (1) / OFF (0):'+str(row['PV4_O'])+' | Voltage [V]: '+str(row['PV4_V'])+' | Current [A]: '+str(row['PV4_A']))
                                pv_sim_write(pv4,str(row['PV4_O']),str(row['PV4_V']),str(row['PV4_A']))

                                logging.info('PV Sim 5 Conditions - ON (1) / OFF (0):'+str(row['PV5_O'])+' | Voltage [V]: '+str(row['PV5_V'])+' | Current [A]: '+str(row['PV5_A']))
                                pv_sim_write(pv5,str(row['PV5_O']),str(row['PV5_V']),str(row['PV5_A']))

                                break
                            except Exception as error:
                                print(error)
                                nretries-=1
                        if nretries==0:
                            raise

                        logging.info('')
                        logging.info('Running relayScript as subprocess...')
                        try:
                            subprocess.run(["python.exe", "relayScript.py", "-"+(str(row['grid_relay'])), "1"])
                            subprocess.run(["python.exe", "relayScript.py", "-"+(str(row['load_relay'])), "3"])
                            logging.info('Successfully ran relayScript as subprocess')
                        
                        except Exception as e:
                            logging.info('Failed to run relayScript as subprocess')
                            logging.info(e)

                        #Check for exit conditions
                        logging.info('Exit condition:'+str(row['Exit condition'])+' | Value: '+str(row['Value']))
                        logging.info('')

                        exit_type=row['Exit condition']
                        exit_value=row['Value']
                        logging.info('Starting condition checking')

                        checkExitCondition(step, exit_type, exit_value, csvwriter)

    if gridsim_name == "MX45":
        gridsim.query('OUTP:IMM OFF')
        logging.info("Turned off MX45 output")
        gridsim.query('++loc')
        logging.info("Setting MX45 to local mode")
    elif gridsim_name == "NHR9410":
        gridsim.query('OUTP OFF', False)
        logging.info("Turning off NHR9410 output")

    gridsim.close()
    logging.info("Closed gridsim socket")
    
    subprocess.run(["python.exe", "relayScript.py", "-0", "1"])
    logging.info("Opened gridsim relay")
    
    subprocess.run(["python.exe", "relayScript.py", "-0", "3"])
    logging.info("Opened eload relay")

    pv1.close()
    logging.info("Closed pv1 socket")
    pv2.close()
    logging.info("Closed pv2 socket")
    pv3.close()
    logging.info("Closed pv3 socket")
    pv4.close()
    logging.info("Closed pv4 socket")
    pv5.close()
    logging.info("Closed pv5 socket")



if __name__ == "__main__":
    main()