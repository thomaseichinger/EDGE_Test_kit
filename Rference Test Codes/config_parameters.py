import telnetlib

def send_telnet_command(serial, command):
    """
    Sends a Telnet command to an inverter and prints the acknowledgement.

    Parameters:
    - serial (str): The serial number of the inverter.
    - command (str): The command to send (e.g., "PGR01" or "PGR00").
    """
    try:
        print(f"Connecting to inverter with serial: {serial}...")
        with telnetlib.Telnet(f"edge-{serial}.local", 23) as tn:
            print(f"Sending command '{command}'...")
            tn.write(command.encode() + b'\r\n')
            ack = tn.read_until(b"\n", 3).decode().strip()  # Read acknowledgment
            print(f"Acknowledgement: {ack}")
    except Exception as e:
        print(f"Error: Failed to connect or send command to inverter with serial {serial}. {e}")

# Example usage of the function:
if __name__ == '__main__':
    serial_number = '4000100104'  # Example serial number
    command = 'PGR00'  # Example command to send
    send_telnet_command(serial_number, command)
