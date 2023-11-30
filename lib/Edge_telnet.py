from telnetlib import Telnet
import time


class edge_system:
    """Documentation for the Edge unit class, does not include private methods of the class."""
    
    def __init__(self,address):
        #""" The constructor."""
        self.ADDRESS=address
        self.client=None

        #"""Method to initialize the connection."""
        self.create_connection()

    def _create_connection(self):
        """
       This function handles the connection with the unit and creates a serial client that it's later used to communicate with the unit.
       It is an internal method and it's used at the moment of creating the class object.

        Args:
            No arguments

        Kwargs:
            No Kwargs.

        Returns:
            No return.

        Raises:
            No raises.

            
        """
        
        self.client=Telnet('edge-'+str(self.ADDRESS)+'.local',23)
        
    def query(self,msg,timeout):

        """
        This function handles communication with the Edge unit. After client is created, a query is defined as a write and & read response action.

        Args:
            msg: The string with characters that represent the desired command.
            timeout: The amount of time that the whole query process will take.

        Kwargs:
            No kwargs.

        Returns:
            A string holding the response of the unit.

        Raises:
            No raises.

        Examples:
            >>>edge_system.query('QPIGS',1)
        """
        
        #Method to query (write a cmd and read the response) the edge unit
        self.client.write(msg.encode()+b"\n\r")
        output = self.client.read_until(b'\r', timeout)
        return [float(x) for x in output.decode().replace('(','').replace('\n','').split(" ")]
    
    def raw_query(self,msg,timeout):

        """
        This function handles communication with the Edge unit. After client is created, a query is defined as a write and & read response action.

        Args:
            msg: The string with characters that represent the desired command.
            timeout: The amount of time that the whole query process will take.

        Kwargs:
            No kwargs.

        Returns:
            A raw binary holding the response of the unit.

        Raises:
            No raises.

        Examples:
            >>>edge_system.raw_query('QPIGS',1)
        """
        #Method to initialize the connection with the Telnet client, but don't replace anything on the string.
        self.client.write(msg.encode()+b"\n\r")
        output = self.client.read_until(b'\r', timeout)
        return output.decode().replace('(','').replace('\n','').split(" ")
        
        
#unit1=edge_system(4000000010)
#unit2=edge_system(4000100026)
#unit=edge_system(4000100006)
##print(len(unit.query('QPIGS2',1)))
##print(len(unit.query('QPIGS',1)))
##print(len(unit.query('QPIRI',1)))
##print(unit.raw_query('QPIGS2',1))
####print(unit.raw_query('QPIGS',1))
##print(unit1.raw_query('QPIGS',1))
##print(unit1.raw_query('QPIGS',1)[8])
##
##print(unit2.raw_query('QPIGS',1))
##print(unit2.raw_query('QPIGS',1)[8])

###To set into a different operation mode
##print(unit.raw_query('QPIRI',1))
##print(unit.raw_query('QPIRI',1)[21])
##unit.raw_query('POPRY0',1)
##time.sleep(5)
##unit.raw_query('POPM01',1)
##time.sleep(3)
##unit.raw_query('POPRY1',1)

