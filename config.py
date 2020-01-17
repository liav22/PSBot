import configparser
import time
import sys

class Config():
    '''Imports bot host info'''
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        if config.get('DEFAULT', 'token') == '' or config.get('DEFAULT', 'prefix') == '':
            print('''Bot cannot start.
                No token / prefix spotted, please edit config.ini accordingly.''')
            time.sleep(6)
            sys.exit()

        self.token: str = config.get('DEFAULT', 'token')
        self.prefix: str = config.get('DEFAULT', 'prefix')
        self.status: str = config.get('DEFAULT', 'status')
        self.owner: str = config.get('DEFAULT', 'owner')
