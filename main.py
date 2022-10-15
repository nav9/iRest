"""
A program that helps remind users to take rest breaks. For more 
information, see the readme file and license file.
"""
import sys

sys.dont_write_bytecode = True #Prevents the creation of some annoying cache files and folders. This line has to be present before all the other imports: https://docs.python.org/3/library/sys.html#sys.dont_write_bytecode and https://stackoverflow.com/a/71434629/453673 

import logging
from timer import timers
from configuration import configHandler
from logging.handlers import RotatingFileHandler
from operatingSystemFunctions import operatingSystemDiversifier
from diskOperations import fileAndFolderOperations

#TODO: shift log file config to file
logFileName = 'logs_iRest.log'
loggingLevel = logging.INFO
logging.basicConfig(level=loggingLevel, format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S') #outputs to console
#log = logging.getLogger(__name__)
handler = RotatingFileHandler(logFileName, maxBytes=2000000, backupCount=2)#TODO: Shift to config file
handler.formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S') #setting this was necessary to get it to write the format to file. Without this, only the message part of the log would get written to the file
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(loggingLevel)

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
    operatingSystemCheck = operatingSystemDiversifier.OperatingSystemIdentifier()
    operatingSystemAdapter = operatingSystemCheck.getOperatingSystemAdapterInstance() #If OS could not be identified, it will return None
    allTimers = []
    defaultTimer = timers.DefaultTimer(operatingSystemAdapter, fileOps)
    if operatingSystemAdapter:#if OS was identified, get the audio notifier specific to that OS
        defaultTimer.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getAudioNotifier()) #TODO: take notifiers from the config file
        defaultTimer.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getGraphicalNotifier()) #TODO: take notifiers from the config file
    allTimers.append(defaultTimer)

    logging.info("Monitoring time ...")

    while True:
        for timer in allTimers:
            timer.execute()
    
    
