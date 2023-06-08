import os
import time
from timer import timers
from collections import deque
from configuration import configHandler
from diskOperations import timeFileManager
from diskOperations import fileAndFolderOperations

class TestConstants:
    TESTS_FOLDER = "tests"

class TestTimeFileManager:    

    def test_loadingWrittenDataFromTimeFile(self):
        currentTime = 1667673922.2530432
        fileFolderOps = fileAndFolderOperations.FileOperations()
        archiveFolder = os.path.join(TestConstants.TESTS_FOLDER, configHandler.Names.ARCHIVE_FOLDER, "")
        fileFolderOps.deleteFolderIfItExists(archiveFolder)        
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        assert len(tm.historicalStrainData) == 0 #because the folder is deleted. So there shouldn't be any past time data
        #---write some time information
        STRAIN_DATA_HISTORY_LENGTH = tm.STRAIN_DATA_HISTORY_LENGTH
        numberOfWrites = STRAIN_DATA_HISTORY_LENGTH - 1 #keeping it within the immediate time file limit (so as to not dig into archived files)
        for _ in range(numberOfWrites):
            tm.writeTimeInformationToFile(currentTime, timers.NatureOfActivity.EYES_BEING_STRAINED) 
            currentTime += 10 #seconds
        assert len(tm.historicalStrainData) == numberOfWrites
        #---program is assumed to have stopped now and started again
        del tm
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        assert len(tm.historicalStrainData) == numberOfWrites
        
    def test_orderOfLoadingDataFromTimeFileAndArchiveFiles(self):
        currentTime = 1667673922.2530432
        fileFolderOps = fileAndFolderOperations.FileOperations()
        archiveFolder = os.path.join(TestConstants.TESTS_FOLDER, configHandler.Names.ARCHIVE_FOLDER, "")
        fileFolderOps.deleteFolderIfItExists(archiveFolder)        
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName                
        tm.TIMER_FILE_MAX_SIZE = 200 #bytes        
        tm.FREQUENCY_TO_CHECK_FILE_SIZE = 5
        STRAIN_DATA_HISTORY_LENGTH = 34
        tm.clearAndResetHistoricalStrainDataSizeTo(STRAIN_DATA_HISTORY_LENGTH)
        assert len(tm.historicalStrainData) == 0 #because the folder is deleted. So there shouldn't be any past time data
        #---write some time information
        STRAIN_DATA_HISTORY_LENGTH = tm.STRAIN_DATA_HISTORY_LENGTH
        dataWritten = deque() #for comparing when the data is re-loaded from timefile and archive files
        for _ in range(STRAIN_DATA_HISTORY_LENGTH):
            tm.writeTimeInformationToFile(currentTime, timers.NatureOfActivity.EYES_BEING_STRAINED) #writing to file
            packedData = tm.packTheTimeDataForWriting(currentTime, timers.NatureOfActivity.EYES_BEING_STRAINED)
            dataWritten.append(packedData) #storing a copy of what was written to file, to be able to compare later if all data was read back properly in the right order
            currentTime += 10 #seconds
        
        #---program is assumed to have stopped now and started again
        del tm
        tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        tm.clearAndResetHistoricalStrainDataSizeTo(STRAIN_DATA_HISTORY_LENGTH)
        tm.extractHistoricalTimeDataFromFiles() #reload the data with the newly set history length which can store all the written data in memory
        assert STRAIN_DATA_HISTORY_LENGTH == len(tm.historicalStrainData)
        assert dataWritten == tm.historicalStrainData #checks if data loaded in exactly the same order as it was written
        
    
    # def test_DefaultTimer_loadingWrittenDataFromArchiveFilesOnly(self):
    #     """ When an archive file is created, it is done by renaming the timefile to the archive file name. This function tests if the data is loaded correctly if only the archive files are present and no timefile is present """
    #     currentTime = 1667673922.2530432
    #     fileFolderOps = fileAndFolderOperations.FileOperations()
    #     archiveFolder = os.path.join(TestConstants.TESTS_FOLDER, configHandler.Names.ARCHIVE_FOLDER, "")
    #     fileFolderOps.deleteFolderIfItExists(archiveFolder)        
    #     tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
    #     #---tweak values for easier testing
    #     tm.FREQUENCY_TO_CHECK_FILE_SIZE = 50
    #     tm.TIMER_FILE_MAX_SIZE = 1000 #bytes
    #     howOftenToCheckForArchiveFiles = 40
    #     #---keep writing data until at least two archive files are created
    #     numberOfWrites = 0
    #     while True:
    #         tm.writeTimeInformationToFile(currentTime, timers.NatureOfActivity.EYES_BEING_STRAINED) 
    #         currentTime += 10 #seconds
    #         numberOfWrites += 1
    #         #---check if at least 2 archive files are created. If yes, exit the loop 
    #         #if numberOfWrites % howOftenToCheckForArchiveFiles == 0:
    #         listOfArchiveFiles = fileFolderOps.getListOfFilesInThisFolderWithThisPrefix(archiveFolder, tm.archiveFileNamePrefix)
    #         if len(listOfArchiveFiles) >= 2:
    #             break        
    #     #---program is assumed to have stopped now and started again
    #     del tm
    #     #Note: a TimeFileManager will be created automatically inside DefaultTimer
    #     operatingSystemAdapter = None
    #     defaultTimer = timers.DefaultTimer(operatingSystemAdapter, fileFolderOps, archiveFolder, configHandler.Names.TIME_FILE)
    #     #tm.FREQUENCY_TO_CHECK_FILE_SIZE = 10
    #     #---the amount of strained time has to be equal to the STRAIN_DATA_HISTORY_LENGTH
    #     assert False
        