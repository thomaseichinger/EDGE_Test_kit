import serial
import time
import re
from datetime import datetime, timezone
import pickle
from collections import defaultdict
import collections.abc
import csv
import argparse
import sys
import pandas as pd
import time
import numpy as np
from datetime import datetime, timezone, timedelta
import pickle
from functools import reduce
import warnings
import os
import serial.tools.list_ports as list_ports
import traceback
import time
warnings.filterwarnings('ignore')
#functions

TIME_STR = datetime.now().strftime("%m%d-%H%M")
MAX_RETRIES = 0

def separator(string):
    split_strings = []
    n  = 2
    for index in range(0, len(string), n):
        split_strings.append(string[index : index + n])
    return split_strings

def Parsing_INVMIN(data_list):
    try:
        parsed_data=[]
        
        #Voltage_Q5_in_V
        hex1,hex2=data_list[1],data_list[0]
        hex_out=np.uint16(int(hex1+hex2,16))
        parsed_data.append(hex_out/(2**5))
        
        #Power_Q4_in_W
        hex1,hex2=data_list[3],data_list[2]
        hex_out=np.int16(int(hex1+hex2,16))
        parsed_data.append(hex_out/(2**4))
        
        #Volt_Amps_r_Q4_in_VA
        hex1,hex2=data_list[5],data_list[4]
        hex_out=np.int16(int(hex1+hex2,16))
        parsed_data.append(hex_out/(2**4))
        
        #dc_voltage_q8_in_V
        hex1,hex2=data_list[7],data_list[6]
        hex_out=np.uint16(int(hex1+hex2,16))
        parsed_data.append(hex_out/(2**8))
        
        #dc_current_Q8_in_A
        hex1,hex2=data_list[9],data_list[8]
        hex_out=np.int16(int(hex1+hex2,16))
        parsed_data.append(hex_out/(2**8))
        
        #temperature_in_C
        parsed_data.append(np.int8(int(data_list[10],16)))
        
        #Inv_device_state
        parsed_data.append(np.uint8(int(data_list[11],16)))
        
        #sunspec_operating_state
        parsed_data.append(np.uint8(int(data_list[12],16)))
        
        #sunspec_event_mask
        hex1,hex2,hex3,hex4=data_list[13],data_list[14],data_list[15],data_list[16]
        parsed_data.append(np.uint32(int(hex1+hex2+hex3+hex4,16)))
        
        #sunspec_event_mask
        hex1,hex2,hex3,hex4=data_list[17],data_list[18],data_list[19],data_list[20]
        parsed_data.append(np.uint32(int(hex1+hex2+hex3+hex4,16)))
        
        parsed_data=[str(i) for i in parsed_data]
        return parsed_data
    except:
        print(data_list)
        raise

def Parsing_ENPRMA(data_list):
    try:
        parsed_data=[]
        
        #Battery ID
        min_tim_spent_closed=data_list[0]
        parsed_data.append(int(min_tim_spent_closed,16))
        
        #Remote Frequency Q8
        hex1,hex2=data_list[2],data_list[1]
        hex_out=int(hex1+hex2,16)
        parsed_data.append(hex_out/(2**8))
        
        #Remote rms v Q5
        hex1,hex2=data_list[4],data_list[3]
        hex_out=int(hex1+hex2,16)
        parsed_data.append(hex_out/(2**5))
        
        
        #CHECK THIS VALUE
        #CHECK THIS VALUE
        #CHECK THIS VALUE
        #MID active power Q0 in W
        hex1,hex2=data_list[6],data_list[5]
        hex_out=int(hex1+hex2,16)
        parsed_data.append(hex_out)
        
        #outlet_time_spent_closed_pct
        parsed_data.append(int(data_list[7],16))
        
        #terminal_time_spent_closed_pct
        parsed_data.append(int(data_list[8],16))
        
        #local_frequency_q8_in_HZ
        hex1,hex2=data_list[10],data_list[9]
        hex_out=int(hex1+hex2,16)
        parsed_data.append(hex_out/(2**8))
        
        #local_rms_q5_INV
        hex1,hex2=data_list[12],data_list[11]
        hex_out=int(hex1+hex2,16)
        parsed_data.append(hex_out/(2**5))
        
        #sum_inverter_pv_power_in_w
        hex1,hex2=data_list[14],data_list[13]
        hex_out=np.int16(int(hex1+hex2,16))
        parsed_data.append(hex_out)
        
        #number_of_active_pv_inverters
        parsed_data.append(int(data_list[15],16))
        
        #string_soc
        parsed_data.append(int(data_list[16],16))
        
        
        
        #CHECK THIS VALUE
        #CHECK THIS VALUE
        #CHECK THIS VALUE
        #sum_battery_power_in_w
        hex1,hex2=data_list[18],data_list[17]
        hex_out=np.int16(int(hex1+hex2,16))
        parsed_data.append(hex_out)
        
        #string_soc
        parsed_data.append(int(data_list[19],16))
        
       
        parsed_data=[str(i) for i in parsed_data]
        return parsed_data
    except:
        print(data_list)
        raise


