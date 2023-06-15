"""
A program that helps remind users to take rest breaks. For more 
information, see the readme file and license file.
"""
import sys
from time import sleep

sys.dont_write_bytecode = True #Prevents the creation of some annoying cache files and folders. This line has to be present before all the other imports: https://docs.python.org/3/library/sys.html#sys.dont_write_bytecode and https://stackoverflow.com/a/71434629/453673 

import logging
from timer import timers
from configuration import configHandler
from logging.handlers import RotatingFileHandler
from operatingSystemFunctions import operatingSystemDiversifier
from diskOperations import fileAndFolderOperations
from diskOperations import timeFileManager
from gui import simpleGUI

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
    SLEEP_SECONDS = 0.01
    logging.info("\n\n---------------------------------")
    logging.info("iRest program started")
    #---Initialize helper classes
    config = configHandler.ConfigurationHandler()
    fileOps = fileAndFolderOperations.FileOperations()
    operatingSystemCheck = operatingSystemDiversifier.OperatingSystemIdentifier()
    operatingSystemAdapter = operatingSystemCheck.getOperatingSystemAdapterInstance() #If OS could not be identified, it will return None    
    #---Create the timer(s)
    allTimers = []
    timeFileManager = timeFileManager.TimeFileManager(configHandler.Names.ARCHIVE_FOLDER, configHandler.Names.TIME_FILE, fileOps) #parameters passed: folderName, fileName
    defaultTimer = timers.DefaultTimer(operatingSystemAdapter, timeFileManager)
    if operatingSystemAdapter:#if OS was identified, get the audio notifier specific to that OS
        defaultTimer.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getAudioNotifier()) #TODO: take notifiers from the config file
        defaultTimer.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getGraphicalNotifier()) #TODO: take notifiers from the config file
    allTimers.append(defaultTimer)
    #---Initialize the main GUI interface
    gui = simpleGUI.MainInterface()
    gui.addThisBackend(operatingSystemAdapter.getWarmthAppAdapterReference())
    gui.addThisBackend(defaultTimer) #backends can be timers or other classes too which need a GUI representation    
    gui.createLayout()
    logging.info("Monitoring time ...")

    while True:
        for timer in allTimers:
            timer.execute()
        if gui.checkIfNotClosedGUI(): gui.runEventLoop()
        else: break
        sleep(SLEEP_SECONDS) #relinquish program control to the operating system, for a while
    logging.info("iRest has been stopped")
    
    
