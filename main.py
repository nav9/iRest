from timer import timers
import logging
#from configuration import configHandler
from logging.handlers import RotatingFileHandler
from operatingSystemFunctions import operatingSystemDiversifier
from diskOperations import fileAndFolderOperations

#TODO: Figure out if logger can be part of a class, rather than being a global like this
#logFileName = os.path.join('logs', 'logs.log') #TODO: Shift to config file and take care of the OS compatibility of the folder slash
logFileName = 'logs.log'
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
log = logging.getLogger(__name__)
handler = RotatingFileHandler(logFileName, maxBytes=2000, backupCount=5)#TODO: Shift to config file
handler.formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S') #setting this was necessary to get it to write the format to file. Without this, only the message part of the log would get written to the file
log.addHandler(handler)
log.setLevel(logging.INFO)

#-------------------------------------------------------------
#-------------------------------------------------------------
#------------------ PROGRAM STARTS HERE ----------------------
#-------------------------------------------------------------
#-------------------------------------------------------------
if __name__ == '__main__':
    log.info("\n\n---------------------------------")
    log.info("iRest program started")
    #fileOps = FileOperations()
    operatingSystemCheck = operatingSystemDiversifier.OperatingSystemChecker()
    operatingSystemAdapter = operatingSystemCheck.getOperatingSystemAdapterInstance() 
    #configHandler = configHandler.ConfigurationHandler()
    timers = timers.DefaultTimer()
    timers.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getAudioNotifier()) #TODO: take notifiers from the config file
    timers.registerOperatingSystemAdapter(operatingSystemAdapter)#If OS was not identified, the adapter will be None

    while True:
        timers.decideWhatToDo()
    
    