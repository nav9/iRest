import logging
import configparser
#from configparser import ConfigParser

class NotifierConstants:
    AUDIO_NOTIFIER = "audioNotifier"
    GRAPHICAL_NOTIFIER = "graphicalNotifier"
    
class GlobalConstants:
    LAST_INDEX_OF_LIST = -1
    FIRST_INDEX_OF_LIST = 0    

class Names:#Note: These names may have to be made specific to specific timers
    ARCHIVE_FOLDER = "timeFiles-iRest"
    TIME_FILE = "timeFile"    

# TODO: Config handler will be programmed when users other than the author of this program need it.
#https://stackoverflow.com/questions/19078170/python-how-would-you-save-a-simple-settings-config-file
#https://stackoverflow.com/questions/54915574/python-configparser-use-defaults-if-not-in-configuration-file
# class ConfigurationHandler:
#     def __init__(self):
#         self.configFilename = "iRestConfig.ini"        
#         self.config = configparser.ConfigParser()        
#         self.checkIfConfigFileExists()

#     def checkIfConfigFileExists(self):
#         configFileFound = True
#         #try:
#         self.config.read(self.configFilename)
#         #logging.info(self.config.sections)
#         #except:
#             #configFileFound = False

#     def setConfigFor(self):
#         pass
