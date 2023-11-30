# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 11:34:53 2022

@author: franc
"""
import serial
import time
import datetime as dt
##import serial
##s=serial.Serial(port='COM10', baudrate=9600, timeout=.1)
##s.readline()
##b'<Arduino is ready>\r\n'
##s.write(b'cl4\n')
##

class relay_module:
    """Documentation for the Arduino Relay Modules, does not include private methods of the class.
       Default baudrate = 9600
       Examples:
       
           >>>relay_module=Arduino.ard_relays('COM10')
    """
    def __init__(self,comport=None,baudrate=9600,slave_id=0):
        self.Comport=str(comport).lower()
        self.Baudrate=9600
        self.id=int(slave_id)
        self.client=None
        self._connect()

    def _connect(self):
        try:
            self.client=serial.Serial(port=self.Comport.upper(), baudrate=9600, timeout=.1)     

        except Exception as error:
            print(error)
            raise
    def close_relay(self,relay_to_close):
        """
        Function to close a specific relay in the module

        Args:
            relay_to_close: The relay/channel to close
            
        Kwargs:
            No kwargs.

        Returns:
            No return 

        Raises:
            No raises.

        Examples:
            >>>ard_relay.close_relay(4)
        """
        self.client.write(('cl'+str(relay_to_close)+'\n').encode())

    def open_relay(self,relay_to_open):
        """
        Function to open a specific relay in the module

        Args:
            relay_to_open: The relay/channel to open
            
        Kwargs:
            No kwargs.

        Returns:
            No return 

        Raises:
            No raises.

        Examples:
            >>>ard_relay.open_relay(4)
        """
        
        self.client.write(('op'+str(relay_to_open)+'\n').encode())
    
    def open_all_module_relays(self):
        """
        Function to open all relays in the module.

        Args:
            None
            
        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>relay_module.open_all_module_relays()
           
        """
        for i in range(1,9):
            self.open_relay(i)

    def close_all_module_relays(self):
        """
        Function to open all relays in the module.

        Args:
            None
            
        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>relay_module.open_all_module_relays()
           
        """
        for i in range(1,9):
            self.close_relay(i)
            

    def load_profile(self,profile_list):
            """
            Function that closes/open the relays according to the profile given. Values go from 0 to 8.
            
            Less than 8 values can be used, but the mapping is alwais from CH1 until CH8. Second example only closes CH2.

            Args:
                profile_list: List with the different relay status: (0) off, (1) on
                
            Kwargs:
                No kwargs.

            Returns:
                None

            Raises:
                No raises.

            Examples:
                >>>relay_module.load_profile([0,1,0,1,1,0,0,0])
                >>>relay_module.load_profile([0,1,0])
               
            """
            try:
                try:
                    for i in range(len(profile_list)):
                        if profile_list[i]:
                            self.close_relay(i+1)
                        else:
                            self.open_relay(i+1)
                except:
                    raise
            except:
                raise
