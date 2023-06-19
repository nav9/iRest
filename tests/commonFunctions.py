import os
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

    def generateElapsedTime(self):
        """ Returns a random float ranging between a to b, and with N digits after the decimal """
        return round(random.uniform(ConstantsForTesting.INTERVAL_BETWEEN_WRITES, ConstantsForTesting.INTERVAL_BETWEEN_WRITES + 1), ConstantsForTesting.DIGITS_AFTER_DECIMAL)
        
    def getCurrentTime(self):
        return self.dummyTimeValues.pop()