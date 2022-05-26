import os 
from collections import deque
from glob import glob
import logging
import natsort

""" 
Keeping track of the amount of time the eyes were strained, requires tracking the total
time even when the computer is restarted or the screen is locked. The only way to track it 
accurately is to store data in a file periodically and examine the latest stored data sequence,
upto a time period that allows determining if the user is strained or has obtained sufficient 
rest. This class performs the function of storing data into a file. When the file gets too large,
the file is renamed (you could consider it being archived, although the word 'archive' here is
a misnomer, because the file is only being renamed) and a new file is created for storing the latest
time data. So after some time, the pattern of files created will be something like this:
Archive1_timeFileName.txt, Archive2_timeFileName.txt, timeFileName.txt.
The Archive1_timeFileName.txt file will contain data from the start of the program. The remaining 
data follows in Archive2_timeFileName.txt, and timeFileName.txt is the file to which the newest data 
is written. When timeFileName.txt exceeds a size threshold, it will be renamed to Archive3_timeFileName.txt,
and a new timeFileName.txt gets created. Since it is time consuming to constantly access the files
to retrieve the past data, a FIFO deque (of limited length) stores the latest time data. When the program starts, the deque
is populated with data from the older files if they exist.
 """
class TimeFileManager:
    def __init__(self, folderNameWithoutFolderSlash, fileNameWithoutFileExtension, fileOperationsHandler):
        self.STRAIN_DATA_HISTORY_LENGTH = 360 #TODO: calculate this based on the size of the interval during which file writes happen
        self.historicalStrainData = deque(maxlen = self.STRAIN_DATA_HISTORY_LENGTH) #maxlen ensures a FIFO behaviour when using append     
        self.folderName = folderNameWithoutFolderSlash
        self.fileNameWithoutExtension = fileNameWithoutFileExtension
        self.archiveFileNamePrefix = "Archive"
        self.fileExtension = ".txt"
        self.timerFileNameWithPath = os.path.join(self.folderName, self.fileNameWithoutExtension, self.fileExtension)
        self.numberOfWritesSinceProgramStart = 0 #to not let file size increase too much if program is run non-stop for many days
        self.TIMER_FILE_MAX_SIZE = 10000 #bytes
        self.FREQUENCY_TO_CHECK_FILE_SIZE = 500
        self.fileOps = fileOperationsHandler
        self.fileOps.createDirectoryIfNotExisting(self.folderName) #The folder to store time files         
        self.FILENAME_SEPARATOR = "_" #TODO: declare these constants in a separate class
        self.LAST_INDEX_OF_LIST = -1
        self.FIRST_INDEX_OF_LIST = 1
        self.__archiveTheTimerFileIfTooLarge()
        self.__extractHistoricalTimeDataFromFiles()
        self.isTheUserStrained()

    def isTheUserStrained(self):
        #Checks the self.historicalStrainData
        pass

    def writeTimeInformationToFile(self, dataToWrite):
        self.historicalStrainData.append(dataToWrite)
        self.fileOps.writeTimeInformationToFile(self.timerFileNameWithPath, str(dataToWrite))
        self.numberOfWritesSinceProgramStart = self.numberOfWritesSinceProgramStart + 1
        #--- To not let file size increase too much if program is run non-stop for many days            
        if self.numberOfWritesSinceProgramStart > self.FREQUENCY_TO_CHECK_FILE_SIZE:
            self.numberOfWritesSinceProgramStart = 0          
            self.__archiveTheTimerFileIfTooLarge()

    def __extractHistoricalTimeDataFromFiles(self):
        historicalData = deque() #TODO: check order in which data is populated and the validity of data retrieved
        if self.fileOps.isValidFile(self.timerFileNameWithPath):#if timer file exists, get as many lines from the end of the file as possible
            historicalData = self.fileOps.getLastLinesOfThisFile(self, self.timerFileNameWithPath, self.STRAIN_DATA_HISTORY_LENGTH)
            if len(historicalData) < self.STRAIN_DATA_HISTORY_LENGTH:
                archiveFiles = self.__getSortedListOfArchiveFiles(listOrderReversalNeeded = True)
                for oneFile in archiveFiles:
                    fullFilePath = os.join(self.folderName, oneFile)
                    historicalData += self.fileOps.getLastLinesOfThisFile(self, fullFilePath, self.STRAIN_DATA_HISTORY_LENGTH)
                    if len(historicalData) >= self.STRAIN_DATA_HISTORY_LENGTH:
                        break
        self.historicalStrainData += historicalData

    def __archiveTheTimerFileIfTooLarge(self):
        """ Check if timer file is larger than a certain value and return True if so """
        if self.fileOps.isValidFile(self.timerFileNameWithPath):#if file exists. If it doesn't exist, it'll get created when the program writes time information to disk
            if self.fileOps.getFileSize(self.timerFileNameWithPath) > self.TIMER_FILE_MAX_SIZE:
                highestOrdinal = self.__findHighestArchiveFileOrdinal()
                newFilename = self.__createArchiveFileNameUsingOrdinal(highestOrdinal + 1)
                self.fileOps.renameFile(self.timerFileNameWithPath, os.path.join(self.folderName, newFilename)) #The so-called "archiving" happens here
                #The new timer file will automatically get created when the program needs to write to disk                
            
    def __findHighestArchiveFileOrdinal(self):
        """ The ordinal is the numbering given to the file. This function finds the highest number that has been reached. If 24 files have been archived, the highest ordinal will be 24, and the calling function will use 24+1 = 25 as the next file ordinal."""
        highestOrdinal = 0 #the default value it starts with is 1, so this value is 0, since the calling function will eventually increment the ordinal to 1 if there's no existing file
        #---search for files starting with the archive prefix
        archiveFiles = self.__getSortedListOfArchiveFiles()
        if archiveFiles: #if list not empty
            logging.info(f"The archive files are: {archiveFiles}")
            #TODO: try catch for if the filenames don't have any substring we are looking for
            fileNameWithHighestOrdinal = archiveFiles[self.LAST_INDEX_OF_LIST]
            fileNameWithHighestOrdinal = fileNameWithHighestOrdinal.split(self.FILENAME_SEPARATOR)[self.FIRST_INDEX_OF_LIST] #get the "Archive1" part of the string, where the "1" is an example of the ordinal
            #---extract the digit in the substring (https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python)
            highestOrdinal = int(''.join(filter(str.isdigit, fileNameWithHighestOrdinal))) 
        return highestOrdinal

    def __getSortedListOfArchiveFiles(self, listOrderReversalNeeded = False):
        archiveFiles = glob(os.path.join(self.folderName, self.archiveFileNamePrefix) + "*") #TODO: shift to fileAndFolderOperations class
        return natsort.natsorted(archiveFiles, reverse = listOrderReversalNeeded) #To sort files with numbers in them, in the right order. An ordinary sort would sort the files as ["Archive_1.txt", "Archive_10.txt", "Archive_2.txt"]

    def __createArchiveFileNameUsingOrdinal(self, ordinal):
        #--- Archive filename will be like "Archive1_timeFileName.txt"
        return self.archiveFileNamePrefix + str(ordinal) + self.FILENAME_SEPARATOR + self.fileNameWithoutExtension + self.fileExtension
