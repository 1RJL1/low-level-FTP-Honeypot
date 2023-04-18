import os
import shutil
import signal


def create_directories(homedir):
    # Create a list of directories to create
    directories = ['ftp', 'downloads', 'documents']

    # Create the directories
    for directory in directories:
        os.mkdir(os.path.join(homedir, directory))

    print('Directories created:', directories)
    
    with open(os.path.join(homedir, 'ftp', 'confidential.txt'), 'w') as f:
        f.write('This is a confidential file.\nPlease do not distribute.')
    with open(os.path.join(homedir, 'downloads', 'taxes2022.doc'), 'w') as f:
        f.write('Tax information for the year 2022.')
    with open(os.path.join(homedir, 'documents', 'client_list.txt'), 'w') as f:
        f.write('List of clients and their contact information.\nPlease keep confidential.')

    print('Files created in directories:', directories)
    
    return directories


def remove_directories(signal, frame, directories):
    for directory in directories:
        shutil.rmtree(directory)
    print('Directories cleaned up, honeypot closed.')
    os._exit(0)



if __name__ == '__main__':
    homedir = '/home/reece/Honeypot/honeypotv2/2'
    directories = create_directories(homedir)

    # Register the signal handler to remove directories when the script is terminated
    signal.signal(signal.SIGINT, lambda signal, frame: signal_handler(signal, frame, directories))

    # Wait for the script to be terminated
    while True:
        try:
          input("Press Ctrl+C to stop the script...")
        except KeyboardInterrupt:
              signal_handler(signal.SIGINT, None)


