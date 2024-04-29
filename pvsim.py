from SCPI_interface import SCPI_interface
from datetime import datetime as dt
import os
import msvcrt, time

class pv_sim(SCPI_interface):

    def log(self):
        filename= 'PV_Logs-' + str(dt.now().strftime("%Y%m%d.%H%M"))
        #Create directory for test case.
        if not os.path.exists('./'+filename):
            os.mkdir('./'+filename)

        with open('./'+filename +'/'+self.ip+ ".csv", "a+") as f:
            f.write('time start,Voltage,Current')

            while True:
                self.query('System:Clear', False)
                f.write('\n' + str(dt.now())+',')
                f.write(self.query('Measure:Voltage?')+',')
                f.write(self.query('Measure:Current?'))
                if msvcrt.kbhit():
                    if msvcrt.getwche() == '\r':
                        break

def pv_sim_write(pv,o,v,a):
    try:
        pv.query('System:Clear', False)
    except Exception as e:
        print("Failed to clear PV's error queue")
        print(e)

    if(v not in str(pv.query('Voltage?'))): 
        try:
            pv.query('Voltage ' + v, False) 
        except Exception as e:
            print("Failed to change PV's voltage")
            print(e)
    if(v in str(pv.query('Voltage?'))):
        print("Successfully changed voltage to " + v)

    if(a not in str(pv.query('Current?'))): 
        try:
            pv.query('Current ' + a, False) 
        except Exception as e:
            print("Failed to change PV's current")
            print(e)
    if(a in str(pv.query('Current?'))):
        print("Successfully changed current to " + a)

    if(o not in str(pv.query('Output:State?'))): 
        try:
            pv.query('Output:State ' + o, False) 
        except Exception as e:
            print("Failed to change PV's output")
            print(e)
    if(o in str(pv.query('Output:State?'))):
        print("Successfully changed output to " + o)



def main():
    pv1=pv_sim('192.168.128.185', 30000, 'ITECH')
    pv1.connect()
    pv_sim_write(pv1, str(0), str(350), str(30))
    for i in range(0, 10):
        print("Error: " + str(pv1.query("SYST:ERR?")))
    pv1.query('System:Clear', False)
    pv1.close()
'''    print("'Source:FUNCTION:mode?': " + instrument.query('Source:FUNCTION:mode?'))
    print("'*CLS': " + instrument.query('*CLS', False))
    print("'Source:FUNCTION:Mode Fixed': " + instrument.query('Source:FUNCTION:Mode Fixed', False))
    print("'Voltage?': " + instrument.query('Voltage?'))
    print("'Voltage 350': " + instrument.query('Voltage 350', False))
    print("'Voltage?': " + instrument.query('Voltage?'))
    print("'Current?': " + instrument.query('Current?'))
    print("'Current 15': " + instrument.query('Current 15', False))
    print("'Current?': " + instrument.query('Current?'))
    print("'FETCH:CURRENT?': " + instrument.query('FETCH:CURRENT?'))
    print("'FETCH:VOLTAGE?': " + instrument.query('FETCH:VOLTAGE?'))
    print("'Measure:Current?': " + instrument.query('Measure:Current?'))
    print("'Measure:Voltage?': " + instrument.query('Measure:Voltage?'))
    print("'FETCH:CURRENT?': " + instrument.query('FETCH:CURRENT?'))
    print("'FETCH:VOLTAGE?': " + instrument.query('FETCH:VOLTAGE?'))
    print("'Output:State?': " + instrument.query('Output:State?'))
    print("'Output:State 1': " + instrument.query('Output:State 1', False))
    print("'Output:State?': " + instrument.query('Output:State?'))
    time.sleep(5)
    print("'FETCH:CURRENT?': " + instrument.query('FETCH:CURRENT?'))
    print("'FETCH:VOLTAGE?': " + instrument.query('FETCH:VOLTAGE?'))
    print("'Measure:Current?': " + instrument.query('Measure:Current?'))
    print("'Measure:Voltage?': " + instrument.query('Measure:Voltage?'))
    print("'FETCH:CURRENT?': " + instrument.query('FETCH:CURRENT?'))
    print("'FETCH:VOLTAGE?': " + instrument.query('FETCH:VOLTAGE?'))
    print("'Output:State 0': " + instrument.query('Output:State 0', False))
    print("'Output:State?': " + instrument.query('Output:State?'))
    time.sleep(5)
    print("'FETCH:CURRENT?': " + instrument.query('FETCH:CURRENT?'))
    print("'FETCH:VOLTAGE?': " + instrument.query('FETCH:VOLTAGE?'))
    print("'Measure:Current?': " + instrument.query('Measure:Current?'))
    print("'Measure:Vo ltage?': " + instrument.query('Measure:Voltage?'))
    print("'FETCH:CURRENT?': " + instrument.query('FETCH:CURRENT?'))
    print("'FETCH:VOLTAGE?': " + instrument.query('FETCH:VOLTAGE?'))'''

    

if __name__ == "__main__":
    main()