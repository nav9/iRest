import os
import time
from timer import timers
from collections import deque
from diskOperations import timeFileManager
from diskOperations import fileAndFolderOperations

class TestsConstants:
    TESTS_FOLDER = "tests"
    FIRST_ELEMENT_OF_LIST = 0

class TestTimeFileManager:
    def test_loadingWrittenDataFromTimeFile(self):
        #currentTime = time.time()
        currentTime = 1667673922.2530432
        fileFolderOps = fileAndFolderOperations.FileOperations()
        archiveFolder = os.path.join(TestsConstants.TESTS_FOLDER, timers.Names.ARCHIVE_FOLDER, "")
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
        archiveFolder = os.path.join(TestsConstants.TESTS_FOLDER, timers.Names.ARCHIVE_FOLDER, "") #create archive files within the tests folder itself
        fileFolderOps.deleteFolderIfItExists(archiveFolder)        
        tm = timeFileManager.TimeFileManager(archiveFolder, timers.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        tm.TIMER_FILE_MAX_SIZE = 1000 #bytes. Set the condition for creating archive files early
        tm.FREQUENCY_TO_CHECK_FILE_SIZE = 1 
        #---write some time information
        numberOfWrites = 1010
        writtenData = deque()
        for _ in range(numberOfWrites):
            tm.writeTimeInformationToFile(currentTime, timers.NatureOfActivity.EYES_BEING_STRAINED) 
            writtenData.append(currentTime)
            currentTime += 10 #seconds
        #---now read the info from the timer file and the archive files and check if it matches with the order in which it was written
        #create a new class which will load the data
        tm2 = timeFileManager.TimeFileManager(archiveFolder, timers.Names.TIME_FILE, fileFolderOps) #parameters passed: folderName, fileName        
        while True:
            written = writtenData.pop()
            loaded = tm2.historicalStrainData.pop()
            assert written == loaded[TestsConstants.FIRST_ELEMENT_OF_LIST]
            if not tm2.historicalStrainData:#is empty
                break
