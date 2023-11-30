import time
from pymodbus.client.sync import ModbusSerialClient
from pymodbus import payload
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian



class LCB:
    """Documentation for the Lyra Controller Board unit, does not include private methods of the class.
        
       Examples:
           >>>lcb=OOP_LCB.LCB(6,1)
    """
    def __init__(self,COMPORT,slave_id):
        self.comport=COMPORT
        self.slave_id=slave_id
        self.serial=None
        #Done
        self.input_registers=None
        self.coils=None
        self.BT_config=None
        self.GU_config=None
        self.SB_config=None
        self.cmd_register=None
        self.time=None
        self.version=None
        self.version_date=None
        self.flags_tf=None
        self.parsed_bt_flags=None
        self.flags_gu=None
        self.parsed_gu_flags=None
        self.flags_sb=None
        self.parsed_sb_flags=None
        self.status=None
        self.opmode=None

        #standalone=True
        self.stablish_connection()
        self.update_time()

#MODBUS METHODS
    def _stablish_connection(self):
        num_retries=3
        while num_retries>0:
            try:
                num_retries-=1
                client=ModbusSerialClient(method='rtu',port='COM'+str(self.comport),stopbits=1,bytesize=8,parity='N',baudrate=115200,timeout=0.2)
                client.connect()
                if client.is_socket_open():
                    self.serial=client
                    print('Connection successfull')
                    return client
                    
                
            except Exception as e:
                num_retries-=1
                if num_retries==0:
                    print(e)
        print('Error while creating connection')

#MODBUS READING METHODS
    def read_uint32_register(self,register):
        """
        Allows the reading of two 16-bit registers (32-bits in total).

        Args:
            register: The integer value of the first register to read.
            
        Kwargs:
            No kwargs.

        Returns:
            A interger value that contains the information from the 32-bits register.

        Raises:
            No raises.

        Examples:
            >>>lcb.read_uint32_register(7000)
        """
        data=None
        try:
            request=self.serial.read_holding_registers(address=register,count=2,unit=self.slave_id)
            decoder = payload.BinaryPayloadDecoder.fromRegisters(request.registers, byteorder=">", wordorder=">")
            if not request.isError():
                return decoder.decode_32bit_uint()
            return data
        except Exception as e:
            print(e)
            raise
        
    def read_hex32_register(self,register):
        """
        Allows the reading of two 16-bit registers (32-bits in total).

        Args:
            register: The integer value of the first register to read.
            

        Kwargs:
            No kwargs.

        Returns:
            A hex value that contains the information from the 32-bits register.

        Raises:
            No raises.

        Examples:
            >>>lcb.read_hex32_register(7000)
        """
        data=None
        try:
            request=self.serial.read_holding_registers(address=register,count=2,unit=self.slave_id)
            if not request.isError():
                return [hex(i) for i in request.registers]
            return data
        except Exception as e:
            print(e)
            raise
        
    def read_coils(self):
        """
        Allows the reading of the coils status from the LCB unit. These are directly linked to the GPIOs of the board.

        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the values of the coils. 0 if a coil is disabled, 1 if enabled.

        Raises:
            No raises.

        Examples:
            >>>lcb.read_coils()
        """
        rq=self.serial.read_coils(1000,count=3,unit=self.slave_id)
        if not rq.isError():
            return [int(x) for x in rq.bits]
        else:
            return [None]*3

    def read_float(self,initial_address,nregisters):
        """
        Allows the reading of n 16-bit registers decoded as 32-bits floats.

        Args:
            initial_address: Initial address of the registers to be read.
            nregisters: The amount of registers to read. Must be an even number.

        Kwargs:
            No kwargs.

        Returns:
            A float value that contains the information from the 32-bits registers.

        Raises:
            No raises.

        Examples:
            >>>lcb.read_float(7000,16)
        """
        data=[]
        try:
            request=self.serial.read_holding_registers(address=initial_address,count=nregisters,unit=self.slave_id)
            decoder = payload.BinaryPayloadDecoder.fromRegisters(request.registers, byteorder=">", wordorder=">")
            if not request.isError():
                for i in range(int(nregisters/2)):
                    data.append(round(decoder.decode_32bit_float(),4))
                self.input_registers=data
                return data
                
            else:
                return data
        except Exception as e:
            print(e)
            return data

    def write_cmd(self,values):
        """
        Allows the writing of n 16-bit registers in the register 5000.

        Args:
            values: List with the 16-bits values to write.

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.write_cmd([0x01,0x00])
        """
        try:
            builder = BinaryPayloadBuilder(byteorder=Endian.Big)
            for value in values:
                builder.add_16bit_int(int(value))
            payload = builder.build()
            result  = self.serial.write_registers(5000, payload, skip_encode=True,unit=self.slave_id)
            if not result.isError():
                #print('Register ',register,' written succesfully with value',value)
                return
        except: 
            raise

        
    def write_float(self,starting_address,values):
        """
        Allows the writing of n floats registers.

        Args:
            starting_address: Initial address of the registers to be written.
            values: List with the 32-bits float values to write.

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.write_float(7000,[200,100])
        """
        starting_address=starting_address
        for i in range(len(values)):
            try:
                builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
                builder.add_32bit_float(values[i])
                payload = builder.build()
                result  = self.serial.write_registers(starting_address+i*2, payload, skip_encode=True, unit=self.slave_id)
            except Exception as e:
                print(e)
                raise
        
