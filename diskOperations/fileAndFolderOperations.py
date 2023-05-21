import os
import ast #to convert string representation of list to actual list
import shutil
import logging
from collections import deque

#TODO: Try catch is needed for most of these functions
#Note: Since these functions are operating-system-independent, they are kept as part of this package, rather than placing them in the operatingSystemFunctions package
class FileOperations:
    def __init__(self):
        pass
   
    def isValidFile(self, filenameWithPath):
        return os.path.isfile(filenameWithPath)   
    
    def getFilenameAndExtension(self, filenameOrPathWithFilename):
        filename, fileExtension = os.path.splitext(filenameOrPathWithFilename)
        return filename, fileExtension
    
    def deleteFolderIfItExists(self, folderPath):
        try:
            if os.path.exists(folderPath):
                shutil.rmtree(folderPath, ignore_errors = True) #The ignore_errors is for when the folder has read-only files https://stackoverflow.com/a/303225/453673
        except Exception as e:
            logging.error("Error when deleting folder: " + folderPath + ". Exception: " + str(e))    
    
    def deleteFileIfItExists(self, filenameWithPath):
        try:
            if os.path.isfile(filenameWithPath):
                os.remove(filenameWithPath)
        except Exception as e:
            logging.error("Error when deleting file: " + filenameWithPath + ". Exception: " + str(e))

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

    def getListOfSubfoldersInThisFolder(self, folderNameWithPath):
        return next(os.walk(folderNameWithPath))[self.SUBDIRECTORIES]
        
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
                try:
                    lastLines.append(ast.literal_eval(line)) #to convert string representation of the lists to actual lists
                except ValueError:
                    logging.warning(f"Encountered a malformed string or some invalid data in {fileNameWithPath} while loading old data.")    
                    pass #Sometimes, the file may contain strange characters like this "\00\00\00\00" which are invalid. Such lines can be avoided. Perhaps inserted at the exact moment a system restart happened or due to some other file error.
        return lastLines

    # def getNamesOfFilesInDirectory(self, fullFolderPath):
    #     return glob(os.path.join(self.folderName, self.archiveFileNamePrefix) + "*")

    def writeTimeInformationToFile(self, pathWithFileName, timeInformation):
        """ Writes time information to file, checks if file is too large and creates a new file if necessary """
        self.appendLinesToFile(pathWithFileName, [timeInformation]) #The square brackets in [timeInformation] are necessary because otherwise, each character in the list or string will get written to a new line in the file

    """ Copy file to another directory. Renaming while moving is possible.  If destination specifies a directory, the file will be copied into destination using the base filename from the source. If destination specifies a file that already exists, it will be replaced. """
    def copyFile(self, filenameWithPath, destinationFolderOrFileWithPath):
        pathToCopiedFile = None
        try:
            pathToCopiedFile = shutil.copy2(filenameWithPath, destinationFolderOrFileWithPath)
        except FileNotFoundError:
            logging.error("Could not find file: " + filenameWithPath + " or folder " + destinationFolderOrFileWithPath)    
        return pathToCopiedFile
    
    def getListOfFilesInThisFolder(self, folderNameWithPath):
        return next(os.walk(folderNameWithPath))[self.FILES_IN_FOLDER]
    
    def getListOfSubfoldersInThisFolder(self, folderNameWithPath):
        return next(os.walk(folderNameWithPath))[self.SUBDIRECTORIES]    