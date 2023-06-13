import time
import logging
from abc import ABC, abstractmethod
from gui import simpleGUI
from configuration import configHandler

class OtherConstants:
    #PROGRAM_JUST_STARTED = -999
    LAST_INDEX_OF_LIST = -1
    PENULTIMATE_INDEX_OF_LIST = -2
    FIRST_INDEX_OF_LIST = 0  
    MAX_SECONDS_REQUIRED_TO_CHECK_STATE = 2  
    
class TimeConstants:
    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60
    HOURS_IN_DAY = 24
    ONE_SECOND = 1
    
class NatureOfActivity:
    EYES_STRAINED = "strained"
    SCREEN_LOCKED = "screen_locked" #Note: For now, only NatureOfActivity.EYES_BEING_STRAINED is being written to file. Things like NatureOfActivity.SCREEN_LOCKED are not considered, since the strain duration can be determined even without them
    PAUSED_VIA_GUI = "paused"
    PROGRAM_NOT_RUNNING = "program_not_running" #iRest was not running during this phase. Such data gets stored in the timefile when the program is started, and the program checks earlier timestamps and realizes that it was started after a time lapse. This happens during system restarts or when iRest has crashed and started again or been manually restarted
    SUSPENDED = "suspended" #this could either be the computer in sleep/suspend state or the iRest process being suspended by the User
    # TYPING = "typing"
    # MOUSE_MOVEMENT = "mouse_movement"
    # WATCHING_VIDEO = "watching_video"
    
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
    def __init__(self, operatingSystemAdapter, timeFileManager):#TODO: Load the values from a config file
        self.REST_MINUTES = 5 #TODO: shift to config file
        self.WORK_MINUTES = 20 #TODO: shift to config file
        self.allowedStrainDuration = TimeConstants.SECONDS_IN_MINUTE * self.WORK_MINUTES #how long to work (in seconds). How many seconds the eyes can be permitted to be strained
        self.restRatio = self.WORK_MINUTES / self.REST_MINUTES #Five minutes of rest for every 20 minutes of work
        logging.debug(f"RestRatio={self.restRatio} = work minutes {self.WORK_MINUTES} * rest minutes {self.REST_MINUTES}")
        self.DATA_SAVE_INTERVAL = TimeConstants.SECONDS_IN_MINUTE #(in seconds) If state changes, data can get saved before this interval elapses too.  #TODO: shift to config file
        self.strainedDuration = 0 
        self.currentState = NatureOfActivity.EYES_STRAINED       
        self.timeFileManager = timeFileManager
        #self.timeFileManager.registerFileOperationsHandler(fileOperationsHandler)       
        self.notifiers = {} #references to various objects that can be used to notify the user
        self.operatingSystemAdapter = operatingSystemAdapter #value will be None if no OS was identified
        self.GUI_Layout = simpleGUI.DefaultTimerLayout(self)
        self.userPausedTimerViaGUI = False
        self.checkLoadedDataToSeeIfUserIsStrained()
        self.currentTime = 0
        self.elapsedTimeAccumulation = 0
        self.pastActivity = NatureOfActivity.EYES_STRAINED
        
    def noteTimeElapsedSinceProgramWasLastRunning(self):#this function is invoked only if historicalStrainData has at least one data stored
        """ program just started, so we check what the last recorded timestamp was, to know after how long this program was started """
        lastKnownTimestamp = self.__getLastKnownTimestamp() #this will be the last known loaded data timestamp
        currentTime = time.time()
        elapsedTime = currentTime - lastKnownTimestamp #time elapsed since the program was last known to be running
        if elapsedTime < 0:
            errorMessage = f"current time {currentTime} is lesser than the last time the program was running {lastKnownTimestamp}. Your system time appears to be messed up. Please delete the {self.timeFileManager.getTimeFilesFolderString()} folder"
            logging.error(errorMessage)
            raise ValueError(errorMessage)
        else:#store elapsed time as rested time. This will get written to file and appended to historicalStrainData
            self.recordTimeElapsedWhenThisProgramWasNotRunning(self, time.time(), elapsedTime)
        return currentTime
    
    def __getLastKnownTimestamp(self):
        lastWrittenData = self.timeFileManager.historicalStrainData[OtherConstants.LAST_INDEX_OF_LIST]
        return self.timeFileManager.getTimestampFromData(lastWrittenData)        

    def checkLoadedDataToSeeIfUserIsStrained(self): 
        self.strainedDuration = 0
        if len(self.timeFileManager.historicalStrainData) > 0:
            self.noteTimeElapsedSinceProgramWasLastRunning()   
            examinedDuration = 0
            for timeData in reversed(self.timeFileManager.historicalStrainData):#iterates backward, to consider the latest data that was written, first
                #timestamp = self.timeFileManager.getTimestampFromData(timeData)
                duration = self.timeFileManager.getElapsedTimeFromData(timeData)
                activity = self.timeFileManager.getNatureOfActivityFromData(timeData)
                examinedDuration = examinedDuration + duration
                if activity == NatureOfActivity.EYES_STRAINED:
                    self.__addStrain(duration)
                else:
                    self.__subtractStrain(duration)
                if examinedDuration >= self.WORK_MINUTES:#if sufficient time is analyzed, stop analyzing
                    break
        #---create a dummy value that simplifies obtaining a "previous" strained time and also creates a marker to indicate when the program began
        duration = 0 #a dummy value
        self.saveActivityAndUpdateStrain(time.time(), duration, NatureOfActivity.EYES_STRAINED) #saves this into the timeFile and also into historicalStrainData


    def execute(self):
        self.currentTime = time.time() #epoch time is simply the time elapsed since a specific year (around 1970)
        #---check if state changed, update strained duration and whether it's time to write to file
        self.checkStateChangeUpdateStrainDurationAndSave()
        #---notify the user based on the strained time
        self.__notifyUserIfTheyNeedToTakeRest_afterCheckingForSuspend()  

    def checkStateChangeUpdateStrainDurationAndSave(self):
        """ Checks for change of state, updates strain duration and writes to file if necessary """
        #---get current activity state
        currentActivity = NatureOfActivity.EYES_STRAINED        
        if self.userPausedTimerViaGUI:#if the user paused the timer via the GUI
            currentActivity = NatureOfActivity.PAUSED_VIA_GUI
        else:        
            if self.operatingSystemAdapter != None: #because the program should be capable of working even if the OS could not be identified            
                if self.operatingSystemAdapter.isScreenLocked(): #screen lock situation is currently being considered the equivalent of suspend or shutdown, so no need to write to file
                    currentActivity = NatureOfActivity.SCREEN_LOCKED
        #---add or subtract strain based on the elapsed activity
        elapsedTime = time.time() - self.currentTime #time elapsed while the previous activity was being performed
        if elapsedTime < 0:#negative elapsed time (means something is wrong)
            errorMessage = f"Elapsed time {elapsedTime} should not be negative." 
            logging.error(errorMessage)
            raise ValueError(errorMessage)
        else:#check for suspend state
            if elapsedTime > OtherConstants.MAX_SECONDS_REQUIRED_TO_CHECK_STATE:#means that the computer got suspended or iRest process got suspended while operations were being done, so this time can be considered as rest time
                #---save any accumulated activity of the state before suspension
                currentActivity = NatureOfActivity.SUSPENDED
                self.checkAndUpdateStrainAndFile(currentActivity)
                #---prime it to save the suspend time when it exits this if condition (the elapsed time during suspension will be a slight bit (less than a second) innacurate) 
                currentActivity = NatureOfActivity.EYES_STRAINED #making the current activity different from the past activity (which is now SUSPEND) so that it'll save and consider the suspended time 
                self.currentTime = time.time() #this will be the timestamp of the suspend time
        self.elapsedTimeAccumulation += elapsedTime        
        self.checkAndUpdateStrainAndFile(currentActivity)

    def checkAndUpdateStrainAndFile(self, currentActivity):        
        #---if state changed or time interval elapsed, update state and write to file
        if self.pastActivity != currentActivity or self.elapsedTimeAccumulation >= self.DATA_SAVE_INTERVAL:#state changed or writing interval reached (the program writes to file at fixed intervals, regardless of state change)
            self.saveActivityAndUpdateStrain(self.currentTime, self.elapsedTimeAccumulation, self.pastActivity)            
            self.pastActivity = currentActivity #whether state changed or not, current has to be assigned to past anyway
            self.elapsedTimeAccumulation = 0 #clear the written elapsed time 

    def saveActivityAndUpdateStrain(self, timestamp, duration, activity):
        self.timeFileManager.writeToFileAndHistoricalDataQueue(timestamp, duration, activity)     
        self.updateUserStrain(duration, activity)       

    def updateUserStrain(self, elapsedTime, activity):
        if NatureOfActivity.EYES_STRAINED == activity:
            self.__addStrain(elapsedTime)
        else:
            self.__subtractStrain(elapsedTime)

    def recordTimeElapsedWhenThisProgramWasNotRunning(self, currentTime, elapsedTime):
        self.timeFileManager.writeToFileAndHistoricalDataQueue(currentTime, elapsedTime, NatureOfActivity.PROGRAM_NOT_RUNNING) #More data can be added to this list when writing, if necessary                    
        self.currentState = NatureOfActivity.PROGRAM_NOT_RUNNING

    def __addStrain(self, elapsedTime_seconds):
        logging.debug(f"+++ Adding strain of {elapsedTime_seconds}s to strained duration {self.strainedDuration}")
        self.strainedDuration = self.strainedDuration + elapsedTime_seconds      

    def __subtractStrain(self, restDuration_seconds):
        logging.debug(f"--- Rested duration: {restDuration_seconds}s. Subtracting {restDuration_seconds * self.restRatio} from strained duration {self.strainedDuration}")
        self.strainedDuration = self.strainedDuration - self.__calculateStrainReductionBasedOnRestDuration(restDuration_seconds) #(20*60)-((20/5)*(5*60))
        if self.strainedDuration < 0: 
            self.strainedDuration = 0

    def __calculateStrainReductionBasedOnRestDuration(self, restDuration_seconds):
        return restDuration_seconds * self.restRatio
        
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
        
    def __notifyUserIfTheyNeedToTakeRest_afterCheckingForSuspend(self):
        #logging.debug("-----> Current strained time: " + time.strftime("%H:%M:%S", time.gmtime(self.strainedDuration)))
        #---check if strained duration is greater than the allowed strain and also ensure that the program wasn't suspended for as long as a User's rest need (because if the program was suspended that long, there's no need of notifying the user to rest)
        if self.strainedDuration > self.allowedStrainDuration and (time.time() - self.currentTime) < self.REST_MINUTES * TimeConstants.SECONDS_IN_MINUTE:#means that the computer got suspended or iRest process got suspended while operations were being done, so this time can be considered as rest time: #notify the User to take rest
            #logging.info(f"* Please take rest. Strained duration: {self.strainedDuration}")
            for notifierID, notifier in self.notifiers.items(): #If operating system was not recognized, the operating system adapter will be None, and no notifier will be registered. It will be an empty dict
                notifier.execute() #within each notifier's execute(), there will be a cooldown timer, which will ensure that the notification is not repeated until some time has passed, even if execute() is invoked frequently        

    def getStrainDetails(self):#returns strainedDuration, allowedStrainDuration, formattedStrainedTime. Used by the GUI and test cases
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

    
