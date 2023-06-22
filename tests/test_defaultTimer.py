from timer import timers
from configuration import configHandler
from diskOperations import timeFileManager
from diskOperations import fileAndFolderOperations
from tests import commonFunctions
from operatingSystemFunctions import operatingSystemDiversifier

class TestDefaultTimer:                
    def test_ensureStrainDataOfZeroDurationWritten_emptyTimeFileSituation(self):
        fileFolderOps = fileAndFolderOperations.FileOperations()
        comFunc = commonFunctions.CommonTestFunctions()   
        archiveFolder = comFunc.createNewTestFolder(fileFolderOps)  
        #---prime the timeFileManager with whatever parameters you want
        timeManager = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps)
        assert 0 == len(timeManager.historicalStrainData) #ensure that the deque is empty. Means no time information is present in the file        
        operatingSystemCheck = operatingSystemDiversifier.OperatingSystemIdentifier()
        operatingSystemAdapter = operatingSystemCheck.getOperatingSystemAdapterInstance() #If OS could not be identified, it will return None                  
        #---creating default timer will automatically write to file, a line of strain duration being 0. This happens if no time file was present or no data was present in it
        defaultTimer = timers.DefaultTimer(operatingSystemAdapter, timeManager)
        assert 1 == len(timeManager.historicalStrainData) #only 1 piece of data should be present. That of the time elapsed since the program last ran  
        assert defaultTimer.strainedDuration == 0
        for timeData in reversed(timeManager.historicalStrainData):#iterates backward, to consider the latest data that was written, first
            #timestamp = tm.getTimestampFromData(timeData)
            duration = timeManager.getElapsedTimeFromData(timeData)
            activity = timeManager.getNatureOfActivityFromData(timeData)
            assert duration == 0
            assert activity == timers.NatureOfActivity.EYES_STRAINED

    def test_ensureLastTimeSinceProgramWasRunIsCheckedAndAccounted(self):
        fileFolderOps = fileAndFolderOperations.FileOperations()
        comFunc = commonFunctions.CommonTestFunctions()
        dummyTime = commonFunctions.DummyTimeFunctions()        
        archiveFolder = comFunc.createNewTestFolder(fileFolderOps)  
        #---prime the timeFileManager with some strained time which happened quite some time before the program is assumed to start
        timeManager = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps)
        secondsElapsedSinceProgramWasLastRun = 5000
        elapsedTime = 1200 #seconds elapsed while eyes were being strained just before currentTime
        currentTime = dummyTime.getCurrentTime() - secondsElapsedSinceProgramWasLastRun #seconds
        timeManager.writeToFileAndHistoricalDataQueue(currentTime, elapsedTime, timers.NatureOfActivity.EYES_STRAINED) 
        assert 1 == len(timeManager.historicalStrainData)
        dummyOS = commonFunctions.DummyOperatingSystemAdapter()
        #---creating default timer will automatically write to file, a line of strain duration being 0. This happens if no time file was present or no data was present in it
        defaultTimer = timers.DefaultTimer(dummyOS, timeManager)
        assert 3 == len(timeManager.historicalStrainData) #3 lines expected. 1.Strained time that was written, 2.Time elapsed since program started, 3.Zero strain data indicating program start
        assert defaultTimer.strainedDuration == 0
        expectedLines = [timers.NatureOfActivity.EYES_STRAINED, timers.NatureOfActivity.PROGRAM_NOT_RUNNING, timers.NatureOfActivity.EYES_STRAINED]
        ordinal = 0
        for timeData in reversed(timeManager.historicalStrainData):#iterates backward, to consider the latest data that was written, first
            #timestamp = tm.getTimestampFromData(timeData)
            #duration = tm.getElapsedTimeFromData(timeData)
            activity = timeManager.getNatureOfActivityFromData(timeData)
            assert expectedLines[ordinal] == activity
            ordinal += 1
        
    def test_ensureStrainedTimeIsRecognizedOnProgramRestart(self):
        fileFolderOps = fileAndFolderOperations.FileOperations()
        comFunc = commonFunctions.CommonTestFunctions()
        dummyTime = commonFunctions.DummyTimeFunctions()        
        archiveFolder = comFunc.createNewTestFolder(fileFolderOps)  
        #---prime the timeFileManager with some strained time that happened just some time ago
        timeManager = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps)
        #---generate some strained time
        JUST_A_LARGE_NUMBER = 360
        actualTimeNow = dummyTime.getCurrentTime()
        currentTime = actualTimeNow - (JUST_A_LARGE_NUMBER * commonFunctions.ConstantsForTesting.INTERVAL_BETWEEN_WRITES)#calculate backward JUST_A_LARGE_NUMBER of times
        for _ in range(0, JUST_A_LARGE_NUMBER):
            elapsedTime = commonFunctions.ConstantsForTesting.INTERVAL_BETWEEN_WRITES #seconds elapsed while eyes were being strained just before currentTime        
            timeManager.writeToFileAndHistoricalDataQueue(currentTime, elapsedTime, timers.NatureOfActivity.EYES_STRAINED) 
            currentTime += elapsedTime  
        #---checking historicalStrainData length is important because this test case is about adding up past strain, and for that, historical data should be loaded
        assert JUST_A_LARGE_NUMBER == len(timeManager.historicalStrainData) 
        dummyOS = commonFunctions.DummyOperatingSystemAdapter()
        #---creating default timer will automatically write to file, a line of strain duration being 0. This happens if no time file was present or no data was present in it
        defaultTimer = timers.DefaultTimer(dummyOS, timeManager)         
        strainedDuration = defaultTimer.getStrainedDuration()
        assert strainedDuration > 0

