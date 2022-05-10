import configparser
from configparser import ConfigParser
# import logging
# from logging.handlers import RotatingFileHandler

# #TODO: There is some better way to use the log file handler creation. Using logger's inbuilt parent-child relationship. Find out.
# logFileName = os.path.join('logs', 'logs.log') #TODO: Shift to config file and take care of the OS compatibility of the folder slash
# logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# log = logging.getLogger(__name__)
# handler = RotatingFileHandler(logFileName, maxBytes=2000, backupCount=5)#TODO: Shift to config file
# handler.formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S') #setting this was necessary to get it to write the format to file. Without this, only the message part of the log would get written to the file
# log.addHandler(handler)
# log.setLevel(logging.INFO)

class ConfigurationHandler:
    def __init__(self):
        self.configFilename = "iRestConfig.ini"        
        self.config = configparser.ConfigParser()        
        self.checkIfConfigFileExists()

    def checkIfConfigFileExists(self):
        configFileFound = True
        #try:
        self.config.read(self.configFilename)
        logging.info(self.config.sections)
        #except:
            #configFileFound = False

    def setConfigFor(self):
        config['default'] = {
        "host" : "192.168.1.1",
        "port" : "22",
        "username" : "username",
        "password" : "password"
    }