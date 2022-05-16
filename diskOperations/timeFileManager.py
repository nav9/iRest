import os 
import logging

class TimeFileManager:
    def __init__(self, folderName, fileName, fileOperationsHandler):
        self.folderName = folderName
        self.fileName = fileName
        self.pathWithFilename = os.path.join(self.folderName, self.fileName)
        self.numberOfWritesSinceProgramStart = 0 #to not let file size increase too much if program is run non-stop for many days
        self.TIMER_FILE_MAX_SIZE = 10000 #bytes
        self.fileOps = fileOperationsHandler
        self.fileOps.createDirectoryIfNotExisting(self.folderName) #The folder to store time files
        self.__renameTimerFileIfTooLarge() 

    def writeTimeInformationToFile(self, dataToWrite):
        self.fileOps.writeTimeInformationToFile(self.pathWithFilename, str(dataToWrite))
        self.numberOfWritesSinceProgramStart = self.numberOfWritesSinceProgramStart + 1
        self.__renameTimerFileIfTooLarge()

    def __renameTimerFileIfTooLarge(self):
        """ Check if timer file is larger than a certain value and return True if so """
        if self.fileOps.isValidFile(self.pathWithFilename):
            #--- To not let file size increase too much if program is run non-stop for many days            
            if self.numberOfWritesSinceProgramStart > self.TIMER_FILE_MAX_SIZE:#A check for any large enough number would do
                self.numberOfWritesSinceProgramStart = 0            

    def findOrdinalOfTimerFile(self, folderContainingTimerFiles):
        """ Timer information files are numbered in ascending order. This function searches if files are missing and which file is numerically the highest, in order to choose which file to start writing to. The numerically highest filename is returned. If no file is found, a file is created with number 0. """
        fileToWriteTo = ""
        return fileToWriteTo        
