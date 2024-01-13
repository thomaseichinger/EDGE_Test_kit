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


# Step 1 Ask for configuration information
#Add try catch for failed and move on to next system, ifelse next timestamp
while True:
    for pcu_id in edge_pcu:
        #print(pcu_id + '\n')
        url = str('http://edge-'+str(pcu_id)+ ':4000/api/device/status')
        with open('./'+filename +'/'+pcu_id+ ".txt", "a+") as f:
            f.write("Started query "+ pcu_id + " at " + str(datetime.datetime.now())+'\n')
            resp = http1.request('GET', url)
            edge_status=[]
            edge_status.append(json.loads(resp.data))
            f.write("Finished querying " + pcu_id + " at " + str(datetime.datetime.now())+'\n')

            f.write('SOC: ' + str(edge_status[0]['data']['status']['general_status'][1]['battery_capacity'])+'\n')
            f.write('Input V: ' + str(edge_status[0]['data']['status']['general_status'][1]['grid_voltage'])+'\n')
            f.write('Input F: ' + str(edge_status[0]['data']['status']['general_status'][1]['grid_frequency'])+'\n')
            f.write('Output V: ' + str(edge_status[0]['data']['status']['general_status'][1]['ac_output_voltage'])+'\n')
            f.write('Output F: ' + str(edge_status[0]['data']['status']['general_status'][1]['ac_output_frequency'])+'\n')
            f.write('Output W: ' + str(edge_status[0]['data']['status']['general_status'][1]['ac_output_active_power'])+'\n')
            f.write('Input W: ' + str(edge_status[0]['data']['status']['general_status_2'][1]['ac_input_active_power'])+'\n')
            f.write('PV_Power: ' + str(edge_status[0]['data']['status']['general_status_2'][1]['pv_active_power'])+'\n')
            f.write('Battery Voltage: ' + str(edge_status[0]['data']['status']['general_status'][1]['battery_voltage'])+'\n')
            f.write('Battery Charge Current: ' + str(edge_status[0]['data']['status']['general_status'][1]['battery_charging_current'])+'\n')
            f.write('Heatsink Temp: ' + str(edge_status[0]['data']['status']['general_status'][1]['inverter_heat_sink_temp'])+'\n')
            f.write('Paygo Permanent Unlock: ' + str(edge_status[0]['data']['status']['paygo'][1]['permanent_unlock'])+'\n')
            f.write('Paygo Time Remaining: ' + str(edge_status[0]['data']['status']['paygo'][1]['time_remaining_s'])+'\n')
            f.write('Battery Float Voltage: ' + str(edge_status[0]['data']['status']['ratings'][1]['battery_float_voltage'])+'\n')
            f.write('Battery Bulk Voltage: ' + str(edge_status[0]['data']['status']['ratings'][1]['battery_bulk_voltage'])+'\n')

    time.sleep(1)
    if msvcrt.kbhit():
        if msvcrt.getwche() == '\r':
            break
    

# for i in PCU_index:
#     qpiri_data.append(edge_status[int(i)]['data']['status']['ratings'][1])
#     genctl_data.append(edge_genctl[int(i)]['data']['config'])
#     osp_data.append(edge_osp[int(i)]['data']['config'])