#LYRA METHODS
    def update_time(self):
        """
        Updates the time of the lyra controller board.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.update_time()
        """
        data=None
        try:
            builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
            builder.add_32bit_uint(int(time.time()))
            payload = builder.build()
            address = 5004
            result  = self.serial.write_registers(address, payload, skip_encode=True, unit=self.slave_id)
            print('LCB time updated')
        except Exception as e:
            print(e)
            pass
            
    def update_basic_info(self):
        """
        Updates the basic information of the lyra controller board.
        Time, version of FW and FW date, flags for each application, status and operation mode.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.update_time()
        """
        #Time and FW data
        self.time=self.read_uint32_register(5004)
        self.version=self.read_hex32_register(5006)
        self.version_date=self.read_hex32_register(5008)

        #Flags
        self.flags_tf=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5010)]
        self.flags_gu=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5012)]
        self.flags_sb=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5014)]
        
        #Status and op mode
        self.status=self.read_hex32_register(5016)
        self.opmode=self.read_hex32_register(5018)

    def _status(self):
    
        self.status=self.read_hex32_register(5016)
        return self.status
    
    def _op_mode(self):
        self.opmode=self.read_hex32_register(5018)
        return self.opmode
        
    
    def _time(self):
        time=self.read_uint32_register(5004)
        self.time=time
        return self.time

    def _bt_flags(self):
        try:
            self.flags_tf=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5010)]
            return self.flags_tf
        except:
            pass
    def parse_bt_flags(self):
        """
        Function that returns the flags for the Balancing Transformer application.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different flags raised during operation.

        Raises:
            No raises.

        Examples:
            >>>lcb.parse_bt_flags()
        """
        try:
            self.flags_tf=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5010)]
            #print(self.flags_tf)
            values1=list(self.flags_tf[1])
            values1.reverse()
            values1=''.join(values1)
            values2=list(self.flags_tf[0])
            values2.reverse()
            values2=''.join(values2)
            values=values1+values2
            #print(values)
            flags=[]
            if values[0]=='1':flags.append('Volt_Min_Disc')
            if values[1]=='1':flags.append('Volt_Max_Disc')
            if values[2]=='1':flags.append('Freq_Min_Disc')
            if values[3]=='1':flags.append('Freq_Max_Disc')
            if values[4]=='1':flags.append('Volt_Diff_Max_Disc')
            if values[5]=='1':flags.append('Freq_Diff_Min_Disc')
            if values[6]=='1':flags.append('Ph_Diff_Max_Disc')
            if values[7]=='1':flags.append('Current_Max_Disc')
            if values[8]=='1':flags.append('V_Diff_G1G2_Max_Disc')
            if values[9]=='1':flags.append('F_Diff_G1G2_Max_Disc')
            if values[10]=='1':flags.append('Ph_Diff_G1G2_Max_Disc')
            if values[11]=='1':flags.append('Volt_Min_Conn')
            if values[12]=='1':flags.append('Volt_Max_Conn')
            if values[13]=='1':flags.append('Volt_Max_Diff_Conn')
            if values[14]=='1':flags.append('Freq_Max_Diff_Conn')
            if values[15]=='1':flags.append('Ph_Max_Diff_Conn')
            if values[16]=='1':flags.append('Time_Out_Conn')
            flags.reverse()
            self.parsed_bt_flags=flags
            return self.parsed_bt_flags
        except:
            raise

    def _gu_flags(self):
        try:
            self.flags_gu=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5012)]
            return self.flags_gu
        except:
            pass

    def parse_gu_flags(self):
        """
        Function that returns the flags for the Grid Uniyfing application.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different flags raised during operation.

        Raises:
            No raises.

        Examples:
            >>>lcb.parse_gu_flags()
        """
        try:
            self.flags_gu=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5012)]
            values=self.flags_gu[1]
            #print(self.flags_gu)
            values1=list(self.flags_gu[1])
            values1.reverse()
            values1=''.join(values1)
            values2=list(self.flags_gu[0])
            values2.reverse()
            values2=''.join(values2)
            values=values1+values2
            #print(values)
            flags=[]
            if values[0]=='1':flags.append('Volt_Min_Disc')
            if values[1]=='1':flags.append('Volt_Max_Disc')
            if values[2]=='1':flags.append('Freq_Min_Disc')
            if values[3]=='1':flags.append('Freq_Max_Disc')
            if values[4]=='1':flags.append('Volt_Diff_Max_Disc')
            if values[5]=='1':flags.append('Freq_Diff_Min_Disc')
            if values[6]=='1':flags.append('Ph_Diff_Max_Disc')
            if values[7]=='1':flags.append('Current_Max_Disc')
            if values[8]=='1':flags.append('V_Diff_G1G2_Max_Disc')
            if values[9]=='1':flags.append('F_Diff_G1G2_Max_Disc')
            if values[10]=='1':flags.append('Ph_Diff_G1G2_Max_Disc')
            if values[11]=='1':flags.append('Volt_Min_Conn')
            if values[12]=='1':flags.append('Volt_Max_Conn')
            if values[13]=='1':flags.append('Volt_Max_Diff_Conn')
            if values[14]=='1':flags.append('Freq_Max_Diff_Conn')
            if values[15]=='1':flags.append('Ph_Max_Diff_Conn')
            if values[16]=='1':flags.append('Time_Out_Conn')
            flags.reverse()
            self.parsed_gu_flags=flags
            return self.parsed_gu_flags
        except:
            pass

    def _sb_flags(self):
        try:
            self.flags_sb=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5014)]
            return self.flags_sb
        except:
            pass
        
    def parse_sb_flags(self):
        """
        Function that returns the flags for the Synchronous Breaker application.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different flags raised during operation.

        Raises:
            No raises.

        Examples:
            >>>lcb.parse_sb_flags()
        """
        try:
            self.flags_sb=['{0:016b}'.format(int(x,16)) for x in self.read_hex32_register(5014)]
            values=self.flags_sb[1]
            #print(self.flags_sb)
            values1=list(self.flags_sb[1])
            values1.reverse()
            values1=''.join(values1)
            values2=list(self.flags_sb[0])
            values2.reverse()
            values2=''.join(values2)
            values=values1+values2
            #print(values)
            flags=[]
            if values[0]=='1':flags.append('Volt_Min_Disc')
            if values[1]=='1':flags.append('Volt_Max_Disc')
            if values[2]=='1':flags.append('Freq_Min_Disc')
            if values[3]=='1':flags.append('Freq_Max_Disc')
            if values[4]=='1':flags.append('Volt_Diff_Max_Disc')
            if values[5]=='1':flags.append('Freq_Diff_Min_Disc')
            if values[6]=='1':flags.append('Ph_Diff_Max_Disc')
            if values[7]=='1':flags.append('Current_Max_Disc')
            if values[8]=='1':flags.append('V_Diff_G1G2_Max_Disc')
            if values[9]=='1':flags.append('F_Diff_G1G2_Max_Disc')
            if values[10]=='1':flags.append('Ph_Diff_G1G2_Max_Disc')
            if values[11]=='1':flags.append('Volt_Min_Conn')
            if values[12]=='1':flags.append('Volt_Max_Conn')
            if values[13]=='1':flags.append('Volt_Max_Diff_Conn')
            if values[14]=='1':flags.append('Freq_Max_Diff_Conn')
            if values[15]=='1':flags.append('Ph_Max_Diff_Conn')
            if values[16]=='1':flags.append('Time_Out_Conn')
            flags.reverse()
            self.parsed_sb_flags=flags
            return self.parsed_sb_flags
        except:
            pass

    def _coils(self):
        self.coils=self.read_coils()
        return self.coils
    
    def _lyra_input_registers(self):
        #ID is composed by two 16-bit digits.
        data=[]
        try:
            nregisters=72
            request=self.serial.read_input_registers(address=7000,count=nregisters,unit=self.slave_id)
            decoder = payload.BinaryPayloadDecoder.fromRegisters(request.registers, byteorder=">", wordorder=">")
            if not request.isError():
                for i in range(int(nregisters/2)):
                    data.append(round(decoder.decode_32bit_float(),4))
                self.input_registers=data
                return data
                
            else:
                return data
        except Exception as e:
            print(e)
            return data
        
    def get_bt_parameters(self):
        """
        Function that gets the configuration parameters for the Balancing Transformer application.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different parameters for the application.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_bt_parameters()
        """
        params=self.read_float(7200,28)
        self.BT_config=params
        return self.BT_config

    def set_bt_parameters(self,values):
        """
        Function that sets the configuration parameters for the Balancing Transformer application.
        
        Args:
            values: List with the values of the different configuration parameters (float or int)

        Kwargs:
            No kwargs.

        Returns:
            A list with the different parameters for the application.

        Raises:
            No raises.

        Examples:
            >>>lcb.set_bt_parameters([0.01, 3.0, 210.0, 250.0, 0.1, 10.0, 10.0, 180.0, 270.0, 20.0, 300.0, 1.0, 3.0, 30.0])
        """
        #[0.01, 3.0, 210.0, 250.0, 0.1, 10.0, 10.0, 180.0, 270.0, 20.0, 300.0, 1.0, 3.0, 30.0]
        if len(values)!=14:
            print('Check your input parameters, length not equal to the configuration registers',len(values))
            
        self.write_float(7200,values)
        print('LCB BT parameters updated successfully')
        print(values)

    def get_gu_parameters(self):
        """
        Function that gets the configuration parameters for the Grid Unifying application.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different parameters for the application.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_gu_parameters()
        """
        params=self.read_float(7260,14)
        self.GU_config=params
        return self.GU_config

    def set_gu_parameters(self,values):
        #[3.0, 210.0, 250.0, 0.1, 10.0, 3.0, 30.0]
        """
        Function that sets the configuration parameters for the Grid Unifying application.
        
        Args:
            values: List with the values of the different configuration parameters (float or int)

        Kwargs:
            No kwargs.

        Returns:
            A list with the different parameters for the application.

        Raises:
            No raises.

        Examples:
            >>>lcb.set_gu_parameters([3.0, 210.0, 250.0, 0.1, 10.0, 3.0, 30.0])
        """
        if len(values)!=7:
            print('Check your input parameters, length not equal to the configuration registers')
            
        self.write_float(7260,values)
        print('LCB GU parameters updated successfully')
        print(values)
        
    def get_sb_parameters(self):
        """
        Function that gets the configuration parameters for the Synchronous Breaker application.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different parameters for the application.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_sb_parameters()
        """
        params=self.read_float(7320,22)
        self.SB_config=params
        return self.SB_config

    def set_sb_parameters(self,values):
        """
        Function that gets the configuration parameters for the Synchronous Breaker application.
        
        Args:
            values: List with the values of the different configuration parameters (float or int)

        Kwargs:
            No kwargs.

        Returns:
            A list with the different parameters for the application.

        Raises:
            No raises.

        Examples:
            >>>lcb.set_sb_parameters([10.0, 210.0, 250.0, 0.1, 10.0, 15.0, 180.0, 270.0, 50.0, 3.0, 30.0])
        """
        #[10.0, 210.0, 250.0, 0.1, 10.0, 15.0, 180.0, 270.0, 50.0, 3.0, 30.0]
        if len(values)!=11:
            print('Check your input parameters, length not equal to the configuration registers')
            
        self.write_float(7320,values)
        print('LCB SB parameters updated successfully')
        print(values)
        

    def get_cmd_register(self):
        """
        Function that gets the command register value.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            The sum of both 32-bit hex values for the registers 5000 and 5002.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_cmd_register()
        """
        try:
            return self.read_hex32_register(5000)+self.read_hex32_register(5002)
        except:
            pass

    def set_cmd_register(self,values):
        """
        Function that writes the command register value.
        
        Args:
            values: List with the values to be written in the command registers (5000 and 5002)

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.set_cmd_register([0x01,0x02])
        """
        self.write_cmd(values)

    def get_side1_calibration_params(self):
        """
        Function that retrieves the calibration parameters for gain & offset in (V,I,P,Q) per phases (A,B,C) for the side 1 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file, registers 7380 and on.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different configuration parameters for side 1 in the LCB, as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_side1_calibration_params()
        """
        params=self.read_float(7380,48)
        self.calibparams1=params
        return self.calibparams1
    
    def get_side2_calibration_params(self):
        """
        Function that retrieves the calibration parameters for gain & offset in (V,I,P,Q) per phases (A,B,C) for the side 2 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file, registers 7440 and on.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different configuration parameters for side 1 in the LCB, as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_side2_calibration_params()
        """
        params=self.read_float(7440,48)
        self.calibparams2=params
        return self.calibparams2

    def set_side1_calibration_params(self,values):
        """
        Function that sets the calibration parameters for gain & offset in (V,I,P,Q) per phases (A,B,C) for the side 2 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file, registers 7440 and on.
        
        Args:
            values: List with float values to be implemented in each register according to the LCB Modbus Register Map

        Kwargs:
            No kwargs.

        Returns:
            A list with the different configuration parameters for side 1 in the LCB, as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.set_side1_calibration_params([1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0])
        """
        self.write_float(7380,values)
        print('LCB SB parameters updated successfully')
        print(values)
        
    
    def set_side2_calibration_params(self,values):
        """
        Function that sets the calibration parameters for gain & offset in (V,I,P,Q) per phases (A,B,C) for the side 1 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file, registers 7380 and on.
        
        Args:
            values: List with float values to be implemented in each register according to the LCB Modbus Register Map

        Kwargs:
            No kwargs.

        Returns:
            A list with the different configuration parameters for side 1 in the LCB, as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.set_side2_calibration_params([1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0])
        """
        self.write_float(7440,values)
        print('LCB SB parameters updated successfully')
        print(values)

