import os
import time
import random
from collections import deque
from configuration import configHandler

class ConstantsForTesting:
    TESTS_FOLDER = "tests"
    DIGITS_AFTER_DECIMAL = 7
    INTERVAL_BETWEEN_WRITES = 60 #seconds (the time interval between the writing of time values to disk. Time is either written at the end of this interval or during state changes)

class CommonTestFunctions:
    def createNewTestFolder(self, fileFolderOps):
        archiveFolder = os.path.join(ConstantsForTesting.TESTS_FOLDER, configHandler.Names.ARCHIVE_FOLDER, "")
        fileFolderOps.deleteFolderIfItExists(archiveFolder) 
        return archiveFolder    

class DummyTimeFunctions:
    def __init__(self) -> None:
        self.dummyTimeValues = deque()

    def generateElapsedTimeOfWriteIntervalDuration(self):
        """ Returns a random float ranging between a to b, and with N digits after the decimal """
        return round(random.uniform(ConstantsForTesting.INTERVAL_BETWEEN_WRITES, ConstantsForTesting.INTERVAL_BETWEEN_WRITES + 1), ConstantsForTesting.DIGITS_AFTER_DECIMAL)
        
    def getCurrentTime(self):
        return time.time()
    
    def getDummyCurrentTime(self):
        return self.dummyTimeValues.pop() #pops from the left of the deque
    
    def setDummyTimeValues(self, listOfTimeValues):
        for data in listOfTimeValues:
            self.dummyTimeValues.appendleft(data)

    def getElapsedDurationSinceThisTime(self, timestamp):#for calculating elapsed time since program last ran
        currentTime = self.getCurrentTime()
        elapsedDuration = currentTime - timestamp
        if elapsedDuration < 0:
            self.__raiseAndLogError(elapsedDuration, currentTime, timestamp)        
        return elapsedDuration, currentTime        

class DummyTimeElapseChecker:
    pass

class DummyWarmthApp:
    pass

class DummyOperatingSystemAdapter:
    def __init__(self) -> None:
        self.screenLocked = False

    def getTimeElapseCheckerInstanceForThisDuration(self, duration):
        return DummyTimeElapseChecker()

    def getTimeFunctionsApp(self):
        return DummyTimeFunctions()

    def isScreenLocked(self):
        return self.screenLocked

    def setScreenLockStatus(self, lockStatus):
        self.screenLocked = lockStatus

    def getWarmthApp(self):
        pass