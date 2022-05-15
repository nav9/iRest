import os 
import logging

class TimeFileManager:
    def __init__(self, folderName, fileName):
        self.folderName = folderName
        self.fileName = fileName
        self.fullPath = os.path.join(self.folderName, self.fileName)
        self.fileOps = None
        self.numberOfWritesSinceProgramStart = 0 #to not let file size increase too much if program is run non-stop for many days
        self.TIMER_FILE_MAX_SIZE = 10000 #bytes

    def registerFileOperationsHandler(self, fileOperationsHandler):
        self.fileOps = fileOperationsHandler
        self.fileOps.createDirectoryIfNotExisting(self.folderName)
        self.__renameTimerFileIfTooLarge()

    def writeTimeInformationToFile(self, dataToWrite):
        self.fileOps.writeTimeInformationToFile(self.fullPath, str(dataToWrite))
        #--- To not let file size increase too much if program is run non-stop for many days
        self.numberOfWritesSinceProgramStart = self.numberOfWritesSinceProgramStart + 1
        if self.numberOfWritesSinceProgramStart > self.TIMER_FILE_MAX_SIZE:#A check for any large enough number would do
            self.numberOfWritesSinceProgramStart = 0
            self.__renameTimerFileIfTooLarge()

    def __renameTimerFileIfTooLarge(self):
        """ Check if timer file is larger than a certain value and return True if so """
        fileIsTooLarge = False

        return fileIsTooLarge

    def findOrdinalOfTimerFile(self, folderContainingTimerFiles):
        """ Timer information files are numbered in ascending order. This function searches if files are missing and which file is numerically the highest, in order to choose which file to start writing to. The numerically highest filename is returned. If no file is found, a file is created with number 0. """
        fileToWriteTo = ""
        return fileToWriteTo        
