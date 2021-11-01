#!/usr/bin/env python

import time
import sched
import subprocess

class LinuxFunctions:
    def __init__(self):  
        self.encoding = 'utf-8'
        self.gnomeScreensaverPresent = self.isGnomeScreensaverPresent()
                  
    def isScreenLocked(self):
        p = subprocess.Popen('gnome-screensaver-command -q | grep "is active"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        locked = False
        if len(p.stdout.readlines()) > 0:
            locked = True
        return locked

    def isGnomeScreensaverPresent(self):
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
                print("Running this command: ", ' '.join(screensaverInstallCommands))
                response = subprocess.Popen(screensaverInstallCommands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
                response.wait()  
                print("Installing...")           

        return screenSaverPresent
    
    def isGnomeScreensaverInstalled(self):
        return self.gnomeScreensaverIsInstalled

    def isThisProgramRunningInLinux(self):
        return 'Linux' in platform.platform() #Does the string returned by platform() contain the substring "Linux"? For example, in Ubuntu, the output is: 'Linux-5.11.0-27-generic-x86_64-with-glibc2.10'


class AudioNotifier:
    def __init__(self):
        self.id = "Speed Say Notifier"
        self.speechProgram = "spd-say"
        self.waitUntilFullTextRead = "--wait"
        self.speechRateArg = "-r"
        self.speechRate = "-10"
        self.fullCommand = [self.speechProgram, self.waitUntilFullTextRead, self.speechRateArg, self.speechRate]
        self.takeRestMessage = "Take rest now"
        
    def takeRestNotification(self):
        speechCommand = self.fullCommand[:] #shallow copy by value
        speechCommand.append(self.takeRestMessage)
        subprocess.run(speechCommand)
        

class Timer:
    def __init__(self):
        self.workInterval = 60 * 20 #how long to work (in seconds)
        self.restRatio = 20 / 5 #Five minutes of rest for every 20 minutes of work
        self.sleepDuration = 10 #how long to sleep before checking system state (in seconds)
        self.workedTime = 0
        self.lastCheckedTime = time.monotonic()
        self.notifiers = {} #references to various objects that can be used to notify the user
        self.systemAdapter = None
        
    def registerNotifier(self, notifier):
        if notifier.id not in self.notifiers:
            print("Registering notifier: ", notifier.id)
            self.notifiers[notifier.id] = notifier
        else:
            print(notifier.id, 'is already registered.')

    def unregisterNotifier(self, notifier):
        if notifier.id in self.notifiers:
            print("Deregistering notifier: ", notifier.id)
            del self.notifiers[notifier.id]
        else:
            print("No such notifier registered: ", notifier)
            
    def check(self):
        time.sleep(self.sleepDuration)
        if self.systemAdapter != None:
            if self.systemAdapter.isScreenLocked():   
                if self.workedTime > 0:
                    self.workedTime = abs(self.workedTime - (self.sleepDuration / self.restRatio))                    
                print("Screen locked. Worked time = ", self.workedTime)
                return
        elapsedTime = time.monotonic() - self.lastCheckedTime
        self.workedTime = self.workedTime + self.sleepDuration
        print('Time elapsed: ', elapsedTime, 's. Worked time: ', self.workedTime)
        if self.workedTime >= self.workInterval:
            self.lastCheckedTime = time.monotonic()
            for notifierID, notifierRef in self.notifiers.items():
                notifierRef.takeRestNotification()
                
    def registerSystemAdapter(self, systemAdapter):
        self.systemAdapter = systemAdapter


#------------------------------------------
#------------ PROGRAM START ---------------
#------------------------------------------

if __name__ == '__main__':
    systemAdapter = LinuxFunctions()
    audioNotification = AudioNotifier()    
    timer = Timer()
    timer.registerNotifier(audioNotification)
    timer.registerSystemAdapter(systemAdapter)

    while True:
        timer.check()
    
    
