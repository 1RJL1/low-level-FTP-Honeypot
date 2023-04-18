import configparser
import netifaces
import ftp_honeypot2
import time
import os
import subprocess

config = configparser.ConfigParser()
config.read('config.ini')

def change_ip_address():
    interfaces = netifaces.interfaces()
    available_ips = []
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for link in addresses[netifaces.AF_INET]:
                if 'broadcast' in link:
                    available_ips.append(link['addr'])
    
    if not available_ips:
        print('No available IP addresses found on the network.')
        return
    
    print('Available IP addresses:')
    for i, ip in enumerate(available_ips):
        print(f'{i + 1}. {ip}')
    
    selection = input('Enter the number of the IP address you want to use: ')
    try:
        selected_ip = available_ips[int(selection) - 1]
    except (ValueError, IndexError):
        print('Invalid selection.')
        return
    
    config.set('FTP', 'ip_address', selected_ip)
    with open('config.ini', 'w') as f:
        config.write(f)
    print("\n")    
    print(f'IP address changed to {selected_ip}.')
    

def toggle_directory_generation():
    current_setting = config.getboolean('FTP', 'generate_directories')
    new_setting = not current_setting
    config.set('FTP', 'generate_directories', str(new_setting))
    with open('config.ini', 'w') as f:
        config.write(f)
    if new_setting:
        print('Directory generation enabled.')
        print("\n")
    else:
        print('Directory generation disabled.')
        print("\n")

def change_login_credentials():
    username = input('Enter new username: ')
    password = input('Enter new password: ')
    config.set('login', 'username', username)
    config.set('login', 'password', password)
    with open('config.ini', 'w') as f:
        config.write(f)
    print("\n")    
    print(f'Login credentials changed to {username}:{password}.')
    
    
def change_home_directory():
    homedir = input('Enter the new home directory: ')

    if not os.path.exists(homedir):
        print("\n")
        print(f'Directory "{homedir}" does not exist.')
        
        return

    config.set('FTP', 'home_directory', homedir)

    with open('config.ini', 'w') as f:
        config.write(f)
    print("\n")
    print(f'Home directory changed to {homedir}.')
       

def clear_ftp_log():
    confirm = input('Are you sure you want to clear the log? (y/n) ')
    if confirm.lower() == 'y':
        with open('ftp_log.txt', 'w') as f:
            f.write('')
        print("\n")    
        print('Log cleared.')
    else:
        print("\n")
        print('Log clearing cancelled.')

def toggle_email_alert():
    current_setting = config.getboolean('FTP', 'email_alert')
    new_setting = not current_setting
    config.set('FTP', 'email_alert', str(new_setting))
    with open('config.ini', 'w') as f:
        config.write(f)
    if new_setting:
        print('Email alerts enabled.')
        print("\n")
    else:
        print('Email alerts disabled.')
        print("\n")
 
def admin_mode():
    ftp_honeypot2.ascii_admin()
    while True:
        print('Admin Mode:')
        print('1. View config.ini')
        print('2. Edit config.ini')
        print('3. Exit')
        
        cmd = input('> ')
        
        if cmd == '1':
            # Read and print the contents of config.ini
            with open('config.ini', 'r') as f:
                print(f.read())
        
        elif cmd == '2':
            # Open the config.ini file using nano editor
            subprocess.run(['nano', 'config.ini'])
            ftp_honeypot2.clear_screen()
            print('Configuration updated.')
        
        elif cmd == '3':
            print('Exiting configuration mode.')
            break
        
        else:
            print('Unknown command. Please enter a number between 1 and 3.')
  

def print_menu():
    ftp_honeypot2.ascii_art()
    print('Configuration menu:')
    print('1. Change IP address		2. Toggle directory generation')
    print('3. Change login credentials	4. Set home directory')
    print('5. Clear log file		6. Toggle email alert')
    print('7. Return to main menu		8. Admin Mode [Use with Caution]')
    
def handle_choice(choice):
    if choice == '1':
        ftp_honeypot2.clear_screen()
        change_ip_address()
        input("Press enter to return...")
    elif choice == '2':
        #ftp_honeypot2.clear_screen()
        toggle_directory_generation()
        input("Press enter to return...")
    elif choice == '3':
        ftp_honeypot2.clear_screen()
        change_login_credentials()
        input("Press enter to return...")
    elif choice == '4':
        change_home_directory()
        input("Press enter to return...")
    elif choice == '5':
        clear_ftp_log()
        input("Press enter to return...")
    elif choice == '6':
        toggle_email_alert()
        input("Press enter to return...")
    elif choice == '7':
        ftp_honeypot2.clear_screen()
        ftp_honeypot2.main_menu()
    elif choice == '8':
        ftp_honeypot2.clear_screen()
        admin_mode()    
    else:
        print('Unknown option.')

def run_menu():
    while True:
        ftp_honeypot2.clear_screen()
        print_menu()
        choice = input('Enter option number > ')
        handle_choice(choice)

