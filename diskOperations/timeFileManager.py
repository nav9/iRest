import os 
import logging

class TimeFileManager:
    def __init__(self, folderName, fileName):
        self.folderName = folderName
        self.fileName = fileName
        self.fullPath = os.path.join(self.folderName, self.fileName)
        self.fileOps = None

    def registerFileOperationsHandler(self, fileOperationsHandler):
        self.fileOps = fileOperationsHandler

    def writeTimeInformationToFile(self, epochTime):
        self.fileOps.writeTimeInformationToFile(self.fullPath, epochTime)