import subprocess
from sys import platform #to check which OS the program is running on
from abc import ABC, abstractmethod


#TODO: Check if the OS has Speed Say installed
#Note: This is an Ubuntu-specific 
class AudioNotifier_Linux:
    def __init__(self):
        self.id = "Speed Say Notifier"
        self.speechProgram = "spd-say" 
        self.waitUntilFullTextRead = "--wait"
        self.speechRateArg = "-r"
        self.speechRate = "-10" #TODO: should this be part of the config file?
        self.fullCommand = [self.speechProgram, self.waitUntilFullTextRead, self.speechRateArg, self.speechRate]
        self.takeRestMessage = "Take rest now"
        
    def takeRestNotification(self):
        speechCommand = self.fullCommand[:] #shallow copy by value
        speechCommand.append(self.takeRestMessage)
        subprocess.run(speechCommand)

class OperatingSystemFunctionality(ABC):#Parent class
    @abstractmethod
    def isScreenLocked(self):
        pass

    @abstractmethod
    def getAudioNotifier(self):
        pass    

class LinuxFunctionality(OperatingSystemFunctionality):#For functions that are specific to Linux. The program uses this class only if it detects it is running on Linux. These same functions should also be available in a "Windows" class and that class would be instantiatiated and used if the program is run on Windows
    def __init__(self):  
        self.encoding = 'utf-8'
        self.gnomeScreensaverPresent = self.__isGnomeScreensaverPresent()
        self.audioNotifier = AudioNotifier_Linux()
    
    def isScreenLocked(self):#Interface function (compulsory to implement)
        theProcess = subprocess.Popen('gnome-screensaver-command -q | grep "is active"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        locked = False
        if len(theProcess.stdout.readlines()) > 0:
            locked = True
        return locked

    def getAudioNotifier(self):
        return self.audioNotifier

    def __isGnomeScreensaverPresent(self):
        screenSaverPresent = False
        while not screenSaverPresent:
            try:
                response = subprocess.Popen(['gnome-screensaver'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout, stderr = response.communicate()
                if stderr != None:
                    print("Error during check for Gnome screensaver: ", stderr)                                        
                stdoutConverted = stdout.decode(self.encoding)
                if 'not found' in stdoutConverted:                     
                    screenSaverPresent = False
                if 'screensaver already running' in stdoutConverted: 
                    screenSaverPresent = True
                    print("Gnome screensaver detected. Lock-screen detection will work fine.")
            except FileNotFoundError as e:
                screenSaverPresent = False
            if not screenSaverPresent:
                print("--------- INSTALLATION ---------")                      
                print("Gnome screensaver is missing (needed for lock-screen detection). It needs your permission to install it...")
                screensaverInstallCommands = ['sudo', 'apt', 'install', '-y', 'gnome-screensaver'] 
                #print("Running this command: ", ' '.join(screensaverInstallCommands))
                response = subprocess.Popen(screensaverInstallCommands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
                response.wait()  
                #print("Installing...")           

        return screenSaverPresent

# class OperatingSystemID:#This might eventually need more elaborate ID codes based on flavours of Linux or versions of Windows etc.
#     LINUX = 0
#     WINDOWS = 1
#     MAC = 2

class OperatingSystemChecker:    
    def __init__(self):
        #self.currentOperatingSystem = None
        self.operatingSystemAdapter = None
        print("Current OS platform: ", platform)
        if self.__isThisProgramRunningInLinux():            
            #self.currentOperatingSystem = OperatingSystemID.LINUX
            self.operatingSystemAdapter = LinuxFunctionality()
            print("Linux detected")
        if self.__isThisProgramRunningInWindows():
            #self.currentOperatingSystem = OperatingSystemID.WINDOWS
            print("Windows detected")
        if self.__isThisProgramRunningInMac():
            #self.currentOperatingSystem = OperatingSystemID.MAC
            print("MacOS detected")

    def __isThisProgramRunningInLinux(self):
        #return 'Linux' in platform.platform() #Does the string returned by platform() contain the substring "Linux"? For example, in Ubuntu, the output is: 'Linux-5.11.0-27-generic-x86_64-with-glibc2.10'
        return platform == "linux" or platform == "linux2"

    def __isThisProgramRunningInWindows(self):
        return platform == "win32"

    def __isThisProgramRunningInMac(self):
        return platform == "darwin"
        
    def getOperatingSystemAdapterInstance(self):#A class instance which provides OS-specific functions
        return self.operatingSystemAdapter #will return None if OS was not identified, and that's ok because this program's functions check for this None. The program is designed to work even without OS-specific functionality
