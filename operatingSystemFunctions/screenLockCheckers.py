import FreeSimpleGUI
import logging
import subprocess
import traceback
from abc import ABC, abstractmethod
from configuration import configHandler
from operatingSystemFunctions import commonFunctions, timeFunctions
from diskOperations import fileAndFolderOperations
from operatingSystemFunctions import commonFunctions

class ScreenLockConstants:
    LOCK_CHECK_INTERVAL_SECONDS = 10 #checking only periodically since it's an expensive operation
    LOCK_CHECK_INTERVAL_SECONDS_EDGE = 30 #checking less often on devices that have lesser processing power

class ScreenLockChecker(ABC):#Abstract parent class
    #Note: Abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def __init__(self):
        #self.id = "someUniqueNotifierName" #has to be implemented in the child class
        pass

    @abstractmethod
    def execute(self):
        """ Checks if the screen is locked. Function returns True if screen is locked. False if not. If screen lock status could not be detected, an error is logged. """
        pass

class GnomeScreenLockCheck(ScreenLockChecker):
    def __init__(self):
        self.id = "Gnome Desktop screen lock checker"
        self.screensaverCommand = "gnome-screensaver-command -q" 
        self.commonFunctions = commonFunctions.CommonFunctions_Linux()
        self.screensaverPresent = self.__isGnomeScreensaverPresent()
        self.lockChecker = timeFunctions.TimeElapseChecker_Linux(ScreenLockConstants.LOCK_CHECK_INTERVAL_SECONDS) #checking only periodically since it's an expensive operation
        self.locked = False

    def execute(self):
        if self.lockChecker.didDurationElapse():
            screenLocked = "is active"
            screenNotLocked = "is inactive"
            receivedOutput = self.commonFunctions.executeBashCommand(self.screensaverCommand)
            if screenLocked in receivedOutput:
                self.locked = True
            else: 
                if screenNotLocked in receivedOutput:
                    self.locked = False
                else:                    
                    callstack = "".join(traceback.format_stack())
                    logging.error(f"SCREENSAVER OUTPUT UNKNOWN. CHECK AND REPROGRAM: {receivedOutput}, Stacktrace {callstack}")   
                    raise Exception("The command to check if the screensaver is active or not seems to have changed. Please check it and reprogram iRest.")                         
            logging.debug(f"SCREEN LOCKED status: {self.locked}")        
        return self.locked

    def __isGnomeScreensaverPresent(self):#Ubuntu does not have the screensaver installed by default
        screenSaverPresent = False
        appName = 'gnome-screensaver'  
        try:                      
            screenSaverPresent = self.commonFunctions.isThisAppInstalled(appName)
        except FileNotFoundError as e:
            screenSaverPresent = False
            logging.error(f"Error encountered: {e}")
        if not screenSaverPresent:
            logging.error("--------- INSTALLATION REQUIRED ---------")                      
            errorMessage = f"{appName} is missing (needed for lock-screen detection). Please install it using 'sudo apt install -y gnome-screensaver' and restart iRest. Stacktrace {traceback.print_stack()}"
            logging.error(errorMessage)
            PySimpleGUI.popup(errorMessage, title="iRest") #TODO: this should result as a message shown in the GUI rather than as a popup here. This line does not help with decopuling the UI
        logging.info(f"{appName} present: {screenSaverPresent}")
        return screenSaverPresent


class CinnamonScreenLockCheck(ScreenLockChecker):#The Cinnamon desktop used in Mint OS
    def __init__(self):
        self.id = "Cinnamon Desktop screen lock checker"
        self.screensaverCommand = "cinnamon-screensaver-command -q" 
        self.commonFunctions = commonFunctions.CommonFunctions_Linux()
        self.lockChecker = timeFunctions.TimeElapseChecker_Linux(ScreenLockConstants.LOCK_CHECK_INTERVAL_SECONDS) #checking only periodically since it's an expensive operation
        self.locked = False

    def execute(self):
        if self.lockChecker.didDurationElapse():
            screenLocked = "is active"
            screenNotLocked = "is inactive"
            receivedOutput = self.commonFunctions.executeBashCommand(self.screensaverCommand)
            if screenLocked in receivedOutput:
                self.locked = True
            else: 
                if screenNotLocked in receivedOutput:
                    self.locked = False
                else:
                    callstack = "".join(traceback.format_stack())
                    logging.error(f"SCREENSAVER OUTPUT UNKNOWN. CHECK AND REPROGRAM: {receivedOutput}. Stacktrace {callstack}")  
                    raise Exception("The command to check if the screensaver is active or not seems to have changed. Please check it and reprogram iRest.")
            logging.debug(f"SCREEN LOCKED status: {self.locked}")        
        return self.locked
    
class RaspberryPiWaylandScreenLockCheck(ScreenLockChecker):
    def __init__(self):
        self.id = "Raspberry Pi Wayland screen lock checker"
        self.folderOps = fileAndFolderOperations.FileOperations() #TODO: see if you can instantiate folderOps globally as a singleton and use it
        self.commonFunc = commonFunctions.CommonFunctions_Linux() #TODO: see if you can instantiate commonFunc globally as a singleton and use it 
        self.lockChecker = timeFunctions.TimeElapseChecker_Linux(ScreenLockConstants.LOCK_CHECK_INTERVAL_SECONDS_EDGE) #checking only periodically since it's an expensive operation
        self.screenLocked = False
        SCREEN_LOCKED_INFO_FILE = ".screen_locked_env" #This filename would be specified in the Raspberry Pi install sh file and/or in the Readme file
        self.pathToScreenLockFile = self.folderOps.joinPathAndFilename(self.folderOps.getUserHomeDirectory(), SCREEN_LOCKED_INFO_FILE)
        self.validScreenLockFilePresent = False #Because the file may get created only once the User manually locks the screen for the first time and there is no need to keep checking once it gets created        
    
    def execute(self):
        if self.lockChecker.didDurationElapse():#duration check is being done here to be able to keep duration checks different for different operating systems or devices
            self.screenLocked = False         
            wlopmOutput = self.commonFunc.executeBashCommand("wlopm -j")
            if '"power-mode": "off"' in wlopmOutput: #---when the screen blanked by going into power save mode on its own
                self.screenLocked = True
            elif self.pathToScreenLockFile:#---when User has manually locked the screen
                if not self.validScreenLockFilePresent:#if the file is not present, check if it got created
                    self.validScreenLockFilePresent = self.folderOps.isValidFile(self.pathToScreenLockFile)
                if self.validScreenLockFilePresent:
                    lines = self.folderOps.readFromFile(self.pathToScreenLockFile)
                    for line in lines:
                        if line.strip() == "export SCREEN_LOCKED=1":
                            self.screenLocked = True
                            break #break out of for                
        return self.screenLocked    
        
#Note: Screen lock checks for various versions of Windows and MacOS can be programmed here
