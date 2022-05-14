import logging
import configparser
#from configparser import ConfigParser

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
        pass
    #     config['default'] = {
    #     "host" : "192.168.1.1",
    #     "port" : "22",
    #     "username" : "username",
    #     "password" : "password"
    # }