import time
import datetime as dt
import math
import pandas as pd
import logging
import threading
from datetime import datetime
import sys
import numpy as np
import os
import lib.OOP_LCB as OOP_LCB
import lib.SCPI_interface as SCPI_interface
import lib.Edge_telnet as edge_telnet
import lib.Waveshare_Relay_Controller as Waveshare_Relay_Controller
import lib.Labjack as labjack
from queue import Queue

#Modbus 11/4
#Infinity 20/3
#BATT 18/7
#EAC 17/6

test='SI001'


##Definition of variables present in the test.
##Presence of instruments
testncycles=1
gridsim_present=1
voltronics=0
edgepresent=0
lyra_present=0
relays_present=0
Modbus_COMPORT='COM17'
genset_app=False
##Comports and addresses
    
volt_comport=6
lcb_comport=7
edge_addresses=[4000100026,4000000010]

#Queue for gridsim_thread
gridsim_queue=Queue(maxsize=0)

#Queue for the relays thread
relays_queue=Queue(maxsize=0)

##Creation of instruments objects.
#LCB setup.
if lyra_present:
    lcb=OOP_LCB.LCB(lcb_comport,1)

#Grid Simulator object
if gridsim_present==1:
    print('Stablishing SCPI connection with grid sim...')
    try:
        
        instrument=SCPI_interface.select_instrument()
    except:
        print('Error while trying to stablish SCPI connection')

#Waveshare Modbus Relay module object
if relays_present:
    try:
        relay_module=Waveshare_Relay_Controller.relay_module(Modbus_COMPORT,9600,1)
        print('Relay status:'+str(relay_module.read_relays_status()))
    except Exception as e:
        print('Error while connecting to relay module')
        print(e)
        pass

if edgepresent==1:
    edges_units=[]
    
#EDGE system object
if edgepresent==1:
    for edge_address in edge_addresses:
        try:
            edge=edge_telnet.edge_system(edge_address)
            print('Connected to Edge System under test at '+str(edge_address))
            print('QPIRI CMD')
            print(edge.raw_query('QPIRI',1))
            edges_units.append(edge)
        except Exception as e:
            print('Error while connecting to edge system')
            print(e)
            raise


#Labjack object
if genset_app:
    #Create Labjack instance
    d=labjack.openAllU3()
    labj=d["320091812"]
    #Configure everything as input
    labj.configIO(FIOAnalog=255)
    


#Functions and threads definition.

def grid_sim_write(on_off,ACDC,v,f):

    logging.info('Setting grid sim with status:'+str(on_off)+' Voltage (CH1): '+str(v))

    if ACDC=='AC':
        logging.info('Grid Sim in AC mode, with Voltage: '+str(v)+' and Frequency: '+str(f))
        #logging.info(str(on_off)+str(ACDC)+str(v)+str(f))
        instrument.query('SYST:FUNC ONE')
        instrument.query('SYST:ERROR?')
        instrument.query('SOURCE:FUNC AC')
        instrument.query('SYST:ERROR?')
        instrument.query('PVOLTage A,'+str(v))
        logging.info('Gridsim voltage, setted correctly')
        instrument.query('SYST:ERROR?')
        instrument.query('FREQuency '+str(f))
        instrument.query('SYST:ERROR?')
        
    elif ACDC=='DC':
        logging.info('Grid Sim in DC mode, with Voltage: '+str(v))
        instrument.query('SYST:FUNC MULT')
        instrument.query('SOURCE:FUNC DC')
        instrument.query('SYST:ERROR?')
        instrument.query('PVOLTage:DC A,'+str(v))
        logging.info('Gridsim voltage, setted correctly')
        instrument.query('SYST:ERROR?')
    
    if int(on_off)==0:
        logging.info('Grid Sim OFF')
        instrument.query('OUTP OFF')
    
    elif int(on_off)==1:
        logging.info('Grid Sim ON')
        instrument.query('OUTP ON')


