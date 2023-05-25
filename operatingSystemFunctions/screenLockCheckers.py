import os
import logging
import subprocess
from abc import ABC, abstractmethod
from configuration import configHandler

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