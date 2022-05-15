import os
import shutil
import logging

#Note: Since these functions are operating-system-independent, they are kept as part of this package, rather than placing them in the operatingSystemFunctions package
class FileOperations:
    def __init__(self):
        pass
   
    def isValidFile(self, filenameWithPath):
        return os.path.isfile(filenameWithPath)   
    
    def getFilenameAndExtension(self, filenameOrPathWithFilename):
        filename, fileExtension = os.path.splitext(filenameOrPathWithFilename)
        return filename, fileExtension
    
    def deleteFile(self, filenameWithPath):
        os.remove(filenameWithPath) #TODO: check if file exists before deleting
        
    def writeLinesToFile(self, filenameWithPath, listOfDataToWrite):
        fileHandle = open(filenameWithPath, 'w')
        for line in listOfDataToWrite:
            fileHandle.write(line)
            fileHandle.write("\n")
        fileHandle.close()
        
    def readFromFile(self, filenameWithPath):
        with open(filenameWithPath) as f:
            lines = f.read().splitlines()#TODO: try catch
        return lines              
    
    def createDirectoryIfNotExisting(self, folder):
        if not os.path.exists(folder): 
            try: os.makedirs(folder)
            except FileExistsError:#in case there's a race condition where some other process creates the directory before makedirs is called
                pass
    
    def isThisValidDirectory(self, folderpath):
        return os.path.exists(folderpath)
    
    def moveFile(self, existingPath, existingFilename, newPath, newFilename):
        """ Move file to another directory. Renaming while moving is possible """
        shutil.move(existingPath + existingFilename, newPath + newFilename)      
    
    def __isTimerFileTooLarge(self):
        """ Check if timer file is larger than a certain value and return True if so """
        fileIsTooLarge = False
        return fileIsTooLarge

    def findWhichTimerInformationFileToWriteTo(self, folderContainingTimerFiles):
        """ Timer information files are numbered in ascending order. This function searches if files are missing and which file is numerically the highest, in order to choose which file to start writing to. The numerically highest filename is returned. If no file is found, a file is created. """
        fileToWriteTo = ""
        return fileToWriteTo

    def writeTimeInformationToFile(self, pathWithFileName, timeInformation):
        """ Writes time information to file, checks if file is too large and creates a new file if necessary """
        self.writeLinesToFile(pathWithFileName, [timeInformation])
