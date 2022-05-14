import logging
import subprocess
from sys import platform #to check which OS the program is running on
from abc import ABC, abstractmethod

class AudioNotifier(ABC):#Abstract parent class
    #Note: Abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def __init__(self):
        #self.id = "someUniqueNotifierName" #has to be implemented in the child class
        pass

    @abstractmethod
    def notifyUserToTakeRest(self):
        """ Plays an audio notification to remind the user to take rest. Function does not return anything """
        pass

    # @abstractmethod
    # def notifyUserThatRestPeriodIsOver(self):
    #     """ Plays an audio notification to inform the user that the resting period completed. Function does not return anything """
    #     pass

#TODO: Check if the OS has Speed Say installed
#Note: This is an Ubuntu-specific notifier. Notifications could also be programmed as a simple bell sound etc.
class SpeedSayAudioNotifier_Linux(AudioNotifier):
    def __init__(self):
        self.id = "Speed Say Notifier"
        self.speechProgram = "spd-say" 
        self.waitUntilFullTextRead = "--wait"
        self.speechRateArg = "-r"
        self.speechRate = "-10" #TODO: should this be part of the config file?
        self.fullCommand = [self.speechProgram, self.waitUntilFullTextRead, self.speechRateArg, self.speechRate]
        self.takeRestMessage = "Take rest now"
        
    def notifyUserToTakeRest(self):
        speechCommand = self.fullCommand[:] #shallow copy by value
        speechCommand.append(self.takeRestMessage)
        subprocess.run(speechCommand)

class OperatingSystemFunctionality(ABC):#Abstract parent class
    #Note: Abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def isUserRelaxingTheirEyes(self):#This can be checked via various techniques. Screen lock or inactivity etc.
        """ Returns True if the User is relaxing their eyes. False otherwise"""
        pass

    @abstractmethod
    def getAudioNotifier(self):
        """ Returns a reference to the audio notification instance created for a particular operating system"""
        pass    

class LinuxFunctionality(OperatingSystemFunctionality):#For functions that are specific to Linux. The program uses this class only if it detects it is running on Linux. These same functions should also be available in a "Windows" class and that class would be instantiatiated and used if the program is run on Windows
    def __init__(self):  
        self.encoding = 'utf-8'
        self.gnomeScreensaverPresent = self.__isGnomeScreensaverPresent()
        self.audioNotifier = SpeedSayAudioNotifier_Linux()
    
    def isUserRelaxingTheirEyes(self):#Interface function (compulsory to implement)
        return self.__isScreenLocked()

    def getAudioNotifier(self):
        return self.audioNotifier
    
    #---
    
    def __isScreenLocked(self):
        theProcess = subprocess.Popen('gnome-screensaver-command -q | grep "is active"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        locked = False
        if len(theProcess.stdout.readlines()) > 0:
            locked = True
        return locked

    def __isGnomeScreensaverPresent(self):
        screenSaverPresent = False
        while not screenSaverPresent:
            try:
                response = subprocess.Popen(['gnome-screensaver'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout, stderr = response.communicate()
                if stderr != None:
                    logging.error("Error during check for Gnome screensaver: ", stderr)                                        
                stdoutConverted = stdout.decode(self.encoding)
                if 'not found' in stdoutConverted:                     
                    screenSaverPresent = False
                if 'screensaver already running' in stdoutConverted: 
                    screenSaverPresent = True
                    logging.info("Gnome screensaver detected. Lock-screen detection will work fine.")
            except FileNotFoundError as e:
                screenSaverPresent = False
            if not screenSaverPresent:
                logging.info("--------- INSTALLATION ---------")                      
                logging.info("Gnome screensaver is missing (needed for lock-screen detection). It needs your permission to install it...")
                screensaverInstallCommands = ['sudo', 'apt', 'install', '-y', 'gnome-screensaver'] 
                #logging.info("Running this command: ", ' '.join(screensaverInstallCommands))
                response = subprocess.Popen(screensaverInstallCommands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
                response.wait()  
                #logging.info("Installing...")           

        return screenSaverPresent

# class OperatingSystemID:#This might eventually need more elaborate ID codes based on flavours of Linux or versions of Windows etc.
#     LINUX = 0
#     WINDOWS = 1
#     MAC = 2

class OperatingSystemChecker:    
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

    def __isThisProgramRunningInLinux(self):
        #return 'Linux' in platform.platform() #Does the string returned by platform() contain the substring "Linux"? For example, in Ubuntu, the output is: 'Linux-5.11.0-27-generic-x86_64-with-glibc2.10'
        return platform == "linux" or platform == "linux2"

    def __isThisProgramRunningInWindows(self):
        return platform == "win32"

    def __isThisProgramRunningInMac(self):
        return platform == "darwin"
        
    def getOperatingSystemAdapterInstance(self):#A class instance which provides OS-specific functions
        return self.operatingSystemAdapter #will return None if OS was not identified, and that's ok because this program's functions check for this None. The program is designed to work even without OS-specific functionality
