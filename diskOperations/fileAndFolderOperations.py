import os
import ast #to convert string representation of list to actual list
import shutil
import logging
from collections import deque

#TODO: Try catch for most of the functions are needed
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

    def renameFile(self, oldFilename, newFilename):
        os.rename(oldFilename, newFilename)
        
    def appendLinesToFile(self, filenameWithPath, listOfDataToWrite): #TODO: This function needs to be improved to better recognize lists. Right now the list passed needs to be enclosed in square brackets when being passed. This should be avoided
        fileHandle = open(filenameWithPath, 'a+')
        for line in listOfDataToWrite:
            fileHandle.write(line)
            fileHandle.write("\n")
        fileHandle.close()
        
    def readFromFile(self, filenameWithPath):
        with open(filenameWithPath) as fileHandler:
            lines = fileHandler.read().splitlines()#TODO: try catch
        return lines              
    
    def createDirectoryIfNotExisting(self, folder):
        if not os.path.exists(folder): 
            try: os.makedirs(folder)
            except FileExistsError:#in case there's a race condition where some other process creates the directory before makedirs is called
                pass
    
    def isValidDirectory(self, folderpath):
        return os.path.exists(folderpath)
    
    def moveFile(self, existingPath, existingFilename, newPath, newFilename):
        """ Move file to another directory. Renaming while moving is possible """
        shutil.move(existingPath + existingFilename, newPath + newFilename)  

    def getFileSize(self, fileNameWithPath):
        """ returns file size in bytes """
        return os.path.getsize(fileNameWithPath)   

    def getLastLinesOfThisFile(self, fileNameWithPath, numberOfLinesToGet):
        """ Gets the last n number of lines from a file. Caution: use only with small files, since this iterates the entire file. Better solutions exist for large files: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-similar-to-tail"""
        lastLines = deque(maxlen = numberOfLinesToGet) #FIFO deque that stores a fixed number of items
        with open(fileNameWithPath) as fileHandler:
            for line in fileHandler:
                lastLines.append(ast.literal_eval(line)) #to convert string representation of the lists to actual lists
        return lastLines

    # def getNamesOfFilesInDirectory(self, fullFolderPath):
    #     return glob(os.path.join(self.folderName, self.archiveFileNamePrefix) + "*")

    def writeTimeInformationToFile(self, pathWithFileName, timeInformation):
        """ Writes time information to file, checks if file is too large and creates a new file if necessary """
        self.appendLinesToFile(pathWithFileName, [timeInformation]) #The square brackets in [timeInformation] are necessary because otherwise, each character in the list or string will get written to a new line in the file
