import pyvisa
import time

rm=pyvisa.ResourceManager()
resources=list(rm.list_resources())+['TCPIP::192.168.100.200::INSTR']
        
def select_instrument():
    """
   This function enumerates the different devices availables and returns a pyvisa client connected with the selected one, capable of query different SCPI commands.
   For further information, please review the Grid Simulator programming manual.

   For lab purposes, this is only used with the grid simulator. The object works with a query-based system from pyvisa, meaning that each query is a write-read action.

    Args:
        No arguments

    Kwargs:
        No Kwargs.

    Returns:
        A pyvisa client with the desired instrument to be used. 

    Raises:
        No raises.
        
    Example:
        >>>instrument=SCPI_interface.select_instrument()
        >>>instrument.query('PVOLtage A,230.0')
        >>>instrument.query('OUTP ON')

    """
    print('')
    print('')
    print('Resources availables')
    for i,dev in enumerate(resources,0):
        print(i,resources[i])
    selected_instrument=int(input('Input resource to connect:'))
    print('')
    print('')
##    if selected_instrument==0:
##        selected_instrument=str(input('Enter resource connection settings'))
##        print('Connecting to instrument ',selected_instrument)
##        instrument=rm.open_resource(selected_instrument)
##    else:
    print('Connecting to instrument ',resources[selected_instrument])
    instrument=rm.open_resource(resources[selected_instrument])
    print('')
    print('')
    print(r"""Please send commands in the following form: instrument.query('*IDN?')""")
    print(instrument.query('*IDN?'))
    return instrument
    
##
##value=input('Do you want to run the example routine (Blinking 230VAC LED)? 1=Yes, 0=No ')
##if value=='1':
##    #Set voltage reference to 230
##    print('Setting reference of Voltage for phase A as 230[V] and repeating blinking sequence x3')
##    time.sleep(1)
##    instrument.query('PVOLtage A,230.0')
##    for i in range(3):
##    #Turn on the grid
##        print('Turning Grid ON for 5[s]')
##        instrument.query('OUTP ON')
##        #Wait for 5 seconds
##        time.sleep(5)
##        #Turn of the grid.
##        print('Turning Grid OFF for 5[s]')
##        instrument.query('OUTP OFF')
##        time.sleep(5)
##    #instrument.close()
##else:
##    pass
#instrument.close()
