import logging
import subprocess
from sys import platform #to check which OS the program is running on
from abc import ABC, abstractmethod
from operatingSystemFunctions import audioNotifiers
from operatingSystemFunctions import graphicalNotifiers
from operatingSystemFunctions import screenLockCheckers
from operatingSystemFunctions import warmColour

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

    @abstractmethod
    def getGraphicalNotifier(self):
        """ Returns a reference to the graphical notification instance created for a particular operating system """
        pass 

    @abstractmethod
    def getWarmthAppAdapterReference(self):
        """ Returns a reference to the instance that handles the colour temperature / warmth / night light in the backend """
        pass     

class LinuxFunctionality(OperatingSystemFunctionality):#For functions that are specific to Linux. The program uses this class only if it detects it is running on Linux. These same functions should also be available in a "Windows" class and that class would be instantiatiated and used if the program is run on Windows
    #cat /etc/os-release prints the Linux flavour
    def __init__(self):  
        self.encoding = 'utf-8'
        #TODO: code needs to be written to dynamically switch to any other notifier
        self.audioNotifier = audioNotifiers.SpeedSaySpeechNotifier_Linux()
        self.graphicalNotifier = graphicalNotifiers.PlyerGraphicalNotifier()
        self.desktopAdapter = LinuxDesktopAdapter()
        self.warmthApp = warmColour.WarmColour_Linux()
    
    def isScreenLocked(self):
        return self.desktopAdapter.isScreenLocked()

    def getAudioNotifier(self):
        return self.audioNotifier

    def getGraphicalNotifier(self):
        return self.graphicalNotifier
    
    def getWarmthAppAdapterReference(self):
        return self.warmthApp
    
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

class LinuxDesktops:#Note: all strings should be in lower case, since the desktop name received from the OS is converted to lower case
    GNOME = "gnome"
    CINNAMON = "cinnamon"

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
    
    def __getDesktopName(self):
        command = "echo $XDG_CURRENT_DESKTOP" #command that queries for the desktop name
        theProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        receivedOutput = " ".join(str(x) for x in theProcess.stdout.readlines()) #readlines() returns a list. This line converts the list to a string
        logging.debug(f"{receivedOutput} desktop name received from OS")
        receivedOutput = receivedOutput.lower()
        return receivedOutput

