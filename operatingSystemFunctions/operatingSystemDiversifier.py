import logging
import subprocess
from sys import platform #to check which OS the program is running on
from abc import ABC, abstractmethod
from diskOperations import fileAndFolderOperations
from operatingSystemFunctions import audioNotifiers
from operatingSystemFunctions import graphicalNotifiers
from operatingSystemFunctions import screenLockCheckers
from operatingSystemFunctions import warmColour
from operatingSystemFunctions import timeFunctions

class OperatingSystemIdentifier:    
    def __init__(self):
        #self.currentOperatingSystem = None
        self.folderOps = fileAndFolderOperations.FileOperations()
        self.operatingSystemAdapter = None
        logging.info(f"Current OS platform: {platform}")
        if self.__isThisProgramRunningInRaspberryPi():            
            self.operatingSystemAdapter = RaspberryPiFunctionality()
            logging.info("Raspberry Pi detected") 
        elif self.__isThisProgramRunningInLinux():            
            #self.currentOperatingSystem = OperatingSystemID.LINUX
            self.operatingSystemAdapter = LinuxFunctionality()
            logging.info("Linux detected")
        elif self.__isThisProgramRunningInWindows():
            #self.currentOperatingSystem = OperatingSystemID.WINDOWS
            logging.info("Windows detected")
        elif self.__isThisProgramRunningInMac():
            #self.currentOperatingSystem = OperatingSystemID.MAC
            logging.info("MacOS detected")
        elif self.operatingSystemAdapter == None:
            logging.warn("Operating system could not be identified. Certain functionality won't be available. You could raise an issue to inform the author about which operating system you are using this program.")

    def __isThisProgramRunningInRaspberryPi(self):
        isRaspberryPi = False
        fileToSearch = '/sys/firmware/devicetree/base/model'
        if self.folderOps.isValidFile(fileToSearch):
            lines = self.folderOps.readFromFile(fileToSearch)
            for line in lines:
                if 'raspberry pi' in line.lower(): 
                    isRaspberryPi = True
        return isRaspberryPi
        
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


#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
# Interface functions for functionality that would be different for
# various operating systems
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
class OperatingSystemFunctionality(ABC):#Abstract parent class
    #Note: Abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def isScreenLocked(self):#This can be checked via various techniques. Screen lock or inactivity etc.
        """ Returns True if the User is relaxing their eyes (which means that it can be programmed to mean that the screen is actually locked or to mean that the User may not be using the mouse and keyboard for an extended period of time). Returns False otherwise """
        pass

    @abstractmethod
    def getAudioNotifier(self):
        """ Returns a reference to the audio notification instance created for a particular operating system """
        pass    

    @abstractmethod
    def getGraphicalNotifier(self):
        """ Returns a reference to the graphical notification instance created for a particular operating system """
        pass 

    @abstractmethod
    def getWarmthAppAdapterReference(self):
        """ Returns a reference to the instance that handles the colour temperature / warmth / night light in the backend """
        pass     

    @abstractmethod
    def getTimeFunctionsApp(self):
        """ Returns a reference to the instance that handles time functions that may or may not be operating system specific """
        pass 

    @abstractmethod
    def getTimeElapseCheckerInstanceForThisDuration(self, duration):
        """ Returns an operating system specific instance which allows checking if a certain duration of time has elapsed """
        pass 

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# These interfaces are for functions specific to operating systems. If any operating system has
# a different desktop with nuanced functionality, there are Desktop Adapter classes which are
# meant to handle such nuances
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class LinuxFunctionality(OperatingSystemFunctionality):#For functions that are specific to Linux. The program uses this class only if it detects it is running on Linux. These same functions should also be available in a "Windows" class and that class would be instantiatiated and used if the program is run on Windows
    #cat /etc/os-release prints the Linux flavour
    def __init__(self):  
        self.encoding = 'utf-8'
        #TODO: code needs to be written to dynamically switch to any other notifier
        self.audioNotifier = audioNotifiers.SpeedSaySpeechNotifier_Linux()
        self.graphicalNotifier = graphicalNotifiers.PlyerGraphicalNotifier()
        self.desktopAdapter = LinuxDesktopAdapter() #To select between the different functionality that Gnome or Cinnamon or any other Linux desktop offers
        self.warmthApp = warmColour.WarmColour_Linux()
        self.timeFunctions = timeFunctions.TimeFunctions_Linux()
    
    def isScreenLocked(self):
        return self.desktopAdapter.isScreenLocked()

    def getAudioNotifier(self):
        return self.audioNotifier

    def getGraphicalNotifier(self):
        return self.graphicalNotifier
    
    def getWarmthAppAdapterReference(self):
        return self.warmthApp
    
    def getTimeFunctionsApp(self):
        return self.timeFunctions
    
    def getTimeElapseCheckerInstanceForThisDuration(self, duration):
        return timeFunctions.TimeElapseChecker_Linux(duration)
    
