import logging

def setup_logger():
    logger = logging.getLogger('ftp_logger')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs all commands
    fh = logging.FileHandler('ftp_log.txt')
    fh.setLevel(logging.DEBUG)

    # create formatter and add it to the handler
    formatter = logging.Formatter('[%(asctime)s] Attacker IP: %(client_ip)s |  Command: %(command)s | Input: %(input_str)s')

    fh.setFormatter(formatter)

    # add the handler to the logger
    logger.addHandler(fh)
    return logger

logger = setup_logger()

def log_command(command, client_ip, input_str):
    logger.debug('', extra={'client_ip': client_ip, 'command': command, 'input_str': input_str})

