import PySimpleGUI
import logging
import subprocess
from abc import ABC, abstractmethod
from configuration import configHandler

class Constants:
    FIRST_ELEMENT_OF_ARRAY = 0
    SECOND_ELEMENT_OF_ARRAY = 1

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
        self.__isGnomeScreensaverPresent()

    def execute(self):
        theProcess = subprocess.Popen(self.screensaverCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        locked = False
        screenLocked = "is active"
        screenNotLocked = "is inactive"
        receivedOutput = " ".join(str(x) for x in theProcess.stdout.readlines()) #readlines() returns a list. This line converts the list to a string
        if screenLocked in receivedOutput:
            locked = True
        else: 
            if screenNotLocked in receivedOutput:
                locked = False
            else:
                logging.error(f"SCREENSAVER OUTPUT UNKNOWN. CHECK AND REPROGRAM: {receivedOutput}")                            
        logging.debug(f"SCREEN LOCKED status: {locked}")        
        return locked

    def __isThisAppInstalled(self, appName):
        appInstalled = False
        status = subprocess.getstatusoutput("dpkg-query -W -f='${Status}' " + appName)
        if not status[Constants.FIRST_ELEMENT_OF_ARRAY]:
            if 'installed' in status[Constants.SECOND_ELEMENT_OF_ARRAY]:
                appInstalled = True
        return appInstalled

    def __isGnomeScreensaverPresent(self):#Ubuntu does not have the screensaver installed by default
        screenSaverPresent = False
        try:
            app = 'gnome-screensaver'
            logging.info(f"Checking if {app} is installed...")
            screenSaverPresent = self.__isThisAppInstalled(app)
        except FileNotFoundError as e:
            screenSaverPresent = False
            logging.error(f"Error encountered: {e}")
        if not screenSaverPresent:
            logging.info("--------- INSTALLATION REQUIRED ---------")                      
            errorMessage = "Gnome screensaver is missing (needed for lock-screen detection). Please install it using 'sudo apt install -y gnome-screensaver' and restart iRest."
            logging.info(errorMessage)
            PySimpleGUI.popup(errorMessage, title="iRest")            
        logging.info(f"Screensaver present: {screenSaverPresent}")
        return screenSaverPresent


class CinnamonScreenLockCheck(ScreenLockChecker):
    def __init__(self):
        self.id = "Cinnamon Desktop screen lock checker"
        self.screensaverCommand = "cinnamon-screensaver-command -q" 

    def execute(self):
        theProcess = subprocess.Popen(self.screensaverCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        locked = False
        screenLocked = "is active"
        screenNotLocked = "is inactive"
        receivedOutput = " ".join(str(x) for x in theProcess.stdout.readlines()) #readlines() returns a list. This line converts the list to a string
        if screenLocked in receivedOutput:
            locked = True
        else: 
            if screenNotLocked in receivedOutput:
                locked = False
            else:
                logging.error(f"SCREENSAVER OUTPUT UNKNOWN. CHECK AND REPROGRAM: {receivedOutput}")                            
        logging.debug(f"SCREEN LOCKED status: {locked}")        
        return locked
    
#Note: Screen lock checks for various versions of Windows and MacOS can be programmed here