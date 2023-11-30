# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 11:34:53 2022

@author: franc
"""
##from pymodbus.client.sync import ModbusSerialClient
from pymodbus import payload
from pymodbus import client
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from pymodbus.utilities import computeCRC
import numpy as np
import time
import datetime as dt


class relay_module:
    """Documentation for the Waveshare Relay Modules, does not include private methods of the class.
       Default baudrate = 9600, default slave_id = 0.
       
       Examples:
           >>>relay_module=Waveshare_Relay_Module.relay_module('COM17')
           >>>relay_module=Waveshare_Relay_Module.relay_module('COM17',baudrate=115200,slave_id=1)
    """
    def __init__(self,comport=None,baudrate=9600,slave_id=0):
        self.Comport=str(comport).lower()
        self.Baudrate=int(baudrate)
        self.id=int(slave_id)
        self.client=None
        self._connect()
        self.read_module_id()

    def _connect(self):
        try:
            if '/dev/' not in self.Comport:
                #Windows - COMPORT case
                self.client=client.ModbusSerialClient(method='rtu',
                                               port=str(self.Comport).upper(),
                                               stopbits=1,bytesize=8,
                                               parity='N',
                                               baudrate=self.Baudrate,
                                               timeout=0.5,
                                               )
            else:
                #Linux or OS case
                self.client=client.ModbusSerialClient(method='rtu',
                                               port=str(self.Comport),
                                               stopbits=1,bytesize=8,
                                               parity='N',
                                               baudrate=self.Baudrate,
                                               timeout=1,
                                               )
        except Exception as error:
            print(error)
            raise


    def read_module_id(self):
        """
        Function to read the module Modbus slave ID value. 

        Args:
            None
            
        Kwargs:
            No kwargs.

        Returns:
            The value of the module Modbus slave ID.

        Raises:
            No raises.

        Examples:
            >>>relay_module.read_module_id()
        """
        return self.client.read_holding_registers(address=0x4000,
                                                  count=1,
                                                  unit=self.id).registers[0]
    
    def change_module_id(self,target_id):
        """
        Function to change the module modbus slave ID value. 

        Args:
            target_id: Int value with the new modbus slave ID.
            
        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>relay_module.change_module_id(4)
        """
        rq=self.client.write_register(address=0x4000,
                                      value=target_id,
                                      unit=self.id)
        if not rq.isError():
            self.id=target_id
            return 'ID of the module changed successfully.'
        else:
            return 'Error while trying to change module ID'
        
    def change_module_baudrate(self,target_baudrate):
        """
        Function to change the module operational baudrate. 

        Args:
            target_baudrate: Hex value that maps with the corresponding baudrate.
            
            0x0000  : 4800
            
            0x0001  : 9600 #DEFAULT BAUDRATE
            
            0x0002  : 19200
            
            0x0003  : 38400
            
            0x0004  : 57600
            
            0x0005  : 115200
            
            0x0006  : 128000
            
            0x0007  : 256000
            
            
        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>relay_module.change_module_baudrate(0x0005)
        """
        
        rq=self.client.write_register(address=0x2000,
                                      value=target_baudrate,
                                      unit=self.id)
        if not rq.isError():
            self.id=target_id
            return 'Baudrate of the module changed successfully.'
        else:
            return 'Error while trying to change module baudrate'
            
    def read_relays_status(self):
        """
        Function to read the module relays status.

        Args:
            None            
            
        Kwargs:
            No kwargs.

        Returns:
            req: The request made to the relay_module
            output: A list with boolean values corresponding to the status of the relay. True = Enabled, False = Disabled.

        Raises:
            No raises.

        Examples:
            >>>req,out=relay_module.read_relays_status()
            >>>out=[True, True, True, True, True, True, True, True]
           
        """
        #Returns a list with bools indicating status of the relays.
    #Register=0, count=8, unit=11 to 14.
    #output -> [True, True, True, True, True, True, True, True]
    #{0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False}
#   If it fails, it will give an error.
        retries=3
        j=0
        
            #time.sleep(0.1)
##            if j!=0:
        while j<retries:
            try:
                print('Attempt: ',j+1)
                socket_flag=self.client.is_socket_open()
                conn_flag=self.client.connected
                flag=socket_flag and conn_flag
                if flag:
                    print(flag)
                    out={}
                    print('Requesting status')
                    req=self.client.read_coils(address=0,count=8,unit=self.id)
                    print('Attempted')
                    
                    if not req.isError():
                        print('Requested sucessfully the status')
                        req = req.bits
                        for i in range(8):
                            out.update({i:req[i]})
                        if j!=0:
                            print('Num_Tries: ',j+1)
                        print(req,out)
                        return req,out
                    j+=1
                    print(req,out)
                    return req,out
                else:
                    print(self.client.is_socket_open())
                    if j==1:
                        print('Trying reconnection')
                        self.client.close()
                        self._connect()
                        self.read_module_id()
                    j+=1
            except:
                print(self.client.is_socket_open())
                if j==2:
                        print('Trying reconnection')
                        self.client.close()
                        self._connect()
                        self.read_module_id()
                j+=1
                raise



    #Individual relay handling
    def close_relay(self,relay_to_close):
        """
        Function to close a relay in the module.

        Args:
            relay_to_close: Int corresponding to the channel to close the relay at. Goes from 1 to 8.            
            
        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>relay_module.close_relay(5)
           
        """
        if relay_to_close not in [1,2,3,4,5,6,7,8]:
            print('Please index relay from 1 to 8')
            return None
        #values for relay_to_close from 1 to 8
        req,status=self.read_relays_status()
        state=status[relay_to_close-1]
        retries=0
        while state==False:
            if retries<3:
                try:
                    print('Retrying close ',retries)
                    retries+=1
                    print('Writing Coil')
                    if self.client.is_socket_open() and self.client.connected:
                        self.client.write_coil(address=relay_to_close-1,
                                           value=0xFF00,
                                           unit=self.id)
                    print('Reading status')
                    req,status=self.read_relays_status()
                    state=status[relay_to_close-1]
                    print('Status read',state)
                except Exception as e:
                    if retries==2:
                        print('Trying reconnection')
                        self.client.close()
                        self._connect()
                    pass
##            elif retries>3 and retries<5:
##                try:
##                    print('Creating error handler')
##                    self._error_handling_module(self.errorhandlerport)
##                    print('Created error handler')
##                    if self.errorhandler!=None:
##                        print('Switching error handler')
##                        errorhandler.close_relay(7)
##                        errorhandler.open_relay(7)
##                        print('Ready to operate again')
##                        self._connect()
##                        retries+=1
##                        self.client.write_coil(address=relay_to_close-1,
##                                               value=0xFF00,
##                                               unit=self.id)
##    ##                    time.sleep(0.2)
##                        req,status=self.read_relays_status()
##                        state=status[relay_to_close-1]
##
##                    else:
##                        retries+=1
                except Exception as e:
                    print(e)
                    pass
            else:
                break
        return

    def open_relay(self,relay_to_open):
        """
        Function to open a relay in the module.

        Args:
            relay_to_close: Int corresponding to the channel to close the relay at. Goes from 1 to 8.            
            
        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>relay_module.close_relay(5)
           
        """
        #values for relay_to_close from 1 to 8
        if relay_to_open not in [1,2,3,4,5,6,7,8]:
            print('Please index relay from 1 to 8')
            return None
        req,status=self.read_relays_status()
        state=status[relay_to_open-1]
        retries=0
        while state==True:
            if retries<3:
                try:
                    print('Retrying open ',retries)
                    retries+=1
                    print('Writing Coil')
                    if self.client.is_socket_open() and self.client.connected:
                        self.client.write_coil(address=relay_to_open-1,
                                               value=0x0000,
                                               unit=self.id)
##                    time.sleep(0.2)
                    print('Reading status')
                    req,status=self.read_relays_status()
                    state=status[relay_to_open-1]
                        
                    print('Status read',state)
                    
                except Exception as e:
                    if retries==2:
                        print('Trying reconnection')
                        self.client.close()
                        self._connect()
                    pass
##            elif retries>3 and retries<5:
##                try:
##                    print('Creating error handler')
##                    self._error_handling_module(self.errorhandlerport)
##                    print('Created error handler')
##                    if self.errorhandler!=None:
##                        print('Switching error handler')
##                        errorhandler.close_relay(7)
##                        errorhandler.open_relay(7)
##                        print('Ready to operate again')
##                        self._connect()
##                        retries+=1
##                        self.client.write_coil(address=relay_to_open-1,
##                                               value=0x0000,
##                                               unit=self.id)
##    ##                    time.sleep(0.2)
##                        req,status=self.read_relays_status()
##                        state=status[relay_to_open-1]
##
##                    else:
##                        retries+=1
                except Exception as e:
                    print(e)
                    raise
            else:
                break
        return

    #Relays group handling
    #Close all relays for a module
    def close_all_module_relays(self):
        """
        Function to close all relays in the module.

        Args:
            None
            
        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>relay_module.close_all_module_relays()
           
        """
        try:
            #Slave ID that contains GUC.
            try:
                status=self.read_relays_status()
            except:
##                time.sleep(0.1)
                status=self.read_relays_status()

            try:
                self.client.write_coil(address=0x00ff,value=1,unit=self.id)
##                time.sleep(0.1)
                status=self.read_relays_status()
                for i in range(8):
                    #if its not closed
                    if status[i]==False:
                        self.close_relay(i)
            except:
                raise
        except:
            raise
    
    #Open all relays for a module
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
        try:
            #Slave ID that contains GUC.
            try:
                status=self.read_relays_status()
            except:
##                time.sleep(0.1)
                status=self.read_relays_status()

            try:
                self.client.write_coil(address=0x00ff,value=0,unit=self.id)
                time.sleep(0.1)
                status=self.read_relays_status()
                for i in range(8):
                    #if its not closed
                    if status[i]==True:
                        self.open_relay(i+1)
            except:
                raise
        except:
            raise

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
            #Slave ID that contains GUC.
            try:
                status=self.read_relays_status()
            except:
                #time.sleep(0.1)
                status=self.read_relays_status()

            try:
                status=self.read_relays_status()
                for i in range(len(profile_list)):
                    if profile_list[i]:
                        self.close_relay(i+1)
                    else:
                        self.open_relay(i+1)
            except:
                raise
        except:
            raise