def gridsimulator_thread(instrument,scpidf):
    global test_done
    global gridsim_queue
    global gridsim_timer
    while True:
        if test_done:
            break
        else:
            if gridsim_queue.empty():
                gridsim_queue.put('Read')
                #print('hey')

            else:
                task = gridsim_queue.get()
                #print('hey2')
                if task=='Read':
                    #print('hey3')
                    try:
                        #logging.info('Reading thread, not writing info in file')
                        if time.time()-gridsim_timer>1:
                            gridsim_timer=time.time()
                            if len(scpidf.columns)==0:
                                scpidf=pd.DataFrame(columns=['datetime','time']+['GridSim V','GridSim I','GridSim Freq','GridSim P','GridSim Q'])
                                ##To retrieve all information.
                                #str(instrument.query('FETC:SCAL?'))
                            scpidf.loc[len(scpidf)+1]=[datetime.now(),time.time()]+[str(instrument.query('FETC:VOLT?')),
                                                                                    str(instrument.query('FETC:CURR?')),
                                                                                    str(instrument.query('FETC:FREQ?')),
                                                                                    str(instrument.query('FETC:POWer?')),
                                                                                    str(instrument.query('FETC:POWer:REACtive?'))]
                            scpidf.to_excel('./'+filename+'/'+filename+'_General_data.xlsx',header=True,index=False)
                            #time.sleep(1-0.12)
                            gridsim_queue.put('Read')
##                            logging.info("Grid Sim Voltage [V]: "+ str(instrument.query('FETC:VOLT?')))
                    except Exception as e:
                        print(e)
                        print('Error reading Grid Sim information')
                        pass

                elif task=='Write':
                    #print('hey4')
                    try:
                        grid_sim_write(row['on_off'],row['GridSimOutput'],row['GridSimV1'],row['GridSimF1'])
                        gridsim_queue.put('Read')
                    except Exception as e:
                        print(e)
                        print('Error writing Grid Sim information')
                        pass

                elif task=='END':
                    #print('hey4')
                    try:
                        grid_sim_write(0,'AC',0,50)
                    except Exception as e:
                        print(e)
                        print('Error finishing grid sim thread')
                        pass
                        
def edge_thread(edge_syst,unit,qpigs_df,qpigs2_df,qpiri_df,qpgs0_df):
    global test_done
    
    #Command + length
    #Beginning + end of test
    BOT={"QET":1,"QLT":1}
    #While testing
    WT={"QPIGS":24,"QPIGS2":5}
    #While testing, slower. CMD+Length+freq in s
    WTS={"QPIRI":(30,60)}

    ##
    BOT_dfs={}
    WT_dfs={}
    WTS_dfs={}

    #Initialize BOT dfs
    for cmd in BOT.keys():
        try:
            length=BOT[cmd]
            df=pd.DataFrame(columns=['datetime','time']+[cmd+"_{0:03d}".format(i) for i in range(1,length+1)])
            data=edge_syst.query(cmd,1)
            df.loc[len(df)+1]=[datetime.now(),time.time()]+data
            df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_'+str(cmd)+'.xlsx',
                              header=True,
                              index=False)
            BOT_dfs.update({cmd:df})
            
        
        except:
            pass

    #Initialize WT dfs
    for cmd in WT.keys():
        try:
            length=WT[cmd]
            df=pd.DataFrame(columns=['datetime','time']+[cmd+"_{0:03d}".format(i) for i in range(1,length+1)])
            data=edge_syst.query(cmd,1)
            df.loc[len(df)+1]=[datetime.now(),time.time()]+data
            df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_'+str(cmd)+'.xlsx',
                              header=True,
                              index=False)
            WT_dfs.update({cmd:df})

        except:
            pass


    #Initialize WTS dfs
    for cmd in WTS.keys():
        try:
            length=WTS[cmd][0]
            df=pd.DataFrame(columns=['datetime','time']+[cmd+"_{0:03d}".format(i) for i in range(1,length+1)])
            data=edge_syst.query(cmd,1)
            df.loc[len(df)+1]=[datetime.now(),time.time()]+data
            df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_'+str(cmd)+'.xlsx',
                              header=True,
                              index=False)
            WTS_dfs.update({cmd:df})

        except:
            pass

    
    while True:
        if test_done:
            break
        else:
            record_init=time.time()
            #Update WT dfs
            for cmd in WT.keys():
                try:
                    data=edge_syst.query(cmd,1)
                    df=WT_dfs[cmd]
                    df.loc[len(df)+1]=[datetime.now(),time.time()]+data
                    df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_'+str(cmd)+'.xlsx',
                                      header=True,
                                      index=False)
                    WT_dfs.update({cmd:df})
                    
                except:
                    pass

            for cmd in WTS.keys():
                try:
                    polling_freq=WTS[cmd][1]
                    if time.time()-record_init>polling_freq:
                        record_init=time.time()
                        data=edge_syst.query(cmd,1)
                        df=WTS_dfs[cmd]
                        df.loc[len(df)+1]=[datetime.now(),time.time()]+data
                        df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_'+str(cmd)+'.xlsx',
                                          header=True,
                                          index=False)
                        WTS_dfs.update({cmd:df})

                except:
                    pass
