import psutil
import logging
import traceback
import subprocess
import FreeSimpleGUI
from abc import ABC, abstractmethod
from configuration import configHandler
from diskOperations import fileAndFolderOperations
from operatingSystemFunctions import commonFunctions
from operatingSystemFunctions import commonFunctions, timeFunctions

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
        self.absolutePathToExecutable = 'exe' #various other attributes can be specified in process_iter, like pid, name, ppid, status, username, etc.
        self.lockscreenGreeter = "/usr/sbin/pi-greeter"
        self.validScreenLockFilePresent = False #Because the file may get created only once the User manually locks the screen for the first time and there is no need to keep checking once it gets created        
    
    def execute(self):
        if self.lockChecker.didDurationElapse():#duration check is being done here to be able to keep duration checks different for different operating systems or devices
            self.screenLocked = False                     
            if self.__isScreenBlanked() or self.__isScreenLocked():
                self.screenLocked = True
        return self.screenLocked   
        
    def __isScreenBlanked(self):
        wlopmOutput = self.commonFunc.executeBashCommand("wlopm -j") #wlopm is Wayland output power management
        if '"power-mode": "off"' in wlopmOutput:
            return True
        return False
        
    def __isScreenLocked(self):
        for proc in psutil.process_iter([self.absolutePathToExecutable]):
            try:
                if proc.info[self.absolutePathToExecutable] and proc.info[self.absolutePathToExecutable] == self.lockscreenGreeter:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False 
           
#Note: Screen lock checks for various versions of Windows and MacOS can be programmed here
