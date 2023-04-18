import socket
import threading
import sys
import os
import time
import smtplib
from email.mime.text import MIMEText

import ftp_config
import ftp_dirgen
from ftp_handler import handle_connection

#----------------------------------------------------------------------------------

def clear_screen():
    """Clears the terminal screen"""
    os.system('clear')
    
#----------------------------------------------------------------------------------    

def ascii_art():
        print(" _        _______  ______            _______ _________ _       _________         ")
        print("( \      (  ___  )(  ___ \ |\     /|(  ____ )\__   __/( (    /|\__   __/|\     /|")
        print("| (      | (   ) || (   ) )( \   / )| (    )|   ) (   |  \  ( |   ) (   | )   ( |")
        print("| |      | (___) || (__/ /  \ (_) / | (____)|   | |   |   \ | |   | |   | (___) |")
        print("| |      |  ___  ||  __ (    \   /  |     __)   | |   | (\ \) |   | |   |  ___  |")
        print("| |      | (   ) || (  \ \    ) (   | (\ (      | |   | | \   |   | |   | (   ) |")
        print("| (____/\| )   ( || )___) )   | |   | ) \ \_____) (___| )  \  |   | |   | )   ( |")
        print("(_______/|/     \||/ \___/    \_/   |/   \__/\_______/|/    )_)   )_(   |/     \|")
        print("\n") #Add lines for spacing


def ascii_admin():
	print("  _______  ______   _______ _________ _          _______  _______  ______   _______ ")
	print(" (  ___  )(  __  \ (       )\__   __/( (    /|  (       )(  ___  )(  __  \ (  ____ \\")
	print(" | (   ) || (  \  )| () () |   ) (   |  \  ( |  | () () || (   ) || (  \  )| (    \/")
	print(" | (___) || |   ) || || || |   | |   |   \ | |  | || || || |   | || |   ) || (__    ")
	print(" |  ___  || |   | || |(_)| |   | |   | (\ \) |  | |(_)| || |   | || |   | ||  __)   ")
	print(" | (   ) || |   ) || |   | |   | |   | | \   |  | |   | || |   | || |   ) || (      ")
	print(" | )   ( || (__/  )| )   ( |___) (___| )  \  |  | )   ( || (___) || (__/  )| (____/\\")
	print(" |/     \|(______/ |/     \|\_______/|/    )_)  |/     \|(_______)(______/ (_______/")
	print("\n")

#----------------------------------------------------------------------------------

def main_menu():
    """Displays the main menu and takes input from user"""
    ascii_art()
    while True:
        #ascii_art()
        print('Main menu:')
        print('1. Start honeypot')
        print('2. Configure honeypot')
        print('3. Help')
        print('4. Exit')

        choice = input('Enter option number > ')

        if choice == '1':
            clear_screen()
            start_honeypot()
            break

        elif choice == '2':
            clear_screen()
            ftp_config.run_menu()

        elif choice == '3':
            clear_screen()
            show_help()         

        elif choice == '4':
            clear_screen()
            sys.exit()

        else:
            clear_screen()
            ascii_art()            
            print('Unknown command. Please enter a number from the menu.')
            print('\n')

#----------------------------------------------------------------------------------

def start_honeypot():
    """Starts the FTP honeypot"""
    host = ftp_config.config.get('FTP', 'ip_address')
    port = 21
    homedir = ftp_config.config.get('FTP', 'home_directory')  # Change this to the directory you want to use for the FTP server

    # Create the directories needed for the FTP server
    generate_directories = ftp_config.config.getboolean('FTP', 'generate_directories')
    
    

    # Create the FTP server socket
    ftp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_sock.bind((host, port))
    ftp_sock.listen(5)

    print(f'FTP honeypot listening on {host}:{port}')
    
    
    if generate_directories:
       ftp_dirgen.create_directories(homedir)

    # Start the input thread
    input_thread = threading.Thread(target=read_input, args=(homedir,))
    input_thread.daemon = True
    input_thread.start()

    # Handle incoming connections
    while True:
        client, addr = ftp_sock.accept()
        print('---------------------------')
        print(f'New connection from {addr}')
        print('---------------------------')
        handle_connection(client, homedir)

#----------------------------------------------------------------------------------

def read_input(homedir):
    while True:
        print('-----------------------------')
        print('Use exit to stop the honeypot')
        cmd = input('> ')

        if cmd == 'exit':
            response = input("Are you sure you want to exit? (y/n): ")
            if response.lower() == 'y':
                if ftp_config.config.getboolean('FTP', 'generate_directories'):
                    ftp_dirgen.remove_directories(None, None, directories=[homedir + '/ftp', homedir + '/downloads', homedir + '/documents'])
                print('Honeypot closed.')    
                os._exit(0)
            else:
                print('Continuing operation.')
        else:
            print('Unknown command. Please enter "exit".')

#----------------------------------------------------------------------------------

def show_help():
    print("FTP Honeypot Help\n")
    print("NAME")
    print("\tLabyrinth - A fake FTP server used to detect and monitor unauthorized access attempts.\n")
    print("DESCRIPTION")
    print("\tLabyrinth is a fake FTP server designed to monitor unauthorized access attempts.")
    print("\tWhen a connection is made to the FTP Honeypot, the server logs the IP address and ")
    print("\tany attempted login credentials.\n")
    print("OPTIONS")
    print("\t1. Start honeypot\n")
    print("\t   Starts the FTP Honeypot server, which listens for incoming connections on the ")
    print("\t   specified IP address and port\n")
    print("\t2. Configure honeypot\n")
    print("\t   Allows the user to configure various settings for the FTP Honeypot, including IP ")
    print("\t   address, pre-defined credentials, and logging settings.\n")
    print("\t3. Help\n")
    print("\t   Displays this help message, which provides an overview of the FTP Honeypot and ")
    print("\t   its available options.\n")
    print("\t4. Exit\n")
    print("\t   Exits the program and stops the FTP Honeypot server.\n")


#----------------------------------------------------------------------------------

if __name__ == '__main__':
    main_menu()

