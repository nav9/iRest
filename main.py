"""
A program that helps remind users to take rest breaks. For more 
information, see the readme file and license file.
"""

from timer import timers
import logging
from configuration import configHandler
from logging.handlers import RotatingFileHandler
from operatingSystemFunctions import operatingSystemDiversifier
from diskOperations import fileAndFolderOperations

logFileName = 'logs.log'
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#log = logging.getLogger(__name__)
handler = RotatingFileHandler(logFileName, maxBytes=2000, backupCount=2)#TODO: Shift to config file
handler.formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S') #setting this was necessary to get it to write the format to file. Without this, only the message part of the log would get written to the file
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

#-------------------------------------------------------------
#-------------------------------------------------------------
#------------------ PROGRAM STARTS HERE ----------------------
#-------------------------------------------------------------
#-------------------------------------------------------------
if __name__ == '__main__':
    logging.info("\n\n---------------------------------")
    logging.info("iRest program started")
    config = configHandler.ConfigurationHandler()
    fileOps = fileAndFolderOperations.FileOperations()
    operatingSystemCheck = operatingSystemDiversifier.OperatingSystemChecker()
    operatingSystemAdapter = operatingSystemCheck.getOperatingSystemAdapterInstance() 
    allTimers = []
    defaultTimer = timers.DefaultTimer()
    defaultTimer.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getAudioNotifier()) #TODO: take notifiers from the config file
    defaultTimer.registerOperatingSystemAdapter(operatingSystemAdapter) #If OS was not identified, the adapter will be None
    defaultTimer.registerFileOperationsHandler(fileOps)

    logging.info("Monitoring time ...")

    while True:
        for timer in allTimers:
            timer.execute()
    
    