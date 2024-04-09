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


filename='Test_0.1'
gridsim_present=1
edge_pcu=[
    '4000100158',
    '4000100104',
    '4000100323',
    '4000100247',
    '4000100142'
]

pv_ips=[
    '192.168.128.243',
    '192.168.128.219',
    '192.168.128.211',
    '192.168.128.191',
    '192.168.128.185'
]

gridsim_ips=['192.168.128.245']

http1 = urllib3.PoolManager()

#Create directory for test case.
if not os.path.exists('./'+filename):
    os.mkdir('./'+filename)

#Create logger object.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler('./'+filename+'/'+filename+str(dt.datetime.now().strftime("DATE_%Y_%m_%d.TIME_%H_%M_%S"))+".log"),
        logging.StreamHandler(sys.stdout)
    ]
)
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
    gridsim=SCPI_interface(gridsim_ips[0], 1234, 'MX45')
    gridsim.connect()
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
        df=pd.read_csv(str('./'+filename+".csv"),header=[0])
    except Exception as e:
        print("Error while trying to open test sequence")
        print(e)
        sys.exit()
        
    try:
        env = os.environ            
        logging.info("Starting yokogawa logger")
        yokoProc = Popen(['python.exe', 'yokogawa.py', filename], stdout=PIPE)
        logging.info("Waiting for yokogawa logger to respond")
        logging.info(yokoProc.stdout.readline(1))
        logging.info("Starting REST_API logger")
        apiProc = Popen(['python.exe', 'REST_API.py'], stdout=PIPE)
    except Exception as e:
        print("Error while trying to open loggers")
        print(e)
        apiProc.kill()
        yokoProc.kill()
        sys.exit()

    try:
        testFramework(df,1)
    except Exception as e:
        print("Error while trying to open test sequence")
        print(e)
        sys.exit()

    try:
        apiProc.kill()
        yokoProc.kill()
    except Exception as e:
        print("Error while trying to terminate loggers")
        print(e)
        sys.exit()

#Functions and threads definition.
        
def pv_sim_write(pv,o,v,a):
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
    return http1.request(
        method="GET",
        url="http://edge-" + pcu_id + ":4000/api/device/status"
    )

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

def checkExitCondition(exit_type, exit_value, ):
    if str(exit_type).lower().replace(' ','')=='timer':
        logging.info('Checking timer condition')
        starttime = time.time()
        while time.time()-starttime<exit_value:
            logging.info('Timer: '+str(round(time.time()-starttime,2))+' out of '+str(exit_value))
            time.sleep(1)
        return 
    
    elif 'Bat Voltage>=' in str(exit_type):
        average_bat_v=0
        logging.info('Checking Battery voltage condition')
        while average_bat_v < exit_value:
            time.sleep(5)
            average_bat_v = 0
            for pcu_id in edge_pcu:
                try:
                    resp = getDeviceStatus(pcu_id)
                except Exception as e:
                    logging.info("Error while trying to query Edge system\n")
                    logging.info(e)
                    continue
                edge_status=[]
                try:
                    edge_status.append(json.loads(resp.data))
                    edge_bat_v=(edge_status[0]['data']['status']['general_status'][1]['battery_voltage'])
                    logging.info(edge_bat_v)
                    average_bat_v+=edge_bat_v
                    logging.info(average_bat_v)
                except Exception as e:
                    logging.info("Error while trying to read response data\n")
                    logging.info(e)
                    continue
            average_bat_v = average_bat_v/len(edge_pcu)
            logging.info(average_bat_v)
        return
    elif 'Bat Voltage<' in str(exit_type):
        average_bat_v = 60
        logging.info('Checking Battery voltage condition')
        while average_bat_v > exit_value:
            time.sleep(5)
            average_bat_v = 0
            for pcu_id in edge_pcu:
                try:
                    resp = getDeviceStatus(pcu_id)
                except Exception as e:
                    logging.info("Error while trying to query Edge system\n")
                    logging.info(e)
                    continue
                edge_status=[]
                try:
                    edge_status.append(json.loads(resp.data))
                    edge_bat_v=(edge_status[0]['data']['status']['general_status'][1]['battery_voltage'])
                    logging.info(edge_bat_v)
                    average_bat_v+=edge_bat_v
                    logging.info(average_bat_v)
                except Exception as e:
                    logging.info("Error while trying to read response data\n")
                    logging.info(e)
                    continue
            average_bat_v = average_bat_v/len(edge_pcu)
            logging.info(average_bat_v)
        return
    elif 'SOC>' in str(exit_type):
        average_SOC = 0
        logging.info('Checking Battery charge condition')
        while average_SOC < exit_value:
            time.sleep(5)
            average_SOC = 0
            for pcu_id in edge_pcu:
                try:
                    resp = getDeviceStatus(pcu_id)
                except Exception as e:
                    logging.info("Error while trying to query Edge system\n")
                    logging.info(e)
                    continue
                edge_status=[]
                try:
                    edge_status.append(json.loads(resp.data))
                    edge_SOC=(edge_status[0]['data']['status']['general_status'][1]['battery_capacity'])
                    logging.info(edge_SOC)
                    average_SOC+=edge_SOC
                    logging.info(average_SOC)
                except Exception as e:
                    logging.info("Error while trying to read response data\n")
                    logging.info(e)
                    continue
            average_SOC = average_SOC/len(edge_pcu)
            logging.info(average_SOC)
        return
    elif 'SOC<' in str(exit_type):
        average_SOC = 101
        logging.info('Checking Battery charge condition')
        while average_SOC > exit_value:
            time.sleep(5)
            average_SOC = 0
            for pcu_id in edge_pcu:
                try:
                    resp = getDeviceStatus(pcu_id)
                except Exception as e:
                    logging.info("Error while trying to query Edge system\n")
                    logging.info(e)
                    continue
                edge_status=[]
                try:
                    edge_status.append(json.loads(resp.data))
                    edge_SOC=(edge_status[0]['data']['status']['general_status'][1]['battery_capacity'])
                    logging.info(edge_SOC)
                    average_SOC+=edge_SOC
                    logging.info(average_SOC)
                except Exception as e:
                    logging.info("Error while trying to read response data\n")
                    logging.info(e)
                    continue
            average_SOC = average_SOC/len(edge_pcu)
            logging.info(average_SOC)
        return

#Test framework
def testFramework(df, testncycles=1):
    for k in range(testncycles):
        logging.info("")
        logging.info('Initializing test '+str(k+1))
        logging.info("")
        ##
        for sub_df in df.groupby('step'):
            ncycles=int(sub_df[1].iloc[0,1])
            for j in range(ncycles):
                for index,row in sub_df[1].iterrows():
                    #if row['step']>5:                
                    if True:
                        logging.info('-------------')
                        logging.info('')
                        logging.info(dt.datetime.now().strftime("%H:%M:%S"))
                        logging.info('STEP '+str(row['step'])+' - '+str(row['description'])+' - Iteration '+str(j+1))


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

                        checkExitCondition(exit_type, exit_value)
                            
                        logging.info('Exit Condition met, going to next step.')
                        logging.info('')
                        logging.info('-------------')
                        logging.info('')

    gridsim.query('OUTP:IMM OFF')
    logging.info("Turned off MX45 output")
    gridsim.query('++loc')
    logging.info("Setting MX45 to local mode")
    gridsim.close()
    logging.info("Closed MX45 socket")
    
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