##                
##
##            try:
##                if len(qpiri_df)==0:
##                    qpiri_df=pd.DataFrame(columns=['datetime','time']+['QPIRI_'+"{0:03d}".format(i) for i in range(1,30+1)])
##                data=edge_syst.query('QPIRI',1/2)
##                qpiri_df.loc[len(qpiri_df)+1]=[datetime.now(),time.time()]+data
##                qpiri_df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_QPIRI.xlsx',
##                                  header=True,
##                                  index=False)
##                
##            except:
##                pass
##            
##            try:
##                if len(qpigs_df)==0:
##                    qpigs_df=pd.DataFrame(columns=['datetime','time']+['QPIGS_'+"{0:03d}".format(i) for i in range(1,24+1)])
##                data=edge_syst.query('QPIGS',1/2)
##                qpigs_df.loc[len(qpigs_df)+1]=[datetime.now(),time.time()]+data
##                qpigs_df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_QPIGS.xlsx',
##                                  header=True,
##                                  index=False)
##                
##            except:
##                pass
##
##            try:
##                if len(qpigs2_df)==0:
##                    qpigs2_df=pd.DataFrame(columns=['datetime','time']+['QPIGS2_'+"{0:03d}".format(i) for i in range(1,5+1)])
##                data=edge_syst.query('QPIGS2',1/2)
##                qpigs2_df.loc[len(qpigs2_df)+1]=[datetime.now(),time.time()]+data
##                qpigs2_df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_QPIGS2.xlsx',
##                                   header=True,
##                                   index=False)
##                
##            except:
##                pass

##            try:
##                if len(qpgs0_df)==0:
##                    qpgs0_df=pd.DataFrame(columns=['datetime','time']+['QPGS0_'+"{0:03d}".format(i) for i in range(1,27+1)])
##                data=edge_syst.raw_query('QPGS'+str(unit-1),1)
##                qpgs0_df.loc[len(qpgs0_df)+1]=[datetime.now(),time.time()]+data
##                qpgs0_df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_QPGS'+str(unit-1)+'.xlsx',
##                                   header=True,
##                                   index=False)
##                
##            except Exception as e:
##                #print(e)
##                pass

    #Update BOT dfs
    for cmd in BOT.keys():
        try:
            data=edge_syst.query(cmd,1)
            df=BOT_dfs[cmd]
            df.loc[len(df)+1]=[datetime.now(),time.time()]+data
            df.to_excel('./'+filename+'/'+filename+'_'+str(unit)+'_'+str(cmd)+'.xlsx',
                              header=True,
                              index=False)
            BOT_dfs.update({cmd:df})
            
        
        except:
            pass
