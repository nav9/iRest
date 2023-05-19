import logging
import subprocess
import PySimpleGUI
import sys
from sys import platform #to check which OS the program is running on
from abc import ABC, abstractmethod
from operatingSystemFunctions import audioNotifiers
from operatingSystemFunctions import graphicalNotifiers

class Constants:
    FIRST_ELEMENT_OF_ARRAY = 0
    SECOND_ELEMENT_OF_ARRAY = 1

class OperatingSystemFunctionality(ABC):#Abstract parent class
    #Note: Abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def isScreenLocked(self):#This can be checked via various techniques. Screen lock or inactivity etc.
        """ Returns True if the User is relaxing their eyes. False otherwise """
        pass

    @abstractmethod
    def getAudioNotifier(self):
        """ Returns a reference to the audio notification instance created for a particular operating system """
        pass    

class LinuxFunctionality(OperatingSystemFunctionality):#For functions that are specific to Linux. The program uses this class only if it detects it is running on Linux. These same functions should also be available in a "Windows" class and that class would be instantiatiated and used if the program is run on Windows
    def __init__(self):  
        self.encoding = 'utf-8'
        self.gnomeScreensaverPresent = self.__isGnomeScreensaverPresent()
        #TODO: code needs to be written to dynamically switch to any other notifier
        self.audioNotifier = audioNotifiers.SpeedSaySpeechNotifier_Linux()
        self.graphicalNotifier = graphicalNotifiers.PlyerGraphicalNotifier()
    
    def isScreenLocked(self):
        return self.__isScreenLocked()

    def getAudioNotifier(self):
        return self.audioNotifier

    def getGraphicalNotifier(self):
        return self.graphicalNotifier
    
    def __isScreenLocked(self):
        theProcess = subprocess.Popen('gnome-screensaver-command -q', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
                logging.error(f"GNOME SCREENSAVER OUTPUT UNKNOWN. CHECK AND REPROGRAM: {receivedOutput}")                            
        logging.debug(f"SCREEN LOCKED status: {locked}")        
        return locked
    
    def __isThisAppInstalled(self, appName):
        appInstalled = False
        status = subprocess.getstatusoutput("dpkg-query -W -f='${Status}' " + appName)
        if not status[Constants.FIRST_ELEMENT_OF_ARRAY]:
            if 'installed' in status[Constants.SECOND_ELEMENT_OF_ARRAY]:
                appInstalled = True
        return appInstalled

    def __isGnomeScreensaverPresent(self):
        screenSaverPresent = False
        #while not screenSaverPresent:
        try:
            app = 'gnome-screensaver'
            logging.info(f"Checking if {app} is installed...")
            screenSaverPresent = self.__isThisAppInstalled(app)
            #response = subprocess.Popen(['gnome-screensaver'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #stdout, stderr = response.communicate()
            #if stderr != None:
            #    logging.error("Error during check for Gnome screensaver: ", stderr)                                        
            #stdoutConverted = stdout.decode(self.encoding)
            #logging.info(f"stdout is {stdoutConverted}")
            #logging.info(f"stderr is {stderr}")
            #if 'not found' in stdoutConverted:                     
            #    screenSaverPresent = False
            #if 'screensaver already running' in stdoutConverted: 
            #    screenSaverPresent = True
            #    logging.info("Gnome screensaver detected. Lock-screen detection will work fine.")
        except FileNotFoundError as e:
            screenSaverPresent = False
            logging.error(f"Error encountered: {e}")
        if not screenSaverPresent:
            logging.info("--------- INSTALLATION REQUIRED ---------")                      
            errorMessage = "Gnome screensaver is missing (needed for lock-screen detection). Please install it using 'sudo apt install -y gnome-screensaver'"
            logging.info(errorMessage)
            PySimpleGUI.popup(errorMessage, title="iRest")
            #sys.exit()
            #screensaverInstallCommands = ['sudo', 'apt', 'install', '-y', 'gnome-screensaver'] 
            #logging.info("Running this command: ", ' '.join(screensaverInstallCommands))
            #response = subprocess.Popen(screensaverInstallCommands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
            #response.wait()  
            #logging.info("Installing...")           
        logging.info(f"Screensaver present: {screenSaverPresent}")
        return screenSaverPresent

# class OperatingSystemID:#This might eventually need more elaborate ID codes based on flavours of Linux or versions of Windows etc.
#     LINUX = 0
#     WINDOWS = 1
#     MAC = 2

class OperatingSystemIdentifier:    
    def __init__(self):
        #self.currentOperatingSystem = None
        self.operatingSystemAdapter = None
        logging.info(f"Current OS platform: {platform}")
        if self.__isThisProgramRunningInLinux():            
            #self.currentOperatingSystem = OperatingSystemID.LINUX
            self.operatingSystemAdapter = LinuxFunctionality()
            logging.info("Linux detected")
        if self.__isThisProgramRunningInWindows():
            #self.currentOperatingSystem = OperatingSystemID.WINDOWS
            logging.info("Windows detected")
        if self.__isThisProgramRunningInMac():
            #self.currentOperatingSystem = OperatingSystemID.MAC
            logging.info("MacOS detected")
        if self.operatingSystemAdapter == None:
            logging.warn("Operating system could not be identified. Functionality like lock screen detection won't work.")

    def __isThisProgramRunningInLinux(self):
        #return 'Linux' in platform.platform() #Does the string returned by platform() contain the substring "Linux"? For example, in Ubuntu, the output is: 'Linux-5.11.0-27-generic-x86_64-with-glibc2.10'
        return platform == "linux" or platform == "linux2"

    def __isThisProgramRunningInWindows(self):
        return platform == "win32"

    def __isThisProgramRunningInMac(self):
        return platform == "darwin"
        
    def getOperatingSystemAdapterInstance(self):#A class instance which provides OS-specific functions
        """ Will return None if OS was not identified, and that's ok because this program's functions check for this None. The program is designed to work even without OS-specific functionality """
        return self.operatingSystemAdapter 
