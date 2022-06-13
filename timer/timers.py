import time
import logging
from abc import ABC, abstractmethod
from diskOperations import timeFileManager

class OtherConstants:
    FIRST_RUN = -999
    
class TimeConstants:
    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60
    HOURS_IN_DAY = 24

class NatureOfActivity:
    EYES_BEING_STRAINED = "eyes_strained"
    SCREEN_LOCKED = "screen_locked"
    TYPING = "typing"
    MOUSE_MOVEMENT = "mouse_movement"

#Note: The program is designed such that multiple timers can be created and run simultaneously. This helps in simultaneously running a Neural Network or any such Machine Learning algorithm which learns from the User's preferences of how much rest they actually need, instead of sticking to pre-defined time intervals
#Note: This abstract class specifies what functions all timers should implement
class RestTimers(ABC): #Abstract parent class
    #Note: Any abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def execute(self):
        """ The function where the program checks to see if the user needs rest or needs to be reminded that the rest period is over """
        pass

    # @abstractmethod
    # def addThisNotifierToListOfNotifiers(self, notifier):
    #     """ To add notifiers like an audio notifier or a text-based notifier or a popup notifier etc. Every notifier should have a notifier id"""
    #     pass

    # @abstractmethod
    # def unregisterNotifier(self, notifier):
    #     """ Remove a notifier from the list of notifiers, based on a notifier id """
    #     pass

    # @abstractmethod
    # def registerOperatingSystemAdapter(self, operatingSystemAdapter): 
    #     """ Register an adapter class that provides functions specific to the operating system that the program is run in """   
    #     pass
    
    # @abstractmethod
    # def registerFileOperationsHandler(self, fileOperationsHandler): 
    #     """ Register a class that provides functions for file and folder operations """   
    #     pass



#Note: This class checks how much time the user worked, whether to notify the User to take rest and whether to notify the User that the rest period has completed. This is just one of the engines which does such processing. You could create a different engine and allow it to work with a different logic.
#Each such class is designed to have its own way of evaluating if the User is strained
class DefaultTimer(RestTimers):#Checks for how much time elapsed and notifies the User
    def __init__(self, operatingSystemAdapter, fileOperationsHandler):#TODO: Load the values from a config file
        self.REST_MINUTES = 5
        self.WORK_MINUTES = 20
        self.allowedStrainDuration = TimeConstants.SECONDS_IN_MINUTE * self.WORK_MINUTES #how long to work (in seconds). How many seconds the eyes can be permitted to be strained
        self.restRatio = self.WORK_MINUTES / self.REST_MINUTES #Five minutes of rest for every 20 minutes of work
        #CAUTION/BUG If the SLEEP_SECONDS value is changed, all old archive files and the time file needs to be deleted, since calculations of strain are based on the assumption that this value is constant across all those files
        self.SLEEP_SECONDS = 10 #how long to sleep before checking system state (in seconds). 
        self.strainedDuration = OtherConstants.FIRST_RUN
        self.lastCheckedTime = time.monotonic()
        self.timeFileManager = timeFileManager.TimeFileManager("timeFiles", "timeFile", fileOperationsHandler) #parameters passed: folderName, fileName
        #self.timeFileManager.registerFileOperationsHandler(fileOperationsHandler)
        self.__checkIfUserIsStrained()
        self.notifiers = {} #references to various objects that can be used to notify the user
        self.operatingSystemAdapter = operatingSystemAdapter #value will be None if no OS was identified
        
    def addThisNotifierToListOfNotifiers(self, notifier):
        if notifier.id not in self.notifiers:#is notifier not already registered here
            logging.info(f"Registering notifier: {notifier.id}")
            self.notifiers[notifier.id] = notifier
        else:
            logging.info(f"{notifier.id} is already registered.")

    def unregisterNotifier(self, notifier):
        if notifier.id in self.notifiers:
            logging.info(f"Deregistering notifier: {notifier.id}")
            del self.notifiers[notifier.id]
        else:
            logging.info(f"No such notifier registered: {notifier.id}")

    # def registerOperatingSystemAdapter(self, operatingSystemAdapter):
    #     self.operatingSystemAdapter = operatingSystemAdapter  

    # def registerFileOperationsHandler(self, fileOperationsHandler):
    #     self.timeFileManager.registerFileOperationsHandler(fileOperationsHandler)
    
    def execute(self):
        time.sleep(self.SLEEP_SECONDS) #relinquish program control to the operating system, for a while
        currentTime = time.time() #epoch time is simply the time elapsed since a specific year (around 1970)
        self.timeFileManager.writeTimeInformationToFile(currentTime, timeFileManager.NatureOfActivity.EYES_BEING_STRAINED) #More data can be added to this list when writing, if necessary        
        self.__checkIfUserIsStrained()
        if self.strainedDuration > self.allowedStrainDuration:#notify the User to take rest
            for notifierID, notifier in self.notifiers.items(): #If operating system was not recognized, the operating system adapter will be None, and no notifier will be registered. It will be an empty dict
                notifier.execute() #within each notifier's execute(), there will be a cooldown timer, which will ensure that the notification is not repeated until some time has passed, even if execute() is invoked frequently

        # time.sleep(self.SLEEP_SECONDS) #relinquish program control to OS
        # if self.operatingSystemAdapter != None: #because the program should be capable of working even if the OS could not be identified
        #     if self.operatingSystemAdapter.isUserRelaxingTheirEyes():   
        #         #---subtract worked time
        #         if self.workedTime > 0:
        #             self.workedTime = abs(self.workedTime - (self.SLEEP_SECONDS / self.restRatio))                    
        #         logging.info(f"Screen locked. Worked time = {self.workedTime}")
        #         return
        # elapsedTime = time.monotonic() - self.lastCheckedTime
        # self.workedTime = self.workedTime + self.SLEEP_SECONDS
        # logging.info(f'Time elapsed: {elapsedTime}s. Worked time: {self.workedTime}s')

    def __checkIfUserIsStrained(self):
        """ Go through historical data and find out how much time the user was strained and how much time user was not strained"""
        #TODO: This function can be made a lot more efficient by reducing the number of calculations

        if self.strainedDuration == OtherConstants.FIRST_RUN:#need to examine past history of stored data since computer may have been restarted
            self.strainedDuration = 0
            previousEpoch = None
            previousActivity = None            
            for timeData in reversed(self.timeFileManager.historicalStrainData):
                epochTime, natureOfActivity = self.timeFileManager.unpackTheTimeData(timeData)
                if natureOfActivity == NatureOfActivity.EYES_BEING_STRAINED:
                    totalStrainTime = totalStrainTime + self.SLEEP_SECONDS
                if previousEpoch:
                    pass
                previousEpoch = epochTime
                previousActivity = natureOfActivity
        else:#simply examine the latest time slice
            pass
                
        