def lcb_thread(lcb,lcb_df):
    while True:
        # check for stop
        global test_done
        if test_done:
            break

        try:
            if len(lcb_df.columns)==0:
                lcb_df=pd.DataFrame(columns=['datetime','time']+['Data'])
            data=lcb.measure_sideA()
            lcb_df.loc[len(lcb_df)+1]=[datetime.now(),time.time()]+[data]
            lcb_df.to_excel('./'+filename+'/'+filename+'_LCB_data.xlsx',
                          header=True,
                          index=False)
            time.sleep(1-0.035)
        except Exception as e:
            print(e)
            print('Error writing Lyra information.')
            pass


def relays_thread(relay_module):
    global test_done
    global relays_queue
    while True:
        if test_done:
            break
        else:
            if relays_queue.empty():
                pass
            else:
                task=relays_queue.get()
                print(task)
                if task=='close_all':
                    try:
                        relay_module.close_all_module_relays()
                    except Exception as e:
                        print('Error while executing action')
                        print(e)
                    
                elif task=='open_all':
                    try:
                        relay_module.open_all_module_relays()
                    except Exception as e:
                        print('Error while executing action')
                        print(e)

                elif task[0]=='profile':
                    try:
                        relay_module.load_profile(task[1])
                    except Exception as e:
                        print('Error while executing action')
                        print(e)
                    
                elif task[0]=='close':
                    try:
                        relay_module.close_relay(task[1])
                    except Exception as e:
                        print('Error while executing action')
                        print(e)

                elif task[0]=='open':
                    try:
                        relay_module.open_relay(task[1])
                    except Exception as e:
                        print('Error while executing action')
                        print(e)
            
gen_start_signal=False
def labjack_thread(labjack_object):
    global gen_start_signal
    global relays_present
    genset_active=0
    genset_disable=1
    if relays_present:
        relay_module.open_relay(7)
        relay_module.open_relay(4)
        
    while True:
        #Loop that reads the status of the gen and grid status
        #Documentation exhibits the right attribute to read the status
        #https://github.com/labjack/LabJackPython/blob/851c5eb06c52e1c8fa3d117b551c18ff1db4e75b/src/u3.py
        gen_start_signal_v=labjack_object.getAIN(4)
        #print(gen_start_signal_v)
        if gen_start_signal_v>2:
            gen_start_signal=True
            if genset_active==0:
                genset_active=1
                genset_disable=0
                print(str(datetime.datetime.now()),'Genset signal On, [V] :',str(gen_start_signal_v))
                
                try:
                    if relays_present:
                        relay_module.close_relay(7)
                except:
                    print('Error trying to turn on genset')
                    pass
        else:
            if genset_disable==0:
                genset_disable=1
                genset_active=0
                gen_start_signal=False
                print(str(datetime.datetime.now()),'Genset signal Off, [V] :',str(gen_start_signal_v))
                try:
                    if relays_present:
                        relay_module.open_relay(7)
                except:
                    print('Error while trying to disable genset')
                    
            genset_active=0
            gen_start_signal=False
            
        #gen_status=labjack_object.
        time.sleep(1)

######################################################
######################################################
######################################################
######################################################
#Define and start the relays module thread
test_done=False
if relays_present:
    t0 = threading.Thread(target=relays_thread, args=(relay_module,))
    t0.start()

gridsim_timer=time.time()


print('Test name: ',test)

filename=test
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
if lyra_present:
    #Log the first calibration parameters of LCB.
    logging.info('Lyra calibration parameters: '+str(lcb.get_v1_offsets())+'  '+str(lcb.get_v1_gains()))
logging.info('Test initialization - '+str(filename))
# logging.info('Initial condition: '+tests[test_name])

#Check for the initial condition.
#check_IC_setupB(tests[test_name])

#Import the testing sequence.
df=pd.read_excel('./Test sequences/'+filename+'.xlsx',header=[0])
##    for index,row in df.iterrows():
##        logging.info(row)
    