#Voltages
    def set_v1_offsets(self,values):
        """
        Function that sets the voltage offset parameters for the phases (A,B,C) in the side 1 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            values: List with float values to be implemented in each register according to the LCB Modbus Register Map

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.set_v1_offsets([0.1,-0.2,0.23])
        """
        off_registers=[7382,7398,7414]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])

    def set_v2_offsets(self,values):
        """
        Function that sets the voltage offset parameters for the phases (A,B,C) in the side 2 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            values: List with float values to be implemented in each register according to the LCB Modbus Register Map

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.set_v2_offsets([0.1,-0.2,0.23])
        """
        off_registers=[7442,7458,7474]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])

    def set_v1_gains(self,values):
        """
        Function that sets the voltage gains parameters for the phases (A,B,C) in the side 1 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            values: List with float values to be implemented in each register according to the LCB Modbus Register Map

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.set_v1_gains([1,1.023,1.01])
        """
        off_registers=[7380,7396,7412]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])

    def set_v2_gains(self,values):
        """
        Function that sets the voltage gains parameters for the phases (A,B,C) in the side 2 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            values: List with float values to be implemented in each register according to the LCB Modbus Register Map

        Kwargs:
            No kwargs.

        Returns:
            None

        Raises:
            No raises.

        Examples:
            >>>lcb.set_v2_gains([1,1.023,1.01])
        """
        off_registers=[7440,7456,7472]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])

    def get_v1_offsets(self):
        """
        Function that gets the voltage offsets parameters for the phases (A,B,C) in the side 1 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different values for the v1 offsets, decoded as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_v1_offsets()
        """
        data=[]
        off_registers=[7382,7398,7414]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data

    def get_v2_offsets(self):
        """
        Function that gets the voltage offsets parameters for the phases (A,B,C) in the side 2 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different values for the v2 offsets, decoded as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_v2_offsets()
        """
        data=[]
        off_registers=[7442,7458,7474]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data

    def get_v1_gains(self):
        """
        Function that gets the voltage gains parameters for the phases (A,B,C) in the side 1 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different values for the v1 gains, decoded as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_v1_gains()
        """
        data=[]
        off_registers=[7380,7396,7412]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data

    def get_v2_gains(self):
        """
        Function that gets the voltage gains parameters for the phases (A,B,C) in the side 2 measurements.
        For more information please review the Lyra Controller Board Modbus Register Map file.
        
        Args:
            None

        Kwargs:
            No kwargs.

        Returns:
            A list with the different values for the v2 gains, decoded as floats.

        Raises:
            No raises.

        Examples:
            >>>lcb.get_v2_gains()
        """
        data=[]
        off_registers=[7440,7456,7472]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data


