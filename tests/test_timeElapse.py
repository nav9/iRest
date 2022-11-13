import os
import time
from timer import timers
from diskOperations import timeFileManager
from diskOperations import fileAndFolderOperations

class TestTimeFileManager:
    def test_loadingWrittenDataFromTimeFile(self):
        #currentTime = time.time()
        currentTime = 1667673922.2530432
        fileFolderOps = fileAndFolderOperations.FileOperations()
        archiveFolder = os.path.join("tests", timers.Names.ARCHIVE_FOLDER, "")
        fileFolderOps.deleteFolderIfItExists(archiveFolder)        
        tm = timeFileManager.TimeFileManager(archiveFolder, timers.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
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
        tm = timeFileManager.TimeFileManager(archiveFolder, timers.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        assert len(tm.historicalStrainData) == numberOfWrites
        
    def test_loadingWrittenDataFromArchiveFiles(self):
        currentTime = 1667673922.2530432
        fileFolderOps = fileAndFolderOperations.FileOperations()
        archiveFolder = os.path.join("tests", timers.Names.ARCHIVE_FOLDER, "")
        fileFolderOps.deleteFolderIfItExists(archiveFolder)        
        tm = timeFileManager.TimeFileManager(archiveFolder, timers.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        tm.FREQUENCY_TO_CHECK_FILE_SIZE = 10
        #---write some time information
        STRAIN_DATA_HISTORY_LENGTH = tm.STRAIN_DATA_HISTORY_LENGTH
        numberOfWrites = STRAIN_DATA_HISTORY_LENGTH - 1 #keeping it within the immediate time file limit
        for _ in range(numberOfWrites):
            tm.writeTimeInformationToFile(currentTime, timers.NatureOfActivity.EYES_BEING_STRAINED) 
            currentTime += 10 #seconds
        assert len(tm.historicalStrainData) == numberOfWrites
        #---program is assumed to have stopped now and started again
        del tm
        tm = timeFileManager.TimeFileManager(archiveFolder, timers.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        tm.FREQUENCY_TO_CHECK_FILE_SIZE = 10
        assert len(tm.historicalStrainData) == numberOfWrites        