try:                                   
    #DEFAULT is off and 0V output.
    if gridsim_present==1:
        grid_sim_write(0,'AC',0,50)
        
    #relay_module.open_all_module_relays()
    if relays_present:
        relays_queue.put('open_all')
except:
    pass

#Input data check
if df['step'].isin([np.NaN]).any():
    print('Please check the input of the test case. Step column is not right.')
    raise

for sdf in df.groupby('step'):
    subdf=sdf[1]
    if np.isnan(subdf.iloc[0,1]):
        print('Please check input of the test case. Ncycles column is not right.')
        raise
logging.info('Data check has passed, step and ncycles are formated correctly.')

exec_time=time.time()

#Synchronizing pulse with Yokogawa.
logging.info("")
logging.info('Synchronizing pulse')
logging.info("")
#relay_module.close_relay(8)
if not genset_app:
    if relays_present:
        relays_queue.put(('close',5))
if relays_present:
    relays_queue.put(('close',8))
    time.sleep(8)
#relay_module.open_relay(8)
    relays_queue.put(('open',8))

#Define and start the grid simulator thread
if gridsim_present:
    t1 = threading.Thread(target=gridsimulator_thread, args=(instrument,general_output))
    t1.start()

#Definition and start of the LCB and EDGE system threads.
if lyra_present:
    t2 = threading.Thread(target=lcb_thread, args=(lcb,lcb_df))
    t2.start()

edge_threads=[]
if edgepresent:
    for edge_unit in edge_units:
        #Empty recipient dataframes.
        general_output=pd.DataFrame()
        qpigsdf=pd.DataFrame()
        qpigs2df=pd.DataFrame()
        qpiridf=pd.DataFrame()          
        lcb_df=pd.DataFrame()
        qpgs0_df=pd.DataFrame()
        #Thread creation
        t4 = threading.Thread(target=edge_thread,args=(edge_unit,1,qpigsdf,qpigs2df,qpiridf,qpgs0_df))
        t4.start()
        edge_threads.append(t4)

if genset_app:
    t6 = threading.Thread(target=labjack_thread,args=(labj))



#Test framework
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
                                logging.info('Grid Sim Conditions - ON (1) / OFF (0):'+str(row['on_off'])+' | Voltage [V]: '+str(row['GridSimV1'])+' | Frequency [Hz]: '+str(row['GridSimF1']))
                                gridsim_queue.put('Write')
                                break
                            except Exception as error:
                                print(error)
                                nretries-=1
                        if nretries==0:
                            raise

                        logging.info('')

                    #GRID Relay setup block.
                    if relays_present:
                        try:
                            #GRID
                            logging.info('Grid  Conditions - ON (1) / OFF (0):'+str(row['grid_relay']))
                            if row['grid_relay']==1:
                                #relay_module.close_relay(5)
                                relays_queue.put(('close',4))
                                
                            elif row['grid_relay']==0:
                                #relay_module.open_relay(5)
                                relays_queue.put(('open',4))
                        except Exception as error:
                            print(error)
                            raise

                    #PV Bypass  SETUP BLOCK
                    if relays_present:
                        try:
                            #GRID
                            logging.info('PV bypassed ON (1) / OFF (0) '+str(row['PV_bypass']))
                            if row['PV_bypass']==1:
                                #relay_module.close_relay(6)
                                relays_queue.put(('close',6))
                            elif row['PV_bypass']==0:
                                #relay_module.open_relay(6)
                                relays_queue.put(('open',6))
                        except Exception as error:
                            print(error)
                            raise



                    #LOAD RACK SETUP BLOCK
                    if relays_present:
                        try:
                            logging.info('LOADS STATUS: '+str([row['load_1'],row['load_2'],row['load_3']]))
                            #relay_module.load_profile([row['load_1'],row['load_2'],row['load_3']])
                            relays_queue.put(('profile',[row['load_1'],row['load_2'],row['load_3']]))
                        except Exception as error:
                            print(error)
                            raise

                    #GENSET
                    if genset_app:
                        genset_condition=row['Genset_OpMode']
                        #0 is relay disabled
                        #1 is relay enabled
                        #2 will dictate what the ZCC does based on Labjack Signal.
                        if genset_condition==0:
                            #Genset relay is disabled by sending a open_relay(7) to the relay module queue, and if Labjack thread is enabled, disable it.
                            if relays_present:
                                relays_queue.put(('open',7))
                        elif genset_condition==1:
                            #Genset relay is enabled by sending a close_relay(7) to the relay module queue, and if Labjack thread is enabled, disable it.
                            if relays_present:
                                relays_queue.put(('close',7))
                        elif genset_condition==2:
                            #The monitor task of the labjack is enabled.
                            t6.start()


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

