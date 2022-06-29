import configparser
import logging
import time
from utils.structure import stream
from datetime import datetime

# Set up log file, it would be saved to log/
now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.basicConfig(filename='log/' + now_time + '.txt', level=logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

# Log current time
logging.info('Current time: %s' % (now_time))

# Read session cookie (need to be updated by hand through login the system)
config_cred = configparser.ConfigParser()
config_cred.read('confidential/session.cred')
credential = config_cred['Creator_session']['session_cookie']

# Read configuration file
config = configparser.ConfigParser()
config.read('config_online.ini')

for indicator in config.sections():
    logging.info("Working on the indicator %s ......" %(indicator))

    Stream = stream(logging, credential, now_time, 'states/indicator_states.csv')
    Stream.load_config(config[indicator])
    Stream.process()

    if Stream.flag_loader_ready:
        Stream.fun_save_hist()
        Stream.create_indicator()
        time.sleep(3)

        Stream.fun_save_ongoing()
        Stream.update_indicator()
        time.sleep(3)
