import logging
import subprocess
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