#Shutting down the gridsim
if gridsim_present==1:
    try:
        gridsim_queue.put('END')
    except:
        pass

if relays_present:
    try:
        #relay_module.open_all_module_relays()
        relays_queue.put('open_all')
    except:
        pass

#Synchronizing pulse with Yokogawa.
logging.info("")
logging.info('Synchronizing pulse')
logging.info("")

if relays_present:
    relays_queue.put(('close',8))
    time.sleep(15)
    relays_queue.put(('open',8))

logging.info(filename)
logging.info('Test completed')
test_done=True

logging.info('Formatting CSV outputs')

if edgepresent:
    try:
        dfqpigs=pd.read_excel('./'+filename+'/'+filename+'_EDGE_QPIGS.xlsx',header=[0])
        dfqpigs['Data']=dfqpigs['Data'].str.replace(r"b'\(",'')
        dfqpigs['Data']=dfqpigs['Data'].str.replace(r"""b"\(""",'')
        dfqpigs[['QPIGS_'+"{0:03d}".format(i) for i in range(1,24+1)]]=dfqpigs["Data"].str.split(" ", expand=True).iloc[:,:24]
        dfqpigs.to_csv('./'+filename+'/'+filename+'_EDGE_QPIGS.csv',header=True,index=False)
    except:
        pass

if lyra_present:
    try:
        dflcb=pd.read_excel('./'+filename+'/'+filename+'_LCB_data.xlsx',header=[0])
        dflcb['Data']=dflcb['Data'].str.replace("[",'').str.replace("]","")
        dflcb[['LCB_'+"{0:03d}".format(i) for i in range(1,18+1)]]=dflcb["Data"].str.split(",", expand=True).iloc[:,:18]
        dflcb.to_excel('./'+filename+'/'+filename+'_LCB_data.xlsx',header=True,index=False)
    except:
        pass

if gridsim_present:
    try:
        dfgrid=pd.read_excel('./'+filename+'/'+filename+'_General_data.xlsx',header=[0])
        dfgrid[['Grid_Sim V_'+"{0:02d}".format(i) for i in range(1,3+1)]]=dfgrid["GridSim V"].str.split(",", expand=True)
        dfgrid[['Grid_Sim I_'+"{0:02d}".format(i) for i in range(1,3+1)]]=dfgrid["GridSim I"].str.split(",", expand=True)
        dfgrid[['Grid_Sim Freq_'+"{0:02d}".format(i) for i in range(1,3+1)]]=dfgrid["GridSim Freq"].str.split(",", expand=True)
        dfgrid[['Grid_Sim P_'+"{0:02d}".format(i) for i in range(1,3+1)]]=dfgrid["GridSim P"].str.split(",", expand=True)
        dfgrid[['Grid_Sim Q_'+"{0:02d}".format(i) for i in range(1,3+1)]]=dfgrid["GridSim Q"].str.split(",", expand=True)
        dfgrid.to_excel('./'+filename+'/'+filename+'_General_data.xlsx',header=True,index=False)


    except:
        pass