def Parsing_BMUMIN(data_list):
    parsed_data=[]
    
    try:
        #Battery ID
        bat_id=data_list[0]
        parsed_data.append(int(bat_id,16))
        # print(bat_id)
        #Battery Voltages
        for i in range(1,11):
            vbat1,vbat2=data_list[i*2],data_list[i*2-1]
            vout=vbat1+vbat2
            hex_vbat=int(vout,16)
            # print(hex_vbat)
            parsed_data.append(hex_vbat)
        #Battery Balancing values
        for i in range(21,31):
            parsed_data.append(int(data_list[i],16))
            # print(int(data_list[i],16))
        #Temperatures
        for i in range(31,33):
            parsed_data.append(np.int8(int(data_list[i],16)))
            # print(int(data_list[i],16))
        #current_a_Q8
        for i in range(17,18):
            hex1,hex2=data_list[i*2],data_list[i*2-1]
            hexout=hex1+hex2
            hex_value=np.int16(int(hexout,16))/(2**8)
            # print(hex_value)
            parsed_data.append(hex_value)
        ##DC_bus_Voltage
        for i in range(18,19):
            hex1,hex2=data_list[i*2],data_list[i*2-1]
            hexout=hex1+hex2
            hex_value=int(hexout,16)
            # print(hex_value)
            parsed_data.append(hex_value)
        #SOC
        parsed_data.append(int(data_list[37],16))
    
        #Legacy data
        #DC current ma
        hex1,hex2=data_list[39],data_list[38]
        hex_value=int(hex1+hex2,16)
        parsed_data.append(hex_value)
        #DC voltage mv
        hex1,hex2=data_list[41],data_list[40]
        hex_value=int(hex1+hex2,16)
        parsed_data.append(hex_value)
        parsed_data=[str(i) for i in parsed_data]
        return parsed_data
    except:
        print(data_list)
        raise

