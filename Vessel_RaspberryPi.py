import serial
import socket
import time


uart = serial.Serial('/dev/serial0', 9600, timeout=0.5)

fstring = "+31616;"
sstring = "+31500;"
uart.write(fstring.encode('utf-8'))
time.sleep(2)
uart.write(sstring.encode('utf-8'))

tsc = 0.05

print("Stating control")


def execute_command(command):
    if command == 'forward':
        uart.write("+31500;".encode('utf-8'))
        time.sleep(tsc)
        uart.write("+31616;".encode('utf-8'))
    elif command == 'backward':
        uart.write("+31500;".encode('utf-8'))
        time.sleep(tsc)
        uart.write("+31384;".encode('utf-8'))
    elif command == 'left forward':
        uart.write("+31500;".encode('utf-8'))
        time.sleep(tsc)
        uart.write("+21616;".encode('utf-8'))
    elif command == 'right forward':
        uart.write("+31500;".encode('utf-8'))
        time.sleep(tsc)
        uart.write("+11616;".encode('utf-8'))
    elif command == 'left turn':
        uart.write("+31500;".encode('utf-8'))
        time.sleep(tsc)
        uart.write("+51616;".encode('utf-8'))
    elif command == 'right turn':
        uart.write("+31500;".encode('utf-8'))
        time.sleep(tsc)
        uart.write("+41616;".encode('utf-8'))
    elif command == 'stop':
        uart.write("+31500;".encode('utf-8'))
        time.sleep(tsc)
        uart.write("+31500;".encode('utf-8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('0.0.0.0', 8001))  
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                print(data)
                if not data:
                    break
                execute_command(data.decode())
