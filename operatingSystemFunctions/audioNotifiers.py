import os
import time
import logging
import subprocess
from pydub import AudioSegment
from pydub.playback import play
from abc import ABC, abstractmethod
from configuration import configHandler

class AudioNotifier(ABC):#Abstract parent class
    category = configHandler.NotifierConstants.AUDIO_NOTIFIER
    #Note: Abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def __init__(self):
        #self.id = "someUniqueNotifierName" #has to be implemented in the child class
        pass

    @abstractmethod
    def execute(self):
        """ Plays an audio notification to remind the user to take rest. Function does not return anything """
        pass
    
    def toggleNotifierActiveState(self):
        """ Toggles the isActive boolean. Returns the state boolean """
        pass
    # @abstractmethod
    # def notifyUserThatRestPeriodIsOver(self):
    #     """ Plays an audio notification to inform the user that the resting period completed. Function does not return anything """
    #     pass

#TODO: Check if the OS has Speed Say installed
#Note: This is an Ubuntu-specific notifier. Notifications could also be programmed as a simple bell sound etc.
class SpeedSaySpeechNotifier_Linux(AudioNotifier):
    def __init__(self):
        self.id = "Speed Say Notifier"
        self.speechProgram = "spd-say" 
        self.waitUntilFullTextRead = "--wait"
        self.speechRateArg = "-r"
        self.speechRate = "-10" #TODO: should this be part of the config file?
        self.fullCommand = [self.speechProgram, self.waitUntilFullTextRead, self.speechRateArg, self.speechRate]
        self.takeRestMessage = "Please rest now"
        self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION = 120 #After the first audio notification, no more notifications would happen during a cooldown period, even if execute() is called repeatedly
        self.userNotified = False
        self.notifiedTime = None
        self.isActive = True

    def execute(self):#This function may get called multiple times, so it has to take care of not annoying the User with too many notifications. So a cooldown time was used to allow for some time until the next notification
        if not self.isActive:
            return
        #Note: Notification cooling time was used within the class itself (instead of externally) since other notifiers may do notification at their own frequencies
        if self.userNotified:            
            elapsedTime = time.monotonic() - self.notifiedTime
            logging.debug(f"Audio notification cooldown elapsed time: {elapsedTime}. Cooldown seconds: {self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION}")
            if elapsedTime >= self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION:#So actual time until the next notification will be COOLDOWN_SECONDS + number of seconds until execute() is invoked again
                self.userNotified = False            
        else:#notify User
            logging.debug("Audio notifier sending notification")            
            speechCommand = self.fullCommand[:] #shallow copy by value
            speechCommand.append(self.takeRestMessage)
            subprocess.run(speechCommand)
            self.notifiedTime = time.monotonic()
            self.userNotified = True
                       
    def toggleNotifierActiveState(self):
        self.isActive = not self.isActive
        return self.isActive     

class EspeakNotifier_RaspberryPi(AudioNotifier):
    def __init__(self):
        self.id = "Espeak Notifier"
        self.speechProgram = "espeak" 
        self.fullCommand = [self.speechProgram]
        self.takeRestMessage = "Please rest now"
        self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION = 120 #After the first audio notification, no more notifications would happen during a cooldown period, even if execute() is called repeatedly
        self.userNotified = False
        self.notifiedTime = None
        self.isActive = True

    def execute(self):#This function may get called multiple times, so it has to take care of not annoying the User with too many notifications. So a cooldown time was used to allow for some time until the next notification
        if not self.isActive:
            return
        #Note: Notification cooling time was used within the class itself (instead of externally) since other notifiers may do notification at their own frequencies
        if self.userNotified:            
            elapsedTime = time.monotonic() - self.notifiedTime
            logging.debug(f"Audio notification cooldown elapsed time: {elapsedTime}. Cooldown seconds: {self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION}")
            if elapsedTime >= self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION:#So actual time until the next notification will be COOLDOWN_SECONDS + number of seconds until execute() is invoked again
                self.userNotified = False            
        else:#notify User
            logging.debug("Audio notifier sending notification")            
            speechCommand = self.fullCommand[:] #shallow copy by value
            speechCommand.append(self.takeRestMessage)
            subprocess.run(speechCommand)
            self.notifiedTime = time.monotonic()
            self.userNotified = True
                       
    def toggleNotifierActiveState(self):
        self.isActive = not self.isActive
        return self.isActive  

class PydubSoundNotifier_Linux(AudioNotifier): #https://realpython.com/playing-and-recording-sound-python/
    def __init__(self):
        self.id = "Simple Audio Sound Notifier"
        self.soundFolder = "sounds" #TODO: shift to config file
        self.soundFile = os.path.join(self.soundFolder, "timeToTakeRest.mp3") #TODO: shift to config file
        self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION = 60 #After the first audio notification, no more notifications would happen during a cooldown period, even if execute() is called repeatedly
        self.userNotified = False
        self.notifiedTime = None
        self.isActive = True

    def execute(self):#This function may get called multiple times, so it has to take care of not annoying the User with too many notifications. So a cooldown time was used to allow for some time until the next notification
        if not self.isActive:
            return        
        #Note: Notification cooling time was used within the class itself (instead of externally) since other notifiers may do notification at their own frequencies
        if self.userNotified:            
            elapsedTime = time.monotonic() - self.notifiedTime
            logging.debug(f"Sound notification cooldown elapsed time: {elapsedTime}. Cooldown seconds: {self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION}")
            if elapsedTime >= self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION:#So actual time until the next notification will be COOLDOWN_SECONDS + number of seconds until execute() is invoked again
                self.userNotified = False            
        else:#notify User
            logging.debug("Sound notifier sending notification")            
            play(AudioSegment.from_mp3(self.soundFile))
            self.notifiedTime = time.monotonic()
            self.userNotified = True

    def toggleNotifierActiveState(self):
        self.isActive = not self.isActive
        return self.isActive  