class infinity_box:
    """Documentation for the Infinity Box CLI interface, does not include private methods of the class.
       
       Examples:
           >>>box=OOP_CLI_interface.infinity_box('COM17',3,4,156699089566)
    """
    
    def __init__(self,com_port,prov_set,power_set,key):
    

        #Default values are None until initialization.
        #Power state expected as an int. Error value is -1
        self.power_state=None
        #Provision state expected as an int. Error value is -1
        self.provision_state=None
        #Device, COMPORT are expected as int and str(?) respectively.
        self.dev=None
        self.comport=None
        #Bus attribute contains the serial bus.
        self.bus=None
        #Box type is a string: 'Primary' or 'Secondary'
        self.boxtype=None
        #invs_sn is expected to be a list with box SN.
        self.invs_sn=None
        
        
        #Focus the data handling on these attributes.
        
        #MID status is expected to be a string with 'Closed' or 'Opened' value. Error value: "No Information"
        self.mid_status=None
        
        #SOC is an int between 0 and 100. Error value: -1
        self.soc=None
        
        #MID information is a list of data 
        self.mid_information=None
        
        #Local voltage and frequency and remote voltage and frequency are float values. Error values: None
        self.local_voltage=None
        self.remote_voltage=None
        self.local_freq=None
        self.remote_freq=None
        
        #LP statuses, as booleans. Error values: None
        self.lp_high=False
        self.lp_low=False
        
        #Values as floats. Error values: -1
        self.pack_voltage,self.pack_current,self.row_voltages=None,None,None
        
        
        
        #Unlock key is an int value provided by NXT Lovelace.
        self.unlock_key=key
        #Box inverters as dictionary
        self.box_inv=None
        #Fan state as int
        self.fans_states=None
        #Create connection
        self._comport(com_port)
        #Unlock the box
        self.unlock_box()

        #Turn on EAC or prov/power state.
        if prov_set!=self.provision_state:
            self.query('prov-set '+str(prov_set))
        if power_set!=self.power_state:
            self.query('power-set '+str(power_set))
            #Wait for the EAC to turn on.
            time.sleep(2)


            
    def BMUMIN_minute_records(self,seconds_to_fetch):
        """
        This method retrieves the last seconds_to_fetch seconds and parses them into a csv file.

        Args:
            seconds_to_fetch: Number of seconds to retrieve for the BMUMIN minute records.

        Kwargs:
            No Kwargs.

        Returns:
            A Dataframe with the minute records. Also a csv file with this df is created at the code execution location.

        Raises:
            No raises.

        Examples:
            >>>infinity_box.BMUMIN_minute_records(3600)
        """
        if not os.path.exists('./Export'):
            os.mkdir('./Export')
        prep=False
        try:
            self.write('cd ..')
            registers=['ENPRMA_DL','BMUMIN_DL','INVMIN_DL','EVENT_DL','DCMIN_DL']
            self.write('cd '+registers[1])
            data=self.query('ls')
            n_records=int(data.split('\n')[1].split('|')[2])

            time_data=self.query('time-get')
            box_time=int(time_data.split('\n')[1].split('|')[2])
            desired_time=seconds_to_fetch
            read_timestamp=box_time-desired_time
            #print(box_time,int(box_time),desired_time,read_timestamp)
            prep=True
            #print('Prep Successful')
        except:
            pass
            #print('Preparation failed')
        
        if prep==True:
            try:
                print('Getting BMU records since ',read_timestamp)
                #print('1667396040')
                #print(str(read_timestamp))
                self.write('read '+str(read_timestamp))
                self.bus.flushInput()
                time.sleep(max(3,min(10*seconds_to_fetch/3600,45)))
                data=''
                while 1:
                    tdata=self.bus.readline()
                    data_left=self.bus.inWaiting()
                    #print(tdata,data_left)
                    if len(tdata)>50:
                        data+=tdata.decode()
                        #print(tdata.decode())
                    #time.sleep(1)
                    if data_left==0:
                        break

                decoded_data=data.split('\n')[1:]
                #print(decoded_data)
                df=pd.DataFrame(columns=['timestamp','data'])
                for x in decoded_data:
                    try:
                        df.loc[len(df)+1]=[int(x.split('\t\t')[0][:-1]),x.split('\t\t')[1]]
                    except:
                        pass
                
                from datetime import datetime
                #Filtering data
                df=df[df.data.apply(lambda x: len(str(x))==84)]
                #Reset the index:
                df.reset_index(inplace=True,drop=True)
                #print(df)
                #Local time
                df['local_time']=df['timestamp'].apply(datetime.fromtimestamp)
                #return df
                #Spliting Data
                df['data list']=df['data'].apply(separator)
                #Parsing data
                df['parsed data']=df['data list'].apply(Parsing_BMUMIN)
                ###Data list to columns
                #Data to df
                extra_columns=['Battery_ID']+['Voltage_'+str(i) for i in range(1,11)]+['Balancing'+str(i) for i in range(1,11)]+['Temp_1','Temp_2','Current_a_q8','DC_bus_voltage','SOC','DC_out_current_ma','dc_out_voltage_mv']
                #parsed_df=pd.DataFrame(df["parsed data"].to_list(), columns=['data_'+str(i) for i in range(len(df['parsed data'][1]))])
                parsed_df=pd.DataFrame(df["parsed data"].to_list(), columns=extra_columns)
                #Join parsed df with the previous one
                final_df=df.join(parsed_df)

                #Droping previous splitted data
                final_df.drop('data list',axis=1,inplace=True)
                final_df.drop('parsed data',axis=1,inplace=True)
                print('Exporting')
                #Export
                final_df.to_csv('./Export/'+str(self.comport)+'_Parsed_BMUMIN_Records.csv',header=True,index=False)
                return final_df
            except Exception as e:
                print('Not able to retrieve records')
                print(e)
                return df
        else:
            print('Not able to retrieve records')
            return None
        
    def INVMIN_minute_records(self,seconds_to_fetch):
        if not os.path.exists('./Export'):
            os.mkdir('./Export')
        prep=False
        try:
            self.write('cd ..')
            registers=['ENPRMA_DL','BMUMIN_DL','INVMIN_DL','EVENT_DL','DCMIN_DL']
            self.write('cd '+registers[2])
            data=self.query('ls')
            n_records=int(data.split('\n')[1].split('|')[2])

            time_data=self.query('time-get')
            box_time=int(time_data.split('\n')[1].split('|')[2])
            desired_time=seconds_to_fetch
            read_timestamp=box_time-desired_time
            #print(box_time,int(box_time),desired_time,read_timestamp)
            prep=True
            #print('Prep Successful')
        except:
            #print('Preparation failed')
            pass
        
        if prep==True:
            try:
                print('Getting INVMIN records since ',read_timestamp)
                #print('1667396040')
                #print(str(read_timestamp))
                self.write('read '+str(read_timestamp))
                self.bus.flushInput()
                time.sleep(max(3,min(10*seconds_to_fetch/3600,45)))
                data=''
                while 1:
                    tdata=self.bus.readline()
                    data_left=self.bus.inWaiting()
                    #print(tdata,data_left)
                    if len(tdata)>50:
                        data+=tdata.decode()
                        #print(tdata.decode())
                    #time.sleep(1)
                    if data_left==0:
                        break

                decoded_data=data.split('\n')[1:]
                #print(decoded_data)
                df=pd.DataFrame(columns=['timestamp','data'])
                for x in decoded_data:
                    try:
                        df.loc[len(df)+1]=[int(x.split('\t\t')[0][:-1]),x.split('\t\t')[1]]
                    except:
                        pass
                
                from datetime import datetime
                #Filtering data
                df=df[df.data.apply(lambda x: len(str(x))==54)]
                #Reset the index:
                df.reset_index(inplace=True,drop=True)
                #print(df)
                #Local time
                df['local_time']=df['timestamp'].apply(datetime.fromtimestamp)
                #return df
                #Spliting Data
                df['data list']=df['data'].apply(separator)
                #Parsing data
                df['parsed data']=df['data list'].apply(Parsing_INVMIN)
                ###Data list to columns
                #Data to df
                extra_columns=['Voltage_Q5_in_V','Power_Q4_in_W','Volt_Amps_r_Q4_in_VA','dc_voltage_q8_in_V','dc_current_Q8_in_A','temperature_in_C','Inv_device_state','sunspec_operating_state','sunspec_event_mask','sunspec_event_mask']
                parsed_df=pd.DataFrame(df["parsed data"].to_list(), columns=extra_columns)
                #parsed_df=pd.DataFrame(df["parsed data"].to_list(), columns=['data_'+str(i) for i in range(len(df['parsed data'][1]))])
                #Join parsed df with the previous one
                final_df=df.join(parsed_df)

                #Droping previous splitted data
                final_df.drop('data list',axis=1,inplace=True)
                final_df.drop('parsed data',axis=1,inplace=True)
                print('Exporting')
                #Export
                final_df.to_csv('./Export/'+str(self.comport)+'_Parsed_INVMIN_Records.csv',header=True,index=False)
                return final_df
            except Exception as e:
                print('Not able to retrieve records')
                print(e)
                return df
        else:
            print('Not able to retrieve records')
            return None

    def EVENT_minute_records(self,seconds_to_fetch):
        if not os.path.exists('./Export'):
            os.mkdir('./Export')
        prep=False
        try:
            self.write('cd ..')
            registers=['ENPRMA_DL','BMUMIN_DL','INVMIN_DL','EVENT_DL','DCMIN_DL']
            self.write('cd '+registers[3])
            data=self.query('ls')
            n_records=int(data.split('\n')[1].split('|')[2])

            time_data=self.query('time-get')
            box_time=int(time_data.split('\n')[1].split('|')[2])
            desired_time=seconds_to_fetch
            read_timestamp=box_time-desired_time
            #print(box_time,int(box_time),desired_time,read_timestamp)
            prep=True
            #print('Prep Successful')
        except:
            pass
            #print('Preparation failed')
        
        if prep==True:
            print('Getting Event records since ',read_timestamp)
            #print('1667396040')
            #print(str(read_timestamp))
            self.write('read '+str(read_timestamp))
            self.bus.flushInput()
            time.sleep(max(3,min(10*seconds_to_fetch/3600,45)))
            data=''
            while 1:
                tdata=self.bus.readline()
                data_left=self.bus.inWaiting()
                #print(tdata,data_left)
                if len(tdata)>50:
                    data+=tdata.decode()
                    #print(tdata.decode())
                #time.sleep(1)
                if data_left==0:
                    break

            decoded_data=data.split('\n')
            df=pd.DataFrame(columns=['timestamp','data'])
            for x in decoded_data:
                try:
                    df.loc[len(df)+1]=[int(x.split('\t\t')[0][:-1]),x.split('\t\t')[1]]
                except:
                    pass
            print('Exporting')
            df.to_csv('./Export/'+str(self.comport)+'_EVENTS_Records.csv',header=True,index=False)
            return df
        else:
            print('Not able to retrieve records')
            return None
        
    def GRID_minute_records(self,seconds_to_fetch):
        if not os.path.exists('./Export'):
            os.mkdir('./Export')
        prep=False
        try:
            self.write('cd ..')
            registers=['GRDMIN_DL']
            self.write('cd '+registers[0])
            data=self.query('ls')
            n_records=int(data.split('\n')[1].split('|')[2])
            time_data=self.query('time-get')
            box_time=int(time_data.split('\n')[1].split('|')[2])
            desired_time=seconds_to_fetch
            read_timestamp=box_time-desired_time
            #print(box_time,int(box_time),desired_time,read_timestamp)
            prep=True
            #print('Prep Successful')
        except:
            pass
            #print('Preparation failed')
        
        if prep==True:
            print('Getting GRID records since ',read_timestamp)
            #print('1667396040')
            #print(str(read_timestamp))
            self.write('read '+str(read_timestamp))
            self.bus.flushInput()
            time.sleep(max(3,min(10*seconds_to_fetch/3600,45)))
            data=''
            while 1:
                tdata=self.bus.readline()
                data_left=self.bus.inWaiting()
                #print(tdata,data_left)
                if len(tdata)>50:
                    data+=tdata.decode()
                    #print(tdata.decode())
                #time.sleep(1)
                if data_left==0:
                    break

            decoded_data=data.split('\n')[1:]
            #print(decoded_data)
            df=pd.DataFrame(columns=['timestamp','data'])
            for x in decoded_data:
                try:
                    df.loc[len(df)+1]=[int(x.split('\t\t')[0][:-1]),x.split('\t\t')[1]]
                except:
                    pass
            print('Exporting')
            df.to_csv('./Export/'+str(self.comport)+'_GRID_Records.csv',header=True,index=False)
            return df
        else:
            print('Not able to retrieve records')
            return None
        
    def ENPRMA_minute_records(self,seconds_to_fetch):
        if not os.path.exists('./Export'):
            os.mkdir('./Export')
        prep=False
        try:
            self.write('cd ..')
            registers=['ENPRMA_DL']
            self.write('cd '+registers[0])
            data=self.query('ls')
            n_records=int(data.split('\n')[1].split('|')[2])

            time_data=self.query('time-get')
            box_time=int(time_data.split('\n')[1].split('|')[2])
            desired_time=seconds_to_fetch
            read_timestamp=box_time-desired_time
            #print(box_time,int(box_time),desired_time,read_timestamp)
            prep=True
            #print('Prep Successful')
        except:
            pass
            #print('Preparation failed')
        
        if prep==True:
            try:
                print('Getting ENPRMA records since ',read_timestamp)
                #print('1667396040')
                #print(str(read_timestamp))
                self.write('read '+str(read_timestamp))
                self.bus.flushInput()
                time.sleep(max(3,min(10*seconds_to_fetch/3600,45)))
                data=''
                while 1:
                    tdata=self.bus.readline()
                    data_left=self.bus.inWaiting()
                    #print(tdata,data_left)
                    if len(tdata)>50:
                        data+=tdata.decode()
                        #print(tdata.decode())
                    #time.sleep(1)
                    if data_left==0:
                        break

                decoded_data=data.split('\n')[1:]
                #print(decoded_data)
                df=pd.DataFrame(columns=['timestamp','data'])
                for x in decoded_data:
                    try:
                        df.loc[len(df)+1]=[int(x.split('\t\t')[0][:-1]),x.split('\t\t')[1]]
                    except:
                        pass
                
                from datetime import datetime
                #Filtering data
                df=df[df.data.apply(lambda x: len(str(x))==40)]
                #Reset the index:
                df.reset_index(inplace=True,drop=True)
                #print(df)
                #Local time
                df['local_time']=df['timestamp'].apply(datetime.fromtimestamp)
                #return df
                #Spliting Data
                df['data list']=df['data'].apply(separator)
                #Parsing data
                df['parsed data']=df['data list'].apply(Parsing_ENPRMA)
                ###Data list to columns
                #Data to df
                extra_columns=['mid_tim_spent_closed_pct','remote_frequency_Q8_in_HZ','remote_rms_Q5_in_V','mid_active_power_Q0_in_W','oulet_time_spent_closed_pct','terminal_time_spent_closed_pct','local_frequency_Q8_in_HZ','local_rms_Q5_in_V','sum_inverter_pv_power_in_w','number_of_active_pv_inverters','string_soc','sum_battery_power_in_w','number_batteries']
                parsed_df=pd.DataFrame(df["parsed data"].to_list(), columns=extra_columns)
                #parsed_df=pd.DataFrame(df["parsed data"].to_list(), columns=['data_'+str(i) for i in range(len(df['parsed data'][1]))])
                #Join parsed df with the previous one
                final_df=df.join(parsed_df)

                #Droping previous splitted data
                final_df.drop('data list',axis=1,inplace=True)
                final_df.drop('parsed data',axis=1,inplace=True)
                print('Exporting')
                #Export
                final_df.to_csv('./Export/'+str(self.comport)+'_Parsed_ENPRMA_Records.csv',header=True,index=False)
                return final_df
            except Exception as e:
                print('Not able to retrieve records')
                print(e)
                return df
        else:
            print('Not able to retrieve records')
            return None


        
            
    def box_inverters(self):
        data=self.query('cfg-list').split("\n")
        nboxes=int([(x,data.index(x)) for x in data if 'number of boxes in volta string' in x.lower()][0][0].split('|')[2])
        index=[(x,data.index(x)) for x in data if 'number of boxes in volta string' in x.lower()][0][1]
        inv_sns=[data[index:][2+i*5:6+i*5] for i in range(nboxes)]
        box_inv={}
        for box in inv_sns:
            invs=[x.split('|')[1] for x in box]
            sns=[x.split('|')[2] for x in box]
            box_inv.update(dict(map(lambda i,j : (i,j) , invs,sns)))
        self.box_inv=box_inv
        #Number of boxes in Volta string#
        
    def update_stats(self):
        if self.boxtype=='Primary':
            try:
                self.mid_state()
                self.mid_info()
                self.local_measurements()
                self._soc()
                self.inv_sn()
                self.box_inverters()
                self.lp()
            except:
                print('Error while updating stats, make sure EAC is on')
                
        if self.boxtype=='Secondary':
            try:
                self.mid_status='None'
                self.mid_information='None'
                self._soc()
            except:
                print('Error while updating stats')
        
    def _comport(self,com_port):
        try:
            ports=[(x.device,list_ports.comports().index(x),x) for x in list_ports.comports()]
            self.dev=[x for x in ports if x[0]==com_port][0][1]
            self.comport=[x for x in ports if x[0]==com_port][0][0]
            self.create_connection()
        except Exception as e:
            print (e)
            raise

    def comm_error_handling(self):
        try:
            self.bus.close()
            self._comport()
        except:
            print('Not able to regain comms')
            pass
        
    def select_comport(self):
        #COMPort recognition and selection block.
        comports = list_ports.comports()
        print('Available devices: ')
        for i,dev in enumerate(comports,1):
            print(i,dev.description)
        dev= int(input("Enter device , Ex: 1 #:  "))-1
        self.dev=dev
        port=comports[dev].device
        self.comport=port
        
    def create_connection(self):
        comports = list_ports.comports()
##        print('Trying to pull data from ' + comports[self.dev].device,'\n')
        try:
            self.bus = serial.Serial(self.comport, timeout=1,baudrate=921600)
            if self.bus.isOpen():
                print('Connection succesfull with ' + comports[self.dev].device,'\n')
            try:
                numretries=3
                #While not able to identify the box
                while numretries>0:
                    boxtype=self.query('cfg-list').split('\n')[1].split('|')[2]
                    #If the boxtype is not primary or secondary, we try again.
                    if boxtype!='Primary' and boxtype!='Secondary':
                        boxtype=self.query('cfg-list').split('\n')[1].split('|')[2]
                        numretries-=1
                    #If it's primary or secondary we asign it to the box and break out of the loop.
                    else:
                        self.boxtype=boxtype
                        break
                if numretries==0:
                    print('Error while trying to stablish connection with the box.')
                else:
                    print('Box type succesfully identified')
            except:
                print('Not able to identify box type, please do it manually or unlock the box')
        except Exception as e:
            print(e)
            print('Failed to create connection with the box')
        
    def query(self,cmd):
        num_retries=3
        while num_retries>0:
            try:
                self.bus.flushInput()
                self.bus.write((cmd + chr(10)).encode())
                time.sleep(0.1)
                output=self.reader()
                #print(output)
                return output
            except Exception as e:
                num_retries-=1
                print('Not able to retrieve data, retrying')
                print(e)
                pass

        return None
    def _fans_states(self):
        try:
            data=self.query('thermal-fan-state')
            self.fans_states=data.split('\n')[1].split('|')[2]
            return self.fans_states
        except Exception as e:
            print(e)
            pass
        
    def write(self,cmd):
        self.bus.write((cmd + chr(10)).encode())
        time.sleep(0.1)

