import socket
import ftp_dirgen
import threading
import sys
import time
from ftp_handler import handle_connection

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 21
    homedir = '/home/reece/Honeypot/honeypotv2/2'  # Change this to the directory you want to use for the FTP server

    ftp_dirgen.create_directories(homedir)

    # Create the FTP server socket
    ftp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_sock.bind((host, port))
    ftp_sock.listen(5)

    print(f'FTP honeypot listening on {host}:{port}')

    

    def read_input():  
        while True:
            cmd = input('> ')
            if cmd == 'exit':
                response = input("Are you sure you want to exit? (y/n): ")
                if response.lower() == 'y':
                    ftp_dirgen.remove_directories(None, None, directories=[homedir + '/ftp', homedir + '/downloads', homedir + '/documents'])
                    print('Directories removed.')
                    ftp_sock.close()
                    break
                else:
                    print('Directories not removed. Continuing operation.')
            else:
                # handle unknown command
                print('Unknown command. Please enter "exit".')

    input_thread = threading.Thread(target=read_input)
    input_thread.daemon = True
    input_thread.start()

    # Handle incoming connections
    while True:
            client, addr = ftp_sock.accept()
            print(f'New connection from {addr}')
            handle_connection(client, homedir)

