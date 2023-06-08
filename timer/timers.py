import time
import logging
from abc import ABC, abstractmethod
from diskOperations import timeFileManager
from gui import simpleGUI
from configuration import configHandler

class OtherConstants:
    PROGRAM_JUST_STARTED = -999
    LAST_INDEX_OF_LIST = -1
    PENULTIMATE_INDEX_OF_LIST = -2
    FIRST_INDEX_OF_LIST = 0    
    
class TimeConstants:
    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60
    HOURS_IN_DAY = 24
    ONE_SECOND = 1
    

class NatureOfActivity:
    EYES_BEING_STRAINED = "eyes_strained"
    SCREEN_LOCKED = "screen_locked"
    TYPING = "typing"
    MOUSE_MOVEMENT = "mouse_movement"
    WATCHING_VIDEO = "watching_video"
    


#Note: The program is designed such that multiple timers can be created and run simultaneously. This helps in simultaneously running a Neural Network or any such Machine Learning algorithm which learns from the User's preferences of how much rest they actually need, instead of sticking to pre-defined time intervals
#Note: This abstract class specifies what functions all timers should implement
class RestTimers(ABC): #Abstract parent class
    #Note: Any abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def execute(self):
        """ The function where the program checks to see if the user needs rest or needs to be reminded that the rest period is over """
        pass

    @abstractmethod
    def getGUIRef(self):
        """ This function needs to be implemented but can be left empty if there's no GUI for the backend. Returns a reference to the GUI instance """
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
    def __init__(self, operatingSystemAdapter, fileOperationsHandler, archiveFolderName, timeFileName):#TODO: Load the values from a config file
        self.REST_MINUTES = 5 #TODO: shift to config file
        self.WORK_MINUTES = 20 #TODO: shift to config file
        self.allowedStrainDuration = TimeConstants.SECONDS_IN_MINUTE * self.WORK_MINUTES #how long to work (in seconds). How many seconds the eyes can be permitted to be strained
        self.restRatio = self.WORK_MINUTES / self.REST_MINUTES #Five minutes of rest for every 20 minutes of work
        logging.debug(f"RestRatio={self.restRatio} = work minutes {self.WORK_MINUTES} * rest minutes {self.REST_MINUTES}")
        #CAUTION/BUG If the SLEEP_SECONDS value is changed, all old archive files and the time file needs to be deleted, since calculations of strain are based on the assumption that this value is constant across all those files. This can be mitigated by storing the sleep time value when writing timestamps to the file each time
        self.CHECKING_INTERVAL = 10 #how long to sleep before checking system state (in seconds).  #TODO: shift to config file
        self.strainedDuration = OtherConstants.PROGRAM_JUST_STARTED
        self.lastCheckedTime = time.time()
        self.timeFileManager = timeFileManager.TimeFileManager(archiveFolderName, timeFileName, fileOperationsHandler) #parameters passed: folderName, fileName
        #self.timeFileManager.registerFileOperationsHandler(fileOperationsHandler)       
        self.notifiers = {} #references to various objects that can be used to notify the user
        self.operatingSystemAdapter = operatingSystemAdapter #value will be None if no OS was identified
        self.GUI_Layout = simpleGUI.DefaultTimerLayout(self)
        self.userPausedTimerViaGUI = False
        self.__checkIfUserIsStrained(OtherConstants.PROGRAM_JUST_STARTED)  #the zero is the elapsed strain time     
        
    def getWarmthAppReference(self):
        return self.operatingSystemAdapter.getWarmthApp()
    
    def getGUIRef(self):
        return self.GUI_Layout
    
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

    def togglePauseStrainedTimeMeasurement(self):
        self.userPausedTimerViaGUI = not self.userPausedTimerViaGUI
        return self.userPausedTimerViaGUI
    
    def toggleAllAudioNotifiers(self):
        toggleState = None
        for notifierID, notifier in self.notifiers.items():
            if notifier.category == configHandler.NotifierConstants.AUDIO_NOTIFIER:
                toggleState = notifier.toggleNotifierActiveState()
        return toggleState
        
    def execute(self):
        currentTime = time.time() #epoch time is simply the time elapsed since a specific year (around 1970)
        if self.userPausedTimerViaGUI:#if the user paused the timer via the GUI
            self.lastCheckedTime = currentTime
            return
        elapsedTime = abs(self.lastCheckedTime - currentTime)
        if elapsedTime < self.CHECKING_INTERVAL:            
            return #not yet time to do any checks, so let other modules get their share of processing time            
        else:#the necessary time has elapsed, so now check if the user needs to rest
            self.lastCheckedTime = currentTime 
        screenLocked = False
        logging.debug(f"OS adapter: {self.operatingSystemAdapter}")
        if self.operatingSystemAdapter != None: #because the program should be capable of working even if the OS could not be identified
            screenLocked = self.operatingSystemAdapter.isScreenLocked()            
        if screenLocked: #screen lock situation is currently being considered the equivalent of suspend or shutdown, so no need to write to file
            logging.info(f"Screen locked: {currentTime}")
            #self.timeFileManager.writeTimeInformationToFile(currentTime, NatureOfActivity.SCREEN_LOCKED) 
        else:
            #Note: For now, only NatureOfActivity.EYES_BEING_STRAINED is being written to file. Things like NatureOfActivity.SCREEN_LOCKED are not considered, since the strain duration can be determined even without them
            logging.debug(f"Strained currentTime: {currentTime}, nature: {NatureOfActivity.EYES_BEING_STRAINED}")
            self.timeFileManager.writeTimeInformationToFile(currentTime, NatureOfActivity.EYES_BEING_STRAINED) #More data can be added to this list when writing, if necessary                    
            self.__checkIfUserIsStrained(elapsedTime)

    def __checkIfUserIsStrained(self, elapsedTime):
        """ Go through historical data and find out how much time the user was strained and how much time user was not strained"""
        #TODO: The examination of past time data needs to be more intelligent
        if len(self.timeFileManager.historicalStrainData) == 0:
            self.strainedDuration = 0
            return
        if self.strainedDuration == OtherConstants.PROGRAM_JUST_STARTED or len(self.timeFileManager.historicalStrainData) == 1:#need to examine past history of stored data since computer may have been restarted
            self.strainedDuration = 0
            logging.debug(f"Program just started. Examining all data in deque. historicalStrainData length: {len(self.timeFileManager.historicalStrainData)}")          
            print(f'len of historical strain data: {len(self.timeFileManager.historicalStrainData)}')
            self.__calculateStrainedDurationFromDataLoadedFromFiles()
        else: #program is already running, so simply examine the latest time slice
            logging.debug(f"Examining only the latest time slice. historicalStrainData length: {len(self.timeFileManager.historicalStrainData)}")  
            currentTimestamp, natureOfActivity = self.timeFileManager.unpackTheTimeData(self.timeFileManager.historicalStrainData[OtherConstants.LAST_INDEX_OF_LIST])
            if natureOfActivity == NatureOfActivity.EYES_BEING_STRAINED:
                self.__addStrain(elapsedTime)
            if len(self.timeFileManager.historicalStrainData) > 1:#there are at least two elements in the queue
                previousTimestamp, previousActivity = self.timeFileManager.unpackTheTimeData(self.timeFileManager.historicalStrainData[OtherConstants.PENULTIMATE_INDEX_OF_LIST])
                #logging.debug(f"Historical data: " + str(self.timeFileManager.historicalStrainData))
                #logging.debug(f"curr" + str(currentTimestamp))
                #logging.debug(f"prev" + str(previousTimestamp))
                timeDifference = abs(currentTimestamp - previousTimestamp) #value in seconds
                logging.debug(f"checking if prev time {previousTimestamp} - current time: {currentTimestamp} = {timeDifference} > sleep seconds: {self.CHECKING_INTERVAL}+1={self.CHECKING_INTERVAL+TimeConstants.ONE_SECOND}")
                if previousActivity == NatureOfActivity.EYES_BEING_STRAINED and timeDifference > elapsedTime + TimeConstants.ONE_SECOND:
                    self.__subtractStrain(timeDifference - elapsedTime)  
        self.__notifyUserIfTheyNeedToTakeRest()  

    def __calculateStrainedDurationFromDataLoadedFromFiles(self):
        previousTimestamp = None
        previousActivity = None 
        elapsedTime = 0
        totalTimeExamined = 0       
        logging.debug(f"len: {len(self.timeFileManager.historicalStrainData)}"); print(f"len: {len(self.timeFileManager.historicalStrainData)}")
        for timeData in reversed(self.timeFileManager.historicalStrainData):#iterates backward, to consider the latest data that was written, first
            logging.debug(f"Examining time data: {str(timeData)}"); print(f"Examining time data: {str(timeData)}")
            currentTimestamp, natureOfActivity = self.timeFileManager.unpackTheTimeData(timeData)
            if previousTimestamp == None: #first timestamp being considered
                logging.debug(f"Considering initial (last) timestamp in deque. currentTimestamp {currentTimestamp}, natureOfActivity {natureOfActivity}")
                print(f"Considering initial (last) timestamp in deque. currentTimestamp {currentTimestamp}, natureOfActivity {natureOfActivity}")
                if natureOfActivity == NatureOfActivity.EYES_BEING_STRAINED:
                    self.__addStrain(self.CHECKING_INTERVAL)
                else:
                    if natureOfActivity == NatureOfActivity.SCREEN_LOCKED:
                        self.__subtractStrain(self.CHECKING_INTERVAL)
                previousTimestamp = currentTimestamp
                previousActivity = natureOfActivity
                elapsedTime = self.CHECKING_INTERVAL
            else:#the remaining timestamps
                elapsedTime = abs(currentTimestamp - previousTimestamp)
                logging.debug(f"currentTimestamp {currentTimestamp}, natureOfActivity {natureOfActivity}, elapsedTime {elapsedTime}")
                print(f"currentTimestamp {currentTimestamp}, natureOfActivity {natureOfActivity}, elapsedTime {elapsedTime}")                
                if natureOfActivity == NatureOfActivity.EYES_BEING_STRAINED:#add strained time
                    self.__addStrain(elapsedTime)
                    #---check if user had rested between current time and previous time. If yes, take into account the rested time by reducing the strained value
                    timeDifference = abs(currentTimestamp-previousTimestamp) #value in seconds
                    logging.debug(f"Checking if prev time {previousTimestamp} - current time: {currentTimestamp} = {timeDifference} > sleep seconds: {self.CHECKING_INTERVAL}+1={self.CHECKING_INTERVAL+TimeConstants.ONE_SECOND}")
                else:
                    if previousActivity == NatureOfActivity.SCREEN_LOCKED:
                        self.__subtractStrain(elapsedTime) 
                previousTimestamp = currentTimestamp
                previousActivity = natureOfActivity
            totalTimeExamined += elapsedTime
            logging.debug(f"Strained time {self.strainedDuration}, timeExamined {totalTimeExamined}"); print(f"Strained time {self.strainedDuration}, timeExamined {totalTimeExamined}")
            #---stop examining the past if a sufficient amount of time has been analyzed (for example, if the difference of the first and second timestamps are one hour, there's no need to examine more time slices, since it's obvious the User got an hour's rest already)
            #TODO: write some code after determining how much time is sufficient time that's analyzed        

    def __addStrain(self, elapsedTime):
        logging.debug(f"+++ Adding strain of {elapsedTime}s to strained duration {self.strainedDuration}")
        self.strainedDuration = self.strainedDuration + elapsedTime      

    def __subtractStrain(self, restDuration):
        logging.debug(f"--- Rested duration: {restDuration}s. Subtracting {restDuration * self.restRatio} from strained duration {self.strainedDuration}")
        self.strainedDuration = self.strainedDuration - (restDuration * self.restRatio)
        if self.strainedDuration < 0: 
            self.strainedDuration = 0

    def __notifyUserIfTheyNeedToTakeRest(self):
        logging.debug("-----> Current strained time: " + time.strftime("%H:%M:%S", time.gmtime(self.strainedDuration)))
        if self.strainedDuration > self.allowedStrainDuration: #notify the User to take rest
            logging.info(f"* Please take rest. Strained duration: {self.strainedDuration}")
            for notifierID, notifier in self.notifiers.items(): #If operating system was not recognized, the operating system adapter will be None, and no notifier will be registered. It will be an empty dict
                notifier.execute() #within each notifier's execute(), there will be a cooldown timer, which will ensure that the notification is not repeated until some time has passed, even if execute() is invoked frequently        

    def getStrainDetails(self):
        return self.strainedDuration, time.strftime("%Hh %Mm %Ss", time.gmtime(self.allowedStrainDuration)), time.strftime("%Hh %Mm %Ss", time.gmtime(self.strainedDuration))

#----------------------------------------------------
#----------------------------------------------------
#----------------------------------------------------

#TODO: Ideas for other possible timers
class VideoAndRSI_AwareTimer(RestTimers):#Does not increase strain duration too fast if User might be watching a video. Is aware of mouse clicks and keyboard presses, so takes into account RSI (Repetitive Strain Injury)
    def __init__():
        pass

class NeuralNetworkTimer(RestTimers):#Asks the User and learns patterns of when the User is tired, so that strain is customized to the User
    def __init__():
        pass    

    