##    def reader(self):
##        # high speed serial reader to handle log output
##        raw =''
##        prev_str=''
##        flag = True
##        safecount = 1
##        try:
##            while flag:
##                data = str(self.bus.readline().decode())
##                if 'CTRL>' in data:
##                    raw+=data
##                    if self.bus.in_waiting==0:
##                        flag=True
##                        self.bus.flushInput()
##                        break
##                else:
##                    raw+=data
##                    prev_str=data
##                    if prev_str=="b''":
##                        safecount+=1
##                    if safecount==3:
##                        break
##                        
##        except serial.SerialException:
##            pass
##        self.bus.flushInput()
##        return raw
        
    
#Reader function
    def reader(self):
        # high speed serial reader to handle log output
        raw = b''
        flag = True
        count = 0
        try:
            while flag:
                data = self.bus.read(self.bus.in_waiting or 1)
                if data:
                    raw += data
                    if raw.endswith(b'CTRL>'):
                        if self.bus.in_waiting == 0:
                            flag = False
                else:
                    print('Trying to read buffer again. Hang in there.')
                    time.sleep(1)
                    count += 1
                    if count > MAX_RETRIES:
                        #sys.exit('USB comms failed, please retry')
                        print('USB comms failed at unit '+str(self.comport)+', please retry')
                        #print(raw.decode())
                        #print(data.decode())
                        flag=False
                        pass
                        
        except serial.SerialException:
            return None
        return raw.decode()


    def inv_sn(self):
        try:
            self.bus.flushInput()
            ########Data acquisition#########
            ########Data acquisition#########
            #eac-grid-data command brings the information associated to measured values.
            #_write(inf_interface, 'cli-unlock')
            self.bus.flushInput()
            self.write('eac-list')
            grid_data=self.reader()
            #print(grid_data)
            data=grid_data.split("\n")
            #Get number of inverters
            n_inverters=int(re.findall('[0-9]+', data[2])[0])
            #Get serial numbers of the inverters
            dicc_inverters={}
            inv_sns=[]
            for i in range(n_inverters):
                info=data[3+i].split(",")
                inverter=info[0][1:]
                inv_SN=info[2].split("|")[1]
                inv_sns.append(inv_SN)
                dicc_inverters.update({i:inv_SN})
            self.invs_sn=inv_sns
            return inv_sns
            #inv_sns= ['12 19 11 04 06 02', '12 19 11 04 05 90', '12 19 11 04 59 85', '12 19 11 04 08 41']

        except Exception as e:
            print('Error retrieving SN numbers, make sure EAC is ON.',e)
            pass

    def check_inv_state(self):
        #Default n_inverters
        n_inverters=5
        try:
            if self.invs_sn!=None:
                n_inverters=len(self.invs_sn)
            inv_data_dicc={}
            for i in range(len(self.invs_sn)):
                try:
                    sn=self.invs_sn[i]
                    self.write('eac-inv-data '+sn)
                    inv_data=self.reader().split('\n')
                    inv_state=[int(i) for i in inv_data[5].split('|')[2].split(',')]
                    inv_data_dicc.update({sn:inv_state})
                except:
                    pass
            return inv_data_dicc
            #inv_data_dicc= {0: [5, 3], 1: [5, 3], 2: [5, 3], 3: [5, 3]}

        except Exception as e:
            print('Error executing the request.',e)
            output_dicc={}
            for i in range(n_inverters):
                output_dicc.update({i:['-','-']})
            return output_dicc

    def bq_check(self):
        #Possible values:
        ##pack_voltage=33104; pack_current=-3316; row_voltages=[3309, 3310, 3312, 3311, 3311, 3311, 3312, 3308, 3310, 3307]
        ##-1 on each value, as error handling value.
        try:
            self.bus.flushInput()
            data=self.query('bq-check').split("\n")
            pack_voltage=int(re.findall('[0-9]+',data[14])[0])
            pack_current=[int(x) for x in re.findall(r"([\d-]*\d+)", data[17])][0]
            row_voltages=[int(re.findall('[0-9]+',x)[1]) for x in data[4:14]]
            self.pack_voltage,self.pack_current,self.row_voltages=pack_voltage,pack_current,row_voltages
            #print(pack_voltage,pack_current,row_voltages)


            ##pack_voltage=33104; pack_current=-3316; row_voltages=[3309, 3310, 3312, 3311, 3311, 3311, 3312, 3308, 3310, 3307]
            return self.pack_voltage,self.pack_current,self.row_voltages
        except Exception as e:
            print(e)
            self.pack_voltage,self.pack_current,self.row_voltages=-1,-1,[-1]*10
            return self.pack_voltage,self.pack_current,self.row_voltages

    def _soc(self):
        #Possible values: int value between 0 and 100, and -1 (Error value).
        try:
            grid_data=self.query('state-get')
            data=grid_data.split("\n")
            self.soc=int(data[3].split('|')[2].split(',')[3])
            return int(data[3].split('|')[2].split(',')[3])
        except Exception as e:
            print('Error with box '+str(self.comport))
            print('COMMS ISSUE - Probably - Cannot retrieve data')
            print(e)
            return -1
    
    def mid_state(self):
        #Possible values: "Closed", "Opened", "No Information".
        try:
            grid_data=self.query('eac-grid-data')
            #grid_data=self.reader()
            # [Hazem] Added printout to debug COMPORT failure in some instances.
            #print(grid_data)
            self.mid_status=grid_data.split('\n')[2].split('|')[2]
            return self.mid_status
        except:
            #Check provision state three times, otherwise comms error.
            try:
                print('Trying to check powerstatus')
                self.state_get()
                #Prov states where EAC is off
                if self.provision_state in [1]:
                    print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                    print('EAC ISSUE - Probably off - Prov set '+str(self.provision_state))
                #Power states where EAC is off
                if self.power_state in [0,1,2]:
                    print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                    print('EAC ISSUE - Probably off - Prov set '+str(self.power_state))
                
            except:
                print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                print('EAC ISSUE - Probably off - Not information available, check COMMS')
                self.mid_status='No Information'
                return self.mid_status
            


    def mid_info(self):
        #Expected values:
        try:
            grid_data=self.query('eac-grid-data')
            #grid_data=self.reader()
            keys=grid_data.split('\n')[4][1:-1].split('|')[0].split(',')
            factors = [re.findall(r'(?:\d+[a-zA-Z]+|[a-zA-Z]+\d+)', keys[i])[0] for i in range(len(keys))]
            values=grid_data.split('\n')[4][1:-1].split('|')[1].split(',')
            values=list(map(lambda x, y: int(y)/2**int(x[1:]), factors, values))
            mid_information = dict(map(lambda i,j : (i,j) , keys,values))
            self.mid_information=mid_information
            return self.mid_information

        except:
            #Check provision state three times, otherwise comms error.
            try:
                print('Trying to check powerstatus')
                self.state_get()
                #Prov states where EAC is off
                if self.provision_state in [1]:
                    print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                    print('EAC ISSUE - Probably off - Prov set '+str(self.provision_state))
                #Power states where EAC is off
                if self.power_state in [0,1,2]:
                    print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                    print('EAC ISSUE - Probably off - Prov set '+str(self.power_state))
                
            except:
                print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                print('EAC ISSUE - Probably off - Not information available, check COMMS')
                self.mid_status='No Information'
                return self.mid_status
    
    
    def state_get(self):
        try:
            data=self.query('state-get')
            self.power_state=int(re.findall('[0-9]+',data.split('\n')[1].split('|')[2].split(',')[0])[0])
            self.provision_state=int(re.findall('[0-9]+',data.split('\n')[2].split('|')[2].split(',')[0])[0])
            return self.provision_state,self.power_state
        except:
            return -1,-1

    def local_measurements(self):
        try:
            grid_data=self.query('eac-grid-data')
            keys=grid_data.split('\n')[3][1:-1].split('|')[0].split(',')
            factors = [re.findall(r'(?:\d+[a-zA-Z]+|[a-zA-Z]+\d+)', keys[i])[0] for i in range(len(keys))]
            values=grid_data.split('\n')[3][1:-1].split('|')[1].split(',')
            values=list(map(lambda x, y: int(y)/2**int(x[1:]), factors, values))
            local_info = dict(map(lambda i,j : (i,j) , keys,values))
            self.local_voltage=local_info['local_rms_Q5_in_V']
            self.local_freq=local_info['local_freq_Q24_in_Hz']
            if self.mid_state()=='Closed':
                self.remote_voltage=local_info['local_rms_Q5_in_V']
                self.remote_freq=local_info['local_freq_Q24_in_Hz']
            elif self.mid_state()=='Opened':
                self.remote_voltage=0
                self.remote_freq=0
            return local_info
        #If not possible to retrieve data regarding local voltage or freq, then values are None.
        except Exception as e:
            print(e)
            #Check provision state three times, otherwise comms error.
            try:
                print('Trying to check powerstatus')
                self.state_get()
                #Prov states where EAC is off
                if self.provision_state in [1]:
                    print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                    print('EAC ISSUE - Probably off - Prov set '+str(self.provision_state))
                #Power states where EAC is off
                if self.power_state in [0,1,2]:
                    print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                    print('EAC ISSUE - Probably off - Prov set '+str(self.power_state))
                
            except:
                print('EAC ISSUE - Probably off - Cannot retrieve EAC-GRID-DATA')
                print('EAC ISSUE - Probably off - Not information available, check COMMS')
                self.local_voltage=None
                self.local_freq=None
                self.remote_voltage=None
                self.remote_freq=None
                return None

        
    def lp(self):
        data=self.query('lp-en')
        
        #Try to get information for the high priority load port.
        try:
            if 'opened' in data.split('\n')[2]:
                self.lp_high=False
            elif 'closed' in data.split('\n')[2]:
                self.lp_high=True
        except Exception as e:
            print(e)
            self.lp_high=None

        #Try to get information for the low priority load port.
        try:
            if 'opened' in data.split('\n')[3]:
                self.lp_low=False
            elif 'closed' in data.split('\n')[3]:
                self.lp_low=True
        except Exception as e:
            print(e)
            self.lp_low=None
            
        #Return both load port values.
        return self.lp_low,self.lp_high

    def unlock_box(self):
        self.query('unlock '+str(self.unlock_key))
        
        
    def reboot(self):
        self.query('reboot')
        time.sleep(30)
        self.create_connection()
        
    def Get_Minute_Records(self,Time):
        if not os.path.exists('./Export'):
            os.mkdir('./Export')
        self.update_stats()
        if self.boxtype=='Primary':
            self.ENPRMA_minute_records(Time)
            self.BMUMIN_minute_records(Time)
            self.INVMIN_minute_records(Time)
            self.GRID_minute_records(Time)
            self.EVENT_minute_records(Time)
        if self.boxtype=='Secondary':
            self.BMUMIN_minute_records(Time)
            self.EVENT_minute_records(Time)

    def AGC(self,vsetpoint,fsetpoint,timeout):
        ia_off,ir_off=self.calculate_interties(vsetpoint,fsetpoint)
        self.query('intertie-offset '+str(ia_off)+' '+str(ir_off)+' '+str(timeout))
        
    def calculate_interties(self,target_v,target_f):
        self.local_measurements()
        meas_v=self.local_voltage
        meas_f=self.local_freq
        num_inverters=12
        nom_current=num_inverters*1.42
        gain=2
        G_per_PCU_list="0.175000000000000 -0.175000000000000;8.40000000000000 8.40000000000000]"
        G_per_PCU = np.matrix(G_per_PCU_list)
        Y=np.linalg.inv(G_per_PCU)*num_inverters;
        fV_err=np.transpose(np.array([(target_f-meas_f),(target_v-meas_v)]))
        print('Errors f,v: ',(target_f-meas_f),(target_v-meas_v))
        value=gain*np.matmul(Y,np.transpose(fV_err))
        ia,ir=value[0].item(0),value[0].item(1)
        return round(ia/nom_current*100,2),round(ir/nom_current*100,2)



    def export_variables(self):
        if self.boxtype=='Primary':
            #Update power_state,provision_state
            try:
                self.state_get()
            except:
                pass
            #Update invs_sn
            try:
                self.inv_sn()
            except:
                pass
            
            #Update mid_status
            try:
                self.mid_state()
            except:
                pass
            
            #Update SOC
            try:
                self._soc()
            except:
                pass
            
            #Update MID Information
            try:
                self.mid_info()
            except:
                pass
            
            #Update local measurements
            try:
                self.local_measurements()
            except:
                pass
            
            #Update box inverters
            try:
                self.box_inverters()
            except:
                pass
            
            #Update load port
            try:
                self.lp()
            except:
                pass
            
            #Update pack voltage, pack current and row voltages with BQ Check
            try:
                self.bq_check()
            except:
                pass
            
            try:
                return self.power_state,self.provision_state,self.boxtype,self.invs_sn,self.mid_status,self.soc,self.mid_information,self.local_voltage,self.remote_voltage,self.local_freq,self.remote_freq,self.box_inv,self.lp_low,self.lp_high,self.pack_voltage,self.pack_current,self.row_voltages
            except:
                print('Problem exporting variables, some values are not possible to update.')
                pass
            
        elif self.boxtype=='Secondary':
            print('Not Implemented yet')
            
