import PySimpleGUI
import logging
import subprocess
from abc import ABC, abstractmethod
from configuration import configHandler
from operatingSystemFunctions import commonFunctions

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

    def execute(self):
        locked = False
        screenLocked = "is active"
        screenNotLocked = "is inactive"
        receivedOutput = self.commonFunctions.executeBashCommand(self.screensaverCommand)
        if screenLocked in receivedOutput:
            locked = True
        else: 
            if screenNotLocked in receivedOutput:
                locked = False
            else:
                logging.error(f"SCREENSAVER OUTPUT UNKNOWN. CHECK AND REPROGRAM: {receivedOutput}")                            
        logging.debug(f"SCREEN LOCKED status: {locked}")        
        return locked

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
            errorMessage = f"{appName} is missing (needed for lock-screen detection). Please install it using 'sudo apt install -y gnome-screensaver' and restart iRest."
            logging.error(errorMessage)
            PySimpleGUI.popup(errorMessage, title="iRest") #TODO: this should result as a message shown in the GUI rather than as a popup here. This line does not help with decopuling the UI
        logging.info(f"{appName} present: {screenSaverPresent}")
        return screenSaverPresent


class CinnamonScreenLockCheck(ScreenLockChecker):
    def __init__(self):
        self.id = "Cinnamon Desktop screen lock checker"
        self.screensaverCommand = "cinnamon-screensaver-command -q" 
        self.commonFunctions = commonFunctions.CommonFunctions_Linux()

    def execute(self):
        locked = False
        screenLocked = "is active"
        screenNotLocked = "is inactive"
        receivedOutput = self.commonFunctions.executeBashCommand(self.screensaverCommand)
        if screenLocked in receivedOutput:
            locked = True
        else: 
            if screenNotLocked in receivedOutput:
                locked = False
            else:
                logging.error(f"SCREENSAVER OUTPUT UNKNOWN. CHECK AND REPROGRAM: {receivedOutput}")                            
        #logging.debug(f"SCREEN LOCKED status: {locked}")        
        return locked
    
#Note: Screen lock checks for various versions of Windows and MacOS can be programmed here