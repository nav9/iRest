import os
import time
import logging
from abc import ABC, abstractmethod

#Note: This abstract class specifies what functions all timers should implement
class RestTimers(ABC):#Abstract parent class
    #Any abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def decideWhatToDo(self):
        """ The function where the program checks to see if the user needs rest or needs to be reminded that the rest period is over """
        pass

    @abstractmethod
    def addThisNotifierToListOfNotifiers(self, notifier):
        """ To add notifiers like an audio notifier or a text-based notifier or a popup notifier etc. Every notifier should have a notifier id"""
        pass

    @abstractmethod
    def unregisterNotifier(self, notifier):
        """ Remove a notifier from the list of notifiers, based on a notifier id """
        pass

    @abstractmethod
    def registerOperatingSystemAdapter(self, operatingSystemAdapter): 
        """ Register an adapter class that provides functions specific to the operating system that the program is run in """   
        pass

#Note: This class checks how much time the user worked, whether to notify the user to take rest and whether to notify the user that the rest period has completed. This is just one of the engines which does such processing. You could create a different engine and allow it to work with a different logic.
class DefaultTimer(RestTimers):#Checks for how much time elapsed and notifies the User
    def __init__(self):#TODO: Load the values from a config file
        self.workInterval = 60 * 20 #how long to work (in seconds)
        self.restRatio = 20 / 5 #Five minutes of rest for every 20 minutes of work
        self.sleepDuration = 10 #how long to sleep before checking system state (in seconds)
        self.workedTime = 0
        self.lastCheckedTime = time.monotonic()
        self.notifiers = {} #references to various objects that can be used to notify the user
        self.operatingSystemAdapter = None
        
    def addThisNotifierToListOfNotifiers(self, notifier):
        if notifier.id not in self.notifiers:#is notifier not already registered here
            logging.info(f"Registering notifier: {notifier.id}")
            self.notifiers[notifier.id] = notifier
        else:
            logging.info(f'{notifier.id} is already registered.')

    def unregisterNotifier(self, notifier):
        if notifier.id in self.notifiers:
            logging.info(f"Deregistering notifier: {notifier.id}")
            del self.notifiers[notifier.id]
        else:
            logging.info(f"No such notifier registered: {notifier.id}")

    def registerOperatingSystemAdapter(self, operatingSystemAdapter):
        self.operatingSystemAdapter = operatingSystemAdapter            

    def decideWhatToDo(self):
        time.sleep(self.sleepDuration)
        if self.operatingSystemAdapter != None:#because the program should work on any OS
            if self.operatingSystemAdapter.isUserRelaxingTheirEyes():   
                if self.workedTime > 0:
                    self.workedTime = abs(self.workedTime - (self.sleepDuration / self.restRatio))                    
                logging.info(f"Screen locked. Worked time = {self.workedTime}")
                return
        elapsedTime = time.monotonic() - self.lastCheckedTime
        self.workedTime = self.workedTime + self.sleepDuration
        logging.info(f'Time elapsed: {elapsedTime}s. Worked time: {self.workedTime}')
        if self.workedTime >= self.workInterval:
            self.lastCheckedTime = time.monotonic()
            for notifierID, notifierRef in self.notifiers.items(): #If operating system was not recognized, the operating system adapter will be None, and no notifier will be registered
                notifierRef.takeRestNotification()
                

        