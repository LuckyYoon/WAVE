#vesselcontrol.py

import socket  # Import socket module for network communication
import tkinter as tk  # Import tkinter for GUI elements (not used in this function)

raspi_ip_address = 'IP Address of Raspberry PI'  # IP Address of the Raspberry Pi controlling the vessel

def send_command(command):
    """
    Sends a command to the Raspberry Pi over a network socket.

    This function establishes a socket connection with the Raspberry Pi using its IP address and a predefined port.
    It then sends the specified command to the Pi, which can be used for various control actions.

    :param command: The command string to be sent to the Raspberry Pi for execution.
    """
    try:
        # Create a socket object using IPv4 addressing and TCP protocol
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Establish a connection to the Raspberry Pi at the specified IP address and port 8001
            s.connect((raspi_ip_address, 8001))
            # Send the command encoded as bytes over the network
            s.sendall(command.encode())
    except Exception as e:
        # Print any error that occurs during the socket communication
        print("Error:", e)