class RaspberryPiFunctionality(OperatingSystemFunctionality):#For functions that are specific to Raspberry Pi 
    def __init__(self):  
        self.encoding = 'utf-8'
        #TODO: code needs to be written to dynamically switch to any other notifier
        self.audioNotifier = audioNotifiers.EspeakNotifier_RaspberryPi()
        self.graphicalNotifier = graphicalNotifiers.WfPanelRaspberryPiNotifier()
        self.desktopAdapter = RaspberryPiDesktopAdapter() #To select between functionality that differs between Wayland or X11 or any other desktop on Raspberry Pi
        self.warmthApp = None
        self.timeFunctions = timeFunctions.TimeFunctions_Linux()
    
    def isScreenLocked(self):
        screenLocked = False
        if self.desktopAdapter:#is not None
            screenLocked = self.desktopAdapter.isScreenLocked()
        return screenLocked

    def getAudioNotifier(self):
        return self.audioNotifier

    def getGraphicalNotifier(self):
        return self.graphicalNotifier
    
    def getWarmthAppAdapterReference(self):
        return self.warmthApp
    
    def getTimeFunctionsApp(self):
        return self.timeFunctions
    
    def getTimeElapseCheckerInstanceForThisDuration(self, duration):
        return timeFunctions.TimeElapseChecker_Linux(duration)    
    


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# These classes help take care of nuances that specific desktop types on operating systems or 
# specific versions of operating systems require
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class LinuxDesktops:#Note: all strings should be in lower case, since the desktop name received from the OS is converted to lower case
    GNOME = "gnome"
    CINNAMON = "cinnamon"
    WAYLAND = "wlroots" #wayland is actually a compositor
    #TODO: add X11 too for Raspberry Pi 

#This class is meant for Linux OS Desktops like Gnome desktop, Cinnamon, Xfce, KDE or Mate
class LinuxDesktopAdapter:
    def __init__(self):
        self.screenLockChecker = None
        desktopName = self.__getDesktopName()    
        #---assign handler based on the desktop detected    
        if LinuxDesktops.GNOME in desktopName:            
            self.screenLockChecker = screenLockCheckers.GnomeScreenLockCheck()            
        if LinuxDesktops.CINNAMON in desktopName:
            self.screenLockChecker = screenLockCheckers.CinnamonScreenLockCheck()
        if self.screenLockChecker == None:
            logging.warn("\n\n\nDesktop could not be identified. Functionality like lock screen detection may not work. Please find out what Desktop you currently have, and program it's lock screen detection into iRest.\n\n\n")
        else:
            logging.info(f"{desktopName} desktop detected")

    def isScreenLocked(self):
        screenLocked = False
        if self.screenLockChecker != None:
            screenLocked = self.screenLockChecker.execute()
        return screenLocked
    
    def __getDesktopName(self):#TODO such a Popen function is in commonFunctions.py
        command = "echo $XDG_CURRENT_DESKTOP" #command that queries for the desktop name
        theProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        receivedOutput = " ".join(str(x) for x in theProcess.stdout.readlines()) #readlines() returns a list. This line converts the list to a string
        logging.debug(f"{receivedOutput} desktop name received from OS")
        receivedOutput = receivedOutput.lower()
        return receivedOutput

#This class is meant for the Raspbian (Raspberry Pi OS) graphical desktop
class RaspberryPiDesktopAdapter:
    def __init__(self):
        self.folderOps = fileAndFolderOperations.FileOperations()
        SCREEN_LOCKED_FILE = ".screen_locked_env" #This filename would be specified in the Raspberry Pi install sh file and/or in the Readme file
        self.screenLockChecker = None
        desktopName = self.__getDesktopName()    
        self.pathToScreenLockFile = None
        self.validScreenLockFilePresent = False #Because the file may get created only once the User manually locks the screen for the first time and there is no need to keep checking once it gets created
        #---assign handler based on the desktop detected    
        if LinuxDesktops.WAYLAND in desktopName:            
            logging.info("\n\n\nRaspberry Pi Wayland detected. Screen lock/blank detection will be available only if you followed the Raspberry pi install instructions.\n\n\n")         
            self.pathToScreenLockFile = self.folderOps.joinPathAndFilename(self.folderOps.getUserHomeDirectory(), SCREEN_LOCKED_FILE)
        else:#TODO: Add functionality for X11 on RPi too
            logging.info(f"Raspberry Pi {desktopName} desktop detected. Some functionality like screen lock/blank may not be available.")        

    def isScreenLocked(self):
        screenLocked = False 
        if self.pathToScreenLockFile:
            if not self.validScreenLockFilePresent:#if the file is not present, check if it got created
                self.validScreenLockFilePresent = self.folderOps.isValidFile(self.pathToScreenLockFile)
            if self.validScreenLockFilePresent:
                lines = self.folderOps.readFromFile(self.pathToScreenLockFile)
                for line in lines:
                    if line.strip() == "export SCREEN_LOCKED=1":
                        screenLocked = True
                        break #break out of for                
        return screenLocked
    
    def __getDesktopName(self):#TODO such a Popen function is in commonFunctions.py
        command = "echo $XDG_CURRENT_DESKTOP" #command that queries for the desktop name
        theProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        receivedOutput = " ".join(str(x) for x in theProcess.stdout.readlines()) #readlines() returns a list. This line converts the list to a string
        logging.debug(f"{receivedOutput} desktop name received from OS")
        receivedOutput = receivedOutput.lower()
        return receivedOutput
        
#If some desktop that is not supported is detected, iRest should still work with the bare minimum functionality, so this adapter is needed        
class UnknownDesktopAdapter:
    def __init__(self):
        self.screenLockChecker = None
        logging.info("\n\n\nUnknown desktop type. Proceeding with minimal functionality\n\n\n")         

    def isScreenLocked(self):
        return False #Since screenlock checks need a specific function, and here we do not know which operating system this is

