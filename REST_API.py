import urllib3
import json
import datetime
import os
from datetime import datetime as dt
import msvcrt, time


edge_pcu=['4000100158','4000100104','4000100323','4000100247','4000100142']


# These variables are used to store directly what's received through the ReST
# API
 
edge_status=[]  
edge_osp=[]
edge_genctl=[]

# These variables are used to extract some of the

genctl_data=[]
osp_data=[]
qpiri_data=[]


http1 = urllib3.PoolManager()


# ssh_key_file=open(ssh_key_path,"r")
# ssh_key1=ssh_key_file.read().rstrip()

filename= 'Edge_Systems_' + str(dt.now().strftime("%Y%m%d.%H%M%S"))
#Create directory for test case.
if not os.path.exists('./'+filename):
    os.mkdir('./'+filename)

for pcu_id in edge_pcu:
    with open('./'+filename +'/'+pcu_id+ ".csv", "a+") as f:
        f.write('time start,time end,SOC,Input V,Input F,Output V,Output F,Output W,Input W,PV_Power,Battery Voltage,Battery Charge Current,Heatsink Temp,Paygo Permanent Unlock,Paygo Time Remaining,Battery Float Voltage,load_port_state,Battery Bulk Voltage')

# Step 1 Ask for configuration information
#Add try catch for failed and move on to next system, ifelse next timestamp
while True:
    #time.sleep(1)
    
    for pcu_id in edge_pcu:
        #print(pcu_id + '\n')
        url = str('http://edge-'+str(pcu_id)+ ':4000/api/device/status')
        with open('./'+filename +'/'+pcu_id+ ".csv", "a+") as f:
            f.write('\n' + str(datetime.datetime.now())+',')
            try:
                resp = http1.request('GET', url)
            except Exception as e:
                print("Failed\n")
                print(e)
                f.write(str(datetime.datetime.now()))
            edge_status=[]
            try:
                edge_status.append(json.loads(resp.data))
                f.write(str(datetime.datetime.now()))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['battery_capacity']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['grid_voltage']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['grid_frequency']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['ac_output_voltage']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['ac_output_frequency']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['ac_output_active_power']))
                f.write(','+str(edge_status[0]['data']['status']['general_status_2'][1]['ac_input_active_power']))
                f.write(','+str(edge_status[0]['data']['status']['general_status_2'][1]['pv_active_power']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['battery_voltage']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['battery_charging_current']))
                f.write(','+str(edge_status[0]['data']['status']['general_status'][1]['inverter_heat_sink_temp']))
                f.write(','+str(edge_status[0]['data']['status']['paygo'][1]['permanent_unlock']))
                f.write(','+str(edge_status[0]['data']['status']['paygo'][1]['time_remaining_s']))
                f.write(','+str(edge_status[0]['data']['status']['ratings'][1]['battery_float_voltage']))
                f.write(','+str(edge_status[0]['data']['status']['ratings'][1]['load_port_state']))
                f.write(','+str(edge_status[0]['data']['status']['ratings'][1]['battery_bulk_voltage']))
            except Exception as e:
                print(e)
                for i in range(0,16):
                    f.write(',N/A')
    time.sleep(1)
    if msvcrt.kbhit():
        if msvcrt.getwche() == '\r':
            break


    

# for i in PCU_index:
#     qpiri_data.append(edge_status[int(i)]['data']['status']['ratings'][1])
#     genctl_data.append(edge_genctl[int(i)]['data']['config'])
#     osp_data.append(edge_osp[int(i)]['data']['config'])