#Current
    def set_i1_offsets(self,values):
        off_registers=[7386,7402,7418]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])

    def set_i2_offsets(self,values):
        off_registers=[7446,7462,7478]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])

    def set_i1_gains(self,values):
        off_registers=[7384,7400,7416]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])

    def set_i2_gains(self,values):
        off_registers=[7444,7460,7476]
        for i in range(len(off_registers)):
            self.write_float(off_registers[i],[values[i]])
            
    def get_i1_offsets(self):
        data=[]
        off_registers=[7386,7402,7418]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data

    def get_i2_offsets(self):
        data=[]
        off_registers=[7446,7462,7478]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data

    def get_i1_gains(self):
        data=[]
        off_registers=[7384,7400,7416]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data

    def get_i2_gains(self):
        data=[]
        off_registers=[7444,7460,7476]
        for i in range(len(off_registers)):
            data.append(self.read_float(off_registers[i],2)[0])
        return data        

    def reboot(self):
        self.write_cmd([0x0000,0x0001])
        time.sleep(0.3)

    def _export_data(self):
        return [self._time(),self.version,self.version_date,self._status(),self._op_mode(),self.get_cmd_register(),self._bt_flags(),self._gu_flags(),self._sb_flags(),self._coils(),self._lyra_input_registers()]
    

    def measure_sideA(self):
        data=[]
        try:
            nregisters=36
            request=self.serial.read_input_registers(address=7000,count=nregisters,unit=self.slave_id)
            decoder = payload.BinaryPayloadDecoder.fromRegisters(request.registers, byteorder=">", wordorder=">")
            if not request.isError():
                for i in range(int(nregisters/2)):
                    data.append(round(decoder.decode_32bit_float(),4))
                self.input_registers=data
                return data
                
            else:
                return data
        except Exception as e:
            print(e)
            return data

    def _export_data_measurements(self):
        return [self._time(),self.measure_sideA()]
##
##lcb=LCB(5,1)
##print(lcb._export_data_measurements())
###lcb._lyra_input_registers()
##print(lcb.measureLN_A())
##print(lcb.measure_sideA())

##lcb=LCB(5,8)
##print(lcb.get_v1_offsets())
##print(lcb.get_v2_offsets())
##lcb.update_basic_info()
#print(lcb._bt_flags())
##print(lcb.parse_bt_flags())
#print(lcb._gu_flags())
##print(lcb.parse_gu_flags())
#print(lcb._sb_flags())
##print(lcb.parse_sb_flags())
##lcb.set_v1_offsets([-11,-11,-11])
##lcb.set_v2_offsets([-11,-11,-11])


