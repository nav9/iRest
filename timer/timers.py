import logging
from abc import ABC, abstractmethod
from gui import simpleGUI
from configuration import configHandler

class OtherConstants:
    LAST_INDEX_OF_LIST = -1
    PENULTIMATE_INDEX_OF_LIST = -2
    FIRST_INDEX_OF_LIST = 0  
    SECONDS_ELAPSED_BEFORE_ASSUMING_SUSPEND = 2
    
class TimeConstants:
    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60
    HOURS_IN_DAY = 24
    ONE_SECOND = 1
    
class NatureOfActivity:
    EYES_STRAINED = "strained"
    SCREEN_LOCKED = "screen_locked" #Note: For now, only NatureOfActivity.EYES_BEING_STRAINED is being written to file. Things like NatureOfActivity.SCREEN_LOCKED are not considered, since the strain duration can be determined even without them
    PAUSED_VIA_GUI = "paused" #User had clicked on a pause button to pause the noting of strained time (the user can use this if screen lock functionality isn't available, and the User wants to let iRest know that the period of pausing is the period that they are taking rest)
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


#Note: This class checks how much time the user worked, whether to notify the User to take rest and whether to notify the User that the rest period has completed. This is just one of the engines which does such processing. You could create a different engine and allow it to work with a different logic.
#Each such class is designed to have its own way of evaluating if the User is strained
class DefaultTimer(RestTimers):#Checks for how much time elapsed and notifies the User
    def __init__(self, operatingSystemAdapter, timeFileManager):#TODO: Load the values from a config file
        self.REST_MINUTES = 5 #TODO: shift to config file
        self.WORK_MINUTES = 20 #TODO: shift to config file
        self.elapsedTimeAccumulation = 0
        self.allowedStrainDuration = TimeConstants.SECONDS_IN_MINUTE * self.WORK_MINUTES #how long to work (in seconds). How many seconds the eyes can be permitted to be strained
        self.restRatio = self.WORK_MINUTES / self.REST_MINUTES #Five minutes of rest for every 20 minutes of work
        logging.debug(f"RestRatio={self.restRatio} = work minutes {self.WORK_MINUTES} * rest minutes {self.REST_MINUTES}")
        self.DATA_SAVE_INTERVAL = TimeConstants.SECONDS_IN_MINUTE #(in seconds) If state changes, data can get saved before this interval elapses too.  
        self.strainedDuration = 0 
        self.currentState = NatureOfActivity.EYES_STRAINED         
        self.timeFileManager = timeFileManager
        self.notifiers = {} #references to various objects that can be used to notify the user
        self.operatingSystemAdapter = operatingSystemAdapter #value will be None if no OS was identified
        self.timeFunctions = self.operatingSystemAdapter.getTimeFunctionsApp()
        self.GUI_Layout = simpleGUI.DefaultTimerLayout(self)
        self.userPausedTimerViaGUI = False
        self.dataSaveInterval = self.operatingSystemAdapter.getTimeElapseCheckerInstanceForThisDuration(self.DATA_SAVE_INTERVAL) #for periodically writing accumulated elapsed time to file
        self.checkLoadedDataToSeeIfUserIsStrained()      
        self.pastActivity = NatureOfActivity.EYES_STRAINED

    def getTimeFileData(self):
        return self.timeFileManager.getTimeFileData()

    def __getLastKnownTimestamp(self):
        lastWrittenData = self.timeFileManager.historicalStrainData[OtherConstants.LAST_INDEX_OF_LIST]
        return self.timeFileManager.getTimestampFromData(lastWrittenData)   
            
    def noteTimeElapsedSinceProgramWasLastRunning(self):#this function is invoked only if historicalStrainData has at least one data stored
        """ program just started, so we check what the last recorded timestamp was, to know after how long this program was started """
        #get time functions are called in getElapsedDuration function and recordTimeElapsed function
        lastKnownTimestamp = self.__getLastKnownTimestamp() #this will be the last known loaded data timestamp
        elapsedDuration, currentTime = self.timeFunctions.getElapsedDurationSinceThisTime(lastKnownTimestamp)#time elapsed since the program was last known to be running
        #---store elapsed time as rested time. This will get written to file and appended to historicalStrainData
        self.recordTimeElapsedWhenThisProgramWasNotRunning(self.timeFunctions.getCurrentTime(), elapsedDuration)
        return currentTime
    
    def checkLoadedDataToSeeIfUserIsStrained(self): #get current time is called thrice in this function (saveActivity function and noteTimeElapsed function)
        self.strainedDuration = 0
        if len(self.timeFileManager.historicalStrainData) > 0:
            self.noteTimeElapsedSinceProgramWasLastRunning() #there are two calls to getCurrentTime here
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
                if examinedDuration >= self.WORK_MINUTES * TimeConstants.SECONDS_IN_MINUTE:#if sufficient time is analyzed, stop analyzing
                    break
        #---create a dummy value that simplifies obtaining a "previous" strained time and also creates a marker to indicate when the program began
        duration = 0 #a dummy value
        self.saveActivityAndUpdateStrain(self.timeFunctions.getCurrentTime(), duration, NatureOfActivity.EYES_STRAINED) #saves this into the timeFile and also into historicalStrainData

    def execute(self):
        #---check if state changed, update strained duration and whether it's time to write to file
        currentActivity, currentTime = self.checkStateChangeUpdateStrainDurationAndSave()
        #---notify the user based on the strained time
        if currentActivity == NatureOfActivity.EYES_STRAINED:
            self.notifyUserIfTheyNeedToTakeRest_afterCheckingForSuspend(currentTime)  #no need of notifying User if the program is paused or screen is locked

    def checkStateChangeUpdateStrainDurationAndSave(self):
        """ Checks for change of state, updates strain duration and writes to file if necessary """
        #---get current activity state
        currentActivity = NatureOfActivity.EYES_STRAINED                
        if self.userPausedTimerViaGUI:#if the user paused the timer via the GUI TODO: this should eventually work even if there's no GUI
            currentActivity = NatureOfActivity.PAUSED_VIA_GUI            
        else:#check for screen lock only periodically since it's an expensive operation    
            if self.operatingSystemAdapter.isScreenLocked(): #check will be done only at a defined time interval. screen lock situation is currently being considered the equivalent of suspend or shutdown, so no need to write to file
                currentActivity = NatureOfActivity.SCREEN_LOCKED                
        logging.debug(f"Current activity: {currentActivity}")
        #---add or subtract strain based on the elapsed activity
        elapsedTime, currentTime = self.timeFunctions.getElapsedDurationSinceTheLastCheck() #time elapsed while the previous activity was being performed
        logging.debug(f"Elapsed time {elapsedTime}. currentTime {currentTime}")
        #---check for whether the computer or iRest had been suspended 
        if elapsedTime > OtherConstants.SECONDS_ELAPSED_BEFORE_ASSUMING_SUSPEND:#means that the computer got suspended or iRest process got suspended while operations were being done, so this time can be considered as rest time
            #---save any accumulated activity of the state before suspension
            currentActivity = NatureOfActivity.SUSPENDED
            self.checkAndUpdateStrainAndFile(currentActivity, self.elapsedTimeAccumulation, currentTime)
            logging.debug(f"detected that the computer was suspended earlier for approx {elapsedTime}s. Saving accumulated time {self.elapsedTimeAccumulation}s")
            #---by altering currentActivity, prime it to save the suspend time when it exits this if condition (the elapsed time during suspension will be a slight bit (less than a second) innacurate) 
            currentActivity = NatureOfActivity.EYES_STRAINED #making the current activity different from the past activity (which is now SUSPEND) so that it'll save and consider the suspended time 
        self.elapsedTimeAccumulation += elapsedTime    
        #---update strain
        logging.debug(f"Elapsed time accumulated: {self.elapsedTimeAccumulation}")
        self.checkAndUpdateStrainAndFile(currentActivity, elapsedTime, currentTime)
        return currentActivity, currentTime

    def checkAndUpdateStrainAndFile(self, currentActivity, elapsedTime, currentTime):        
        """ if state changed or time interval elapsed, update state and write to file. Else just update strain value """
        logging.debug(f"past: {self.pastActivity}, current: {currentActivity}, accumulatedElapsedTime: {self.elapsedTimeAccumulation}")
        if self.pastActivity != currentActivity or self.elapsedTimeAccumulation >= self.DATA_SAVE_INTERVAL:#state changed or writing interval reached (the program writes to file at fixed intervals, regardless of state change)
            logging.debug(f"State changed or time interval elapsed. Saving to file: elapsed:{elapsedTime}s, accumulated:{self.elapsedTimeAccumulation}s current:{currentTime}s currentActivity:{currentActivity} pastActivity: {self.pastActivity}")
            self.saveActivityAndUpdateStrain(currentTime, elapsedTime, self.pastActivity)            
            self.pastActivity = currentActivity #whether state changed or not, current has to be assigned to past anyway
            self.elapsedTimeAccumulation = 0 #clear the written elapsed time             
        else:#do a routine strain variable update without saving to file
            logging.debug(f"Routine strain variable update without saving to file. Using elapsed: {elapsedTime}s and pastActivity: {self.pastActivity}")
            self.updateUserStrain(elapsedTime, self.pastActivity)

    def saveActivityAndUpdateStrain(self, timestamp, duration, activity):
        logging.debug(f"Saving to file: timestamp {timestamp}, elapsedTime {self.elapsedTimeAccumulation}, pastActivity {activity}")
        self.timeFileManager.writeToFileAndHistoricalDataQueue(timestamp, self.elapsedTimeAccumulation, activity)     
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
        
    def notifyUserIfTheyNeedToTakeRest_afterCheckingForSuspend(self, currentTime):
        logging.debug(f"-----> Current strained time: {self.timeFunctions.getTimeFormattedAsHMS(self.strainedDuration)}")
        #---check if strained duration is greater than the allowed strain and also ensure that the program wasn't suspended for as long as a User's rest need (because if the program was suspended that long, there's no need of notifying the user to rest)
        if self.strainedDuration > self.allowedStrainDuration and (self.timeFunctions.getCurrentTime() - currentTime) < self.REST_MINUTES * TimeConstants.SECONDS_IN_MINUTE:#means that the computer got suspended or iRest process got suspended while operations were being done, so this time can be considered as rest time: #notify the User to take rest
            logging.info(f"* Please take rest. Strained duration: {self.strainedDuration}")
            for notifierID, notifier in self.notifiers.items(): #If operating system was not recognized, the operating system adapter will be None, and no notifier will be registered. It will be an empty dict
                notifier.execute() #within each notifier's execute(), there will be a cooldown timer, which will ensure that the notification is not repeated until some time has passed, even if execute() is invoked frequently        

    def getStrainedDuration(self):
        return self.strainedDuration
    
    def getStrainDetails(self):#returns strainedDuration, allowedStrainDuration, formattedStrainedTime. Used by the GUI and test cases
        return self.strainedDuration, self.timeFunctions.getTimeFormattedAsHMS(self.allowedStrainDuration), self.timeFunctions.getTimeFormattedAsHMS(self.strainedDuration)

    def setTestTimeFunctionsInstance(self, testTimeFunctions):#used by test cases to be able to emulate a supply of time values more conveniently
        self.timeFunctions = testTimeFunctions

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

    
