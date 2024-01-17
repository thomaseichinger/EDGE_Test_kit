import time
import datetime as dt
import pandas as pd
import logging
import sys
import os
import socket
import subprocess

term = '\n'
filename='SIP001_SF5.csv'
gridsim_present=1

def main():
    #filename = sys.argv[1:]
    #if sys.argv[2:]:
    #    testncycles = sys.argv[2:]
    try:
        #Import the testing sequence.
        df=pd.read_csv(str('SIP001_SF5.csv\\SITP001_SF5.csv'),header=[0])
        ##    for index,row in df.iterrows():
        ##        logging.info(row)
        '''
        try:
            subprocess.run(["python.exe", "yokogawa.py", "&"])
        except Exception as e:
            print("Error while trying to open test sequence")
            print(e)
            sys.exit()'''
        subprocess.run(["python.exe", "REST_API.py"])
        
        testFramework(df)
    except Exception as e:
        print("Error while trying to open test sequence")
        print(e)
        sys.exit()

#Create directory for test case.
if not os.path.exists('./'+filename):
    os.mkdir('./'+filename)

#Create logger object.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler('./'+filename+'/'+filename+".log"),
        logging.StreamHandler(sys.stdout)
    ]
)

#Gridsim query function
def query(msg: bytes, debug = False):
    cmd = bytes((msg+term).encode('utf-8'))
    instrument.send(cmd)
    if debug: print("trying to send " +str(cmd))
    data = bytes(''.encode('utf-8'))
    data += instrument.recv(4096)
    if debug: print("received " + str(data.encode('utf-8')))
    return data

#Grid Simulator object
if gridsim_present==1:
    print('Stablishing SCPI connection with grid sim...')
    try:
        instrument=socket.socket()
        instrument.connect(('192.168.128.245', 1234))
        data = bytes(''.encode('utf-8'))
        data = query('*IDN?')
        if 'MX45' not in str(data): 
            print('Error while trying to establish SCPI connection')
            sys.exit()
        print("Successfully established connection with MX45")          
    except Exception as e:
        print('Error while trying to establish SCPI connection')
        print(e)
        sys.exit()

#Functions and threads definition.

def grid_sim_write(on_off,ACDC,v,f,slew):

    logging.info('Setting grid sim with status:'+str(on_off)+' Voltage (CH1): '+str(v))

    if(str(300) not in str(query('VOLT:RANG?'))): 
        query('VOLT:RANG ' + str(300))
        print("Successfully changed voltage range to 300")
    print(query('VOLT:RANG?'))

    if ACDC=='AC':
        logging.info('Grid Sim in AC mode, with Voltage: '+str(v)+' and Frequency: '+str(f))
        #logging.info(str(on_off)+str(ACDC)+str(v)+str(f))
        if('AC' not in str(query('MODE?'))): 
            query('MODE AC')
            print("Succesfully changed mode to AC")
        
        if(str(f) not in str(query('FREQ?'))):  
            query('FREQ ' + str(f))
            print("Succesfully changed Frequency")
        print(query('FREQ?'))

        if(str(v) not in str(query('VOLT ' + str(v)))):
            query('VOLT ' + str(v))
            print("Succesfully changed Volts")
        print(query('VOLT?'))
        if(str(slew) not in str(query('VOLT:SLEW:IMMEDIATE?'))):  
            query('VOLT:SLEW ' + str(slew))
            print("Successfully changed voltage slew rate")
        print(query('VOLT:SLEW:IMMEDIATE?'))

    if int(on_off)==0:
        logging.info('Grid Sim OFF')
        query('OUTP:IMM OFF')
    
    elif int(on_off)==1:
        logging.info('Grid Sim ON')
        query('OUTP ON')


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
                        if gridsim_present==1:
                            #GRID SIMULATOR SETUP BLOCK
                            nretries=3
                            while nretries>0:
                                try:
                                    #GRID SIM
                                    logging.info('Grid Sim Conditions - ON (1) / OFF (0):'+str(row['Grid sim on_off'])+' | Voltage [V]: '+str(row['GridSimV'])+' | Frequency [Hz]: '+str(row['GridSimF']))
                                    grid_sim_write(str(row['Grid sim on_off']),'AC',str(row['GridSimV']),str(row['GridSimF']),str(row['slew_rate']))
                                    
                                    subprocess.run(["python.exe", "relayScript.py", "-"+(str(row['grid_relay'])), "1"])
                                    subprocess.run(["python.exe", "relayScript.py", "-"+(str(row['load_relay'])), "3"])
                                    break
                                except Exception as error:
                                    print(error)
                                    nretries-=1
                            if nretries==0:
                                raise

                        

                            logging.info('')


                        #Check for exit conditions
                        logging.info('Exit condition:'+str(row['Exit condition'])+' | Value: '+str(row['Value']))
                        logging.info('')

                        exit_condition=False
                        exit_type=row['Exit condition']
                        exit_value=row['Value']
                        refresh_period=0.1
                        logging.info('Starting condition checking')

                        while not exit_condition:
                            if str(exit_type).lower().replace(' ','')=='timer':
                                logging.info('Checking timer condition')
                                starttime = time.time()

                                while time.time()-starttime<row['Value']:
                                    logging.info('STEP '+str(row['step'])+' - '+str(row['description'])+' - Iteration '+str(j+1))
                                    logging.info('Timer: '+str(round(time.time()-starttime,2))+' out of '+str(row['Value']))
                                    time.sleep(refresh_period)

                                break
                            
                        logging.info('Condition met, going to next step.')
                        logging.info('')
                        logging.info('-------------')
                        logging.info('')
    query('OUTP OFF')
    query('++loc')
    subprocess.run(["python.exe", "relayScript.py", "-0", "1"])
    subprocess.run(["python.exe", "relayScript.py", "-0", "3"])


if __name__ == "__main__":
    main()