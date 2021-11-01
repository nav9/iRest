#!/usr/bin/env python

import time
import sched
import subprocess

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
        self.sleepDuration = 10 #how long to sleep before checking system state (in seconds)
        self.lastCheckedTime = time.monotonic()
        self.notifiers = {} #references to various objects that can be used to notify the user
        
    def registerNotifier(self, notifier):
        if notifier.id not in self.notifiers:
            print("Registering notifier: ", notifier.id, notifier)
            self.notifiers[notifier.id] = notifier
        else:
            print(notifier.id, 'is already registered.')

    def unregisterNotifier(self, notifier):
        if notifier.id in self.notifiers:
            print("Deregistering notifier: ", notifier.id, notifier)
            del self.notifiers[notifier.id]
        else:
            print("No such notifier registered: ", notifier)
            
    def check(self):
        time.sleep(self.sleepDuration)
        elapsedTime = time.monotonic() - self.lastCheckedTime
        print('Time elapsed: ', elapsedTime)
        if elapsedTime >= self.workInterval:
            self.lastCheckedTime = time.monotonic()
            for notifierID, notifierRef in self.notifiers.items():
                notifierRef.takeRestNotification()


#------------------------------------------
#------------ PROGRAM START ---------------
#------------------------------------------

if __name__ == '__main__':
    audioNotification = AudioNotifier()    
    timer = Timer()
    timer.registerNotifier(audioNotification)

    while True:
        timer.check()
    
    
