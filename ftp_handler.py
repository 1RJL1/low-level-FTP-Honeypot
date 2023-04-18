import os
import glob
import logging
import ftp_config
from ftp_logger import setup_logger, log_command
from ftplib import error_perm
import ftp_alert
import socket
import time

def handle_connection(client, homedir):
    current_dir = homedir
    root_dir = homedir
    data_sock = None
    is_logged_in = False
    username = ftp_config.config.get('login', 'username')
    password = ftp_config.config.get('login', 'password')
    start_time = time.time()
    
    
    #Sends alert to administrator
    
    
    #Setup logger called 
    logger = setup_logger()
    
    #Sends initial response to client
    client.send(b'220 FTP Server\r\n')

    while True:

        try:

        # Receive FTP command from client
            data = client.recv(1024)

            if not data:
                break

        # Parse FTP command
            parts = data.decode().strip().split(' ')
            command = parts[0].upper()

        # Log commands
            log_command(command, client.getpeername()[0], ' '.join(parts[1:]))

        # Handle FTP commands
            if command == 'USER':
               if parts[1] == username:
                   client.send(b'331 OK\r\n')
               else:
                   client.send(b'530 Login incorrect.\r\n')

            elif command == 'PASS':
               if parts[1] == ftp_config.config.get('login', 'password'):
                   is_logged_in = True
                   client.send(b'230 Login successful\r\n')
               else:
                   client.send(b'530 Login incorrect.\r\n')
                   client.close()
            
            elif not is_logged_in:
                    client.send(b'530 Please log in.\r\n')
            
            elif command == 'QUIT':
                client.send(b'221 Goodbye\r\n')
                break
            
            elif command == 'MKD':
                dir_name = ' '.join(parts[1:])
                new_dir = os.path.join(current_dir, dir_name)
                   
                try:
                    os.mkdir(new_dir)
                    client.send(f'257 "{dir_name}" created\r\n'.encode())
                
                except OSError as e:
                    client.send(f'550 "{new_dir}" could not be created: {e}\r\n'.encode())
            
            elif command == 'RMD':
                dir_name = ' '.join(parts[1:])
                rm_dir = os.path.join(current_dir, dir_name)
                
                try:
                    os.rmdir(rm_dir)
                    client.send(f'250 "{dir_name}" removed\r\n'.encode())
                
                except OSError as e:
                    client.send(f'550 "{dir_name}" either does not exist or could not be removed\r\n'.encode())
            
            elif command == 'PWD':
                relpath = os.path.relpath(current_dir, homedir)
                if relpath == ".":
                   relpath = "/files"
                else:   
                    relpath = "files/" + relpath.replace("\\", "/")
                client.send(f'257 "{relpath}" is the current directory\r\n'.encode())    
            
            elif command == 'CWD':
                dir_name = ' '.join(parts[1:])
                if dir_name == '..':
                    if current_dir == root_dir:
                        client.send(f'550 Cannot change to parent directory.\r\n'.encode())
                    else:
                        current_dir = os.path.dirname(current_dir)
                        client.send(f'250 CWD command successful\r\n'.encode())
                elif dir_name == '/' or dir_name.lower() == '/root':
                    client.send(f'550 Cannot change to root directory.\r\n'.encode())        
                else:
                    new_dir = os.path.join(current_dir, dir_name)
                    if os.path.isdir(new_dir):
                        current_dir = new_dir
                        client.send(f'250 CWD command successful\r\n'.encode())
                    else:
                        client.send(f'550 "{dir_name}" is not a directory\r\n'.encode())
                        
            elif command == 'PASV':
                # Enter passive mode
                if data_sock is not None:
                    data_sock.close()
                data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip_address = ftp_config.config.get('FTP', 'ip_address')
                data_sock.bind((ip_address, 0))
                data_sock.listen(1)
                ip, port = data_sock.getsockname()
                client.send(f'227 Entering Passive Mode ({ip.replace(".",",")},{port>>8},{port&0xff})\r\n'.encode())
            
            elif command == 'PORT':
                # Enter active mode
                parts = parts[1].split(',')
                ip = '.'.join(parts[:4])
                port = (int(parts[4]) << 8) + int(parts[5])
                data_sock = client.make_port_socket(ip, port)
                client.send(b'200 PORT command successful.\r\n')    
            
            elif command == 'HOST':
                # Return public IP address of the server
                host_ip = socket.gethostbyname(socket.gethostname())
                host_str = host_ip.replace(".", ",")
                client.send(f'215 {host_str}\r\n'.encode())
            
            elif command == 'LIST':
                if data_sock is None:
                    client.send(b'425 Use PORT or PASV first.\r\n')
                    continue
                data_conn, _ = data_sock.accept()
                client.send(b'150 Opening data connection.\r\n')
                files = glob.glob(os.path.join(current_dir, '*'))
                file_list = '\r\n'.join(os.path.basename(file) for file in files) + '\r\n'
                encoded_file_list = file_list.encode('utf-8', errors='replace')
                data_conn.send(encoded_file_list)
                data_conn.close()
                client.send(b'226 Transfer complete.\r\n')
            
            elif command == 'RETR':
                # Retrieve a file
                if data_sock is None:
                    client.send(b'425 Use PORT or PASV first.\r\n')
                    continue
                file_path = os.path.join(current_dir, ' '.join(parts[1:]))
                if os.path.isfile(file_path):
                    data_conn, _ = data_sock.accept()
                    client.send(b'150 Opening data connection.\r\n')
                    with open(file_path, 'rb') as f:
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            data_conn.send(data)
                    data_conn.close()
                    client.send(b'226 Transfer complete.\r\n')
                else:
                    client.send(f'550 "{file_path}" not found.\r\n'.encode()) 
            
            elif command == 'STOR':
                # Store a file
                if data_sock is None:
                    client.send(b'425 Use PORT or PASV first.\r\n')
                    continue
                file_path = os.path.join(current_dir, ' '.join(parts[1:]))
                data_conn, _ = data_sock.accept()
                client.send(b'150 Opening data connection.\r\n')
                try:
                    with open(file_path, 'wb') as f:
                        while True:
                            data = data_conn.recv(1024)
                            if not data:
                                break
                            f.write(data)
                    client.send(b'226 Transfer complete.\r\n')
                except IsADirectoryError:
                    client.send(b'550 Directory not avaialable.\r\n')
                data_conn.close()
            
            elif command == 'DELE':
                # Delete a file
                file_path = os.path.join(current_dir, ' '.join(parts[1:]))
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    client.send(f'250 "file" removed\r\n'.encode())
                else:
                    client.send(f'550 "file" not found.\r\n'.encode())
            
            else:
                client.send(b'500 Unknown command\r\n')

        except error_perm:
            client.send(b'530 Login incorrect.\r\n')
            break
    
    duration = int(time.time() - start_time) 
            
    if ftp_config.config.getboolean('FTP', 'email_alert'):
       ftp_alert.send_email_with_attachment(duration=duration) 
    if data_sock is not None:
        data_sock.close()
    client.close()