##
##box1=infinity_box('COM12',3,4,156999076589)
##box1.mid_state()
####box1.query('bq-check')
##box1.update_stats()
##
##box2=infinity_box('COM12',3,4,156799036450)
##box2.update_stats()
##
##boxes=[box1,box2]
##while True:
##    for box in boxes:
##        print(box.comport)
##        box.AGC(227,50,60)

#box1.AGC(230,50,2)
##box2=infinity_box('COM23',3,4,156699048387)
##box2.update_stats()
##box3=infinity_box('COM8',3,4,156699048387)
##box3.update_stats()
##boxes=[box1,box2,box3]
##
##for box in boxes:
##    box.query('time-set '+str(int(time.time())))
##    print(box.query('time-get'))
    
##box1.ENPRMA_minute_records(3600*8)
##time.sleep(3)
##
##while True:
##    init_time=time.time()
##    print('')
##    print('-')
##    print(box1.export_variables())
##    print('Execution Time',time.time()-init_time)
##    print('-')
##    print('')
##    
##box1.Get_Minute_Records(3600*24)
##box2=infinity_box('COM12',3,4,156699089566)
##box2.Get_Minute_Records(3600*24)
##box3=infinity_box('COM13',3,4,156699089828)
##box3.Get_Minute_Records(3600*24)

##box1.update_stats()
    ##box1.check_inv_state()
##box1._comport('COM11')
##box2=infinity_box()
##box2._comport('COM12')
##box3=infinity_box()
##box3._comport('COM13')

##box1.update_stats()
##box2.update_stats()
##box3.update_stats()
##box1.box_inverters()
##print(box1.box_inv)
####box.select_comport()
##print(box.bq_check())
##print(box.inv_sn())
