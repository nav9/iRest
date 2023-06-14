import os
from timer import timers
from collections import deque
from configuration import configHandler
from diskOperations import timeFileManager
from diskOperations import fileAndFolderOperations
from common import ConstantsForTesting, DummyTimeFunctions

class TestTimeFileManager:            
    def test_loadingWrittenDataFromTimeFile(self):
        currentTime = 1667673922.2530432
        elapsedTime = 0
        fileFolderOps = fileAndFolderOperations.FileOperations()
        archiveFolder = os.path.join(ConstantsForTesting.TESTS_FOLDER, configHandler.Names.ARCHIVE_FOLDER, "")
        fileFolderOps.deleteFolderIfItExists(archiveFolder)        
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        #---ensure that if no files were present, the historicalStrainData should be zero sized
        assert len(tm.historicalStrainData) == 0 #because the folder is deleted. So there shouldn't be any past time data
        #---write some time information
        STRAIN_DATA_HISTORY_LENGTH = tm.STRAIN_DATA_HISTORY_LENGTH
        numberOfWrites = STRAIN_DATA_HISTORY_LENGTH - 1 #keeping it within the immediate time file limit (so as to not dig into archived files)
        for _ in range(numberOfWrites):
            tm.writeToFileAndHistoricalDataQueue(currentTime, elapsedTime, timers.NatureOfActivity.EYES_STRAINED) 
            elapsedTime = DummyTimeFunctions.generateElapsedTime()
            currentTime += elapsedTime #seconds
        assert len(tm.historicalStrainData) == numberOfWrites
        #---program is assumed to have stopped now and started again
        del tm
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        assert len(tm.historicalStrainData) == numberOfWrites
        
    def test_orderOfLoadingDataFromTimeFileAndArchiveFiles(self):
        currentTime = 1667673922.2530432
        elapsedTime = 0
        fileFolderOps = fileAndFolderOperations.FileOperations()
        archiveFolder = os.path.join(ConstantsForTesting.TESTS_FOLDER, configHandler.Names.ARCHIVE_FOLDER, "")
        fileFolderOps.deleteFolderIfItExists(archiveFolder)        
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName                
        tm.TIMER_FILE_MAX_SIZE = 200 #bytes        
        tm.FREQUENCY_TO_CHECK_FILE_SIZE = 5
        STRAIN_DATA_HISTORY_LENGTH = 34
        tm.clearAndResetHistoricalStrainDataSizeTo(STRAIN_DATA_HISTORY_LENGTH)
        #---write some time information
        STRAIN_DATA_HISTORY_LENGTH = tm.STRAIN_DATA_HISTORY_LENGTH
        dataWritten = deque() #for comparing when the data is re-loaded from timefile and archive files
        for _ in range(STRAIN_DATA_HISTORY_LENGTH):
            tm.writeToFileAndHistoricalDataQueue(currentTime, elapsedTime, timers.NatureOfActivity.EYES_STRAINED) #writing to file
            packedData = tm.packTheTimeDataForWriting(currentTime, elapsedTime, timers.NatureOfActivity.EYES_STRAINED)
            dataWritten.append(packedData) #storing a copy of what was written to file, to be able to compare later if all data was read back properly in the right order
            elapsedTime = DummyTimeFunctions.generateElapsedTime()
            currentTime += elapsedTime #seconds        
        #---program is assumed to have stopped now and started again
        del tm
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        tm.clearAndResetHistoricalStrainDataSizeTo(STRAIN_DATA_HISTORY_LENGTH)
        tm.extractHistoricalTimeDataFromFiles() #reload the data with the newly set history length which can store all the written data in memory
        assert STRAIN_DATA_HISTORY_LENGTH == len(tm.historicalStrainData)
        assert dataWritten == tm.historicalStrainData #checks if data loaded in exactly the same order as it was written


# class TestDefaultTimer:        
#     def createNewTestFolder(self, fileFolderOps):
#         archiveFolder = os.path.join(ConstantsForTesting.TESTS_FOLDER, configHandler.Names.ARCHIVE_FOLDER, "")
#         fileFolderOps.deleteFolderIfItExists(archiveFolder) 
#         return archiveFolder        
    
#     def test_processingSingleLineOfDataInTimefile(self):#error happened once when the program didn't have a condition to handle a single line of data
#         fileFolderOps = fileAndFolderOperations.FileOperations()
#         archiveFolder = self.createNewTestFolder(fileFolderOps)
#         #---prime the timeFileManager with whatever parameters you want
#         tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps)


        