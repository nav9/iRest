import os 
from glob import glob
import logging
import natsort

class TimeFileManager:
    def __init__(self, folderName, fileNameWithoutExtension, fileOperationsHandler):
        self.folderName = folderName
        self.fileNameWithoutExtension = fileNameWithoutExtension
        self.archiveFileNamePrefix = "Archive"
        self.fileExtension = ".txt"
        self.pathWithFilename = os.path.join(self.folderName, self.fileNameWithoutExtension, self.fileExtension)
        self.numberOfWritesSinceProgramStart = 0 #to not let file size increase too much if program is run non-stop for many days
        self.TIMER_FILE_MAX_SIZE = 10000 #bytes
        self.fileOps = fileOperationsHandler
        self.fileOps.createDirectoryIfNotExisting(self.folderName) #The folder to store time files         
        self.FILENAME_SEPARATOR = "_" #TODO: declare these constants in a separate class
        self.LAST_INDEX_OF_LIST = -1
        self.FIRST_INDEX_OF_LIST = 1
        self.__archiveTheTimerFileIfTooLarge()

    def writeTimeInformationToFile(self, dataToWrite):
        self.fileOps.writeTimeInformationToFile(self.pathWithFilename, str(dataToWrite))
        self.numberOfWritesSinceProgramStart = self.numberOfWritesSinceProgramStart + 1
        #--- To not let file size increase too much if program is run non-stop for many days            
        if self.numberOfWritesSinceProgramStart > self.TIMER_FILE_MAX_SIZE:#A check for any large enough number would do
            self.numberOfWritesSinceProgramStart = 0          
            self.__archiveTheTimerFileIfTooLarge()

    def __archiveTheTimerFileIfTooLarge(self):
        """ Check if timer file is larger than a certain value and return True if so """
        if self.fileOps.isValidFile(self.pathWithFilename):#if file exists. If it doesn't exist, it'll get created when the program writes time information to disk
            highestOrdinal = self.__findHighestFileOrdinal()
            newFilename = self.__createArchiveFilenameUsingOrdinal(highestOrdinal + 1)
            self.fileOps.renameFile(self.pathWithFilename, os.path.join(self.folderName, newFilename))
            
    def __findHighestFileOrdinal(self):
        """ The ordinal is the numbering given to the file. This function finds the highest number that has been reached. If 24 files have been archived, the highest ordinal will be 24, and the calling function will use 24+1 = 25 as the next file ordinal."""
        highestOrdinal = 1 #the default value it starts with
        #---search for files starting with the archive prefix
        archiveFiles = glob(os.path.join(self.folderName, self.archiveFileNamePrefix) + "*") #TODO: shift to fileAndFolderOperations class
        archiveFiles = natsort.natsorted(archiveFiles) #To sort files with numbers in them, in the right order. An ordinary sort would sort the files as ["Archive_1.txt", "Archive_10.txt", "Archive_2.txt"]
        if archiveFiles: #if list not empty
            logging.info(f"The archive files are: {archiveFiles}")
            #TODO: try catch for if the filenames don't have any substring we are looking for
            fileNameWithHighestOrdinal = archiveFiles[self.LAST_INDEX_OF_LIST]
            fileNameWithHighestOrdinal = fileNameWithHighestOrdinal.split(self.FILENAME_SEPARATOR)[self.FIRST_INDEX_OF_LIST] #get the "Archive1" part of the string, where the "1" is an example of the ordinal
            #---extract the digit in the substring (https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python)
            highestOrdinal = int(''.join(filter(str.isdigit, fileNameWithHighestOrdinal))) 
        return highestOrdinal

    def __createArchiveFilenameUsingOrdinal(self, ordinal):
        #--- Archive filename will be like "Archive1_timeFileName.txt"
        return self.archiveFileNamePrefix + str(ordinal) + self.FILENAME_SEPARATOR + self.fileNameWithoutExtension + self.fileExtension

    def findOrdinalOfTimerFile(self, folderContainingTimerFiles):
        """ Timer information files are numbered in ascending order. This function searches if files are missing and which file is numerically the highest, in order to choose which file to start writing to. The numerically highest filename is returned. If no file is found, a file is created with number 0. """
        fileToWriteTo = ""
        return fileToWriteTo        
