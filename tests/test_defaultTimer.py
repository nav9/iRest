from timer import timers
from configuration import configHandler
from diskOperations import timeFileManager
from diskOperations import fileAndFolderOperations
from tests import commonFunctions
from operatingSystemFunctions import operatingSystemDiversifier

#Each test case is designed to be a self-contained environment. Hence the large size.

class TestDefaultTimer:                
    def test_ensureStrainDataOfZeroDurationWritten_emptyTimeFileSituation(self):
        fileFolderOps = fileAndFolderOperations.FileOperations()
        comFunc = commonFunctions.CommonTestFunctions()   
        archiveFolder = comFunc.createNewTestFolder(fileFolderOps)  
        #---no timefile will be available at this time
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
        currentTime = dummyTime.actualTimeNow() - secondsElapsedSinceProgramWasLastRun #seconds
        timeManager.writeToFileAndHistoricalDataQueue(currentTime, elapsedTime, timers.NatureOfActivity.EYES_STRAINED) 
        assert 1 == len(timeManager.historicalStrainData)
        dummyOS = commonFunctions.DummyOperatingSystemAdapter()        
        #---create some time values that'll be used as the dummy time during DefaultTimer's calls to get current time
        dummyTime = commonFunctions.DummyTimeFunctions()
        timeAt_getElapsedDurationCall = dummyTime.actualTimeNow()
        timeAt_recordTimeElapsedCall = dummyTime.actualTimeNow()
        timeAt_saveActivityCall = dummyTime.actualTimeNow()
        timeSupply = [timeAt_getElapsedDurationCall, timeAt_recordTimeElapsedCall, timeAt_saveActivityCall]#because the checkStateChangeUpdateStrainDurationAndSave() function's internal calls need time values twice
        dummyTime.setDummyTimeValues(timeSupply)
        dummyOS.overrideDefaultDummyTimeFunctions(dummyTime)
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
        #---no timefile will be available at this time
        timeManager = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps)
        #---generate some strained time
        JUST_A_LARGE_NUMBER = 360
        actualTimeNow = dummyTime.actualTimeNow()
        currentTime = actualTimeNow - (JUST_A_LARGE_NUMBER * commonFunctions.ConstantsForTesting.INTERVAL_BETWEEN_WRITES)#calculate backward JUST_A_LARGE_NUMBER of times
        for _ in range(0, JUST_A_LARGE_NUMBER):
            elapsedTime = commonFunctions.ConstantsForTesting.INTERVAL_BETWEEN_WRITES #seconds elapsed while eyes were being strained just before currentTime        
            timeManager.writeToFileAndHistoricalDataQueue(currentTime, elapsedTime, timers.NatureOfActivity.EYES_STRAINED) 
            currentTime += elapsedTime  
        #---checking historicalStrainData length is important because this test case is about adding up past strain, and for that, historical data should be loaded
        assert JUST_A_LARGE_NUMBER == len(timeManager.historicalStrainData) 
        dummyOS = commonFunctions.DummyOperatingSystemAdapter()
        #---create some time values that'll be used as the dummy time during DefaultTimer's calls to get current time
        dummyTime = commonFunctions.DummyTimeFunctions()
        timeAt_getElapsedDurationCall = dummyTime.actualTimeNow()
        timeAt_recordTimeElapsedCall = dummyTime.actualTimeNow()
        timeAt_saveActivityCall = dummyTime.actualTimeNow()
        timeSupply = [timeAt_getElapsedDurationCall, timeAt_recordTimeElapsedCall, timeAt_saveActivityCall]#because the checkStateChangeUpdateStrainDurationAndSave() function's internal calls need time values twice
        dummyTime.setDummyTimeValues(timeSupply)
        dummyOS.overrideDefaultDummyTimeFunctions(dummyTime)
        #---creating default timer will automatically write to file, a line of strain duration being 0. This happens if no time file was present or no data was present in it
        defaultTimer = timers.DefaultTimer(dummyOS, timeManager)         
        strainedDuration = defaultTimer.getStrainedDuration()
        assert strainedDuration > 0

    def test_ensureThatElapsedTimeIsAccountedIfProgramIsSuspendedDuringExecuteFunction(self):
        fileFolderOps = fileAndFolderOperations.FileOperations()
        comFunc = commonFunctions.CommonTestFunctions()
        dummyTime = commonFunctions.DummyTimeFunctions()        
        archiveFolder = comFunc.createNewTestFolder(fileFolderOps)  
        #---no timefile will be available at this time
        timeManager = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps)
        dummyOS = commonFunctions.DummyOperatingSystemAdapter()
        #---create some time values that'll be used as the dummy time during DefaultTimer's calls to get current time
        dummyTime = commonFunctions.DummyTimeFunctions()
        timeAt_getElapsedDurationCall = dummyTime.actualTimeNow()
        #timeAt_recordTimeElapsedCall = dummyTime.actualTimeNow()
        #timeAt_saveActivityCall = dummyTime.actualTimeNow()
        #timeSupply = [timeAt_getElapsedDurationCall, timeAt_recordTimeElapsedCall, timeAt_saveActivityCall]#because the checkStateChangeUpdateStrainDurationAndSave() function's internal calls need time values twice
        timeSupply = [timeAt_getElapsedDurationCall]#because the checkStateChangeUpdateStrainDurationAndSave() function's internal calls need time values twice
        dummyTime.setDummyTimeValues(timeSupply)
        dummyOS.overrideDefaultDummyTimeFunctions(dummyTime)
        #---creating default timer will automatically write to file, a line of strain duration being 0. This happens if no time file was present or no data was present in it
        defaultTimer = timers.DefaultTimer(dummyOS, timeManager)         
        strainedDuration = defaultTimer.getStrainedDuration()
        #---strain should be zero here
        assert strainedDuration == 0
        notifier = commonFunctions.DummyNotifier()
        defaultTimer.addThisNotifierToListOfNotifiers(notifier)
        #---create a list of three time values that will be supplied when getCurrentTime() is called. This will help simulate a suspend state
        # first get the latest known time
        latestTimeData = timeManager.historicalStrainData[timers.OtherConstants.LAST_INDEX_OF_LIST]
        latestTime = timeManager.getTimestampFromData(latestTimeData)
        # create a time that'll be used in checkStateChangeUpdateStrainDurationAndSave() as current time. This time should normally be less than a second, but since we are simulating suspend state, it's being inflated to a large elapsed time that'll get detected as suspended state
        timeElapsedByTheTimeExecuteCalled = latestTime + timers.TimeConstants.SECONDS_IN_MINUTE + timers.OtherConstants.SECONDS_ELAPSED_BEFORE_ASSUMING_SUSPEND
        timeCheckedDuringNotificationCheck = timeElapsedByTheTimeExecuteCalled + timers.TimeConstants.SECONDS_IN_MINUTE + timers.OtherConstants.SECONDS_ELAPSED_BEFORE_ASSUMING_SUSPEND
        timeSupply = [timeElapsedByTheTimeExecuteCalled, timeCheckedDuringNotificationCheck]
        dummyTime.setDummyTimeValues(timeSupply)
        #---rather than call execute() of DefaultTimer, call the functions inside execute() to simulate the execute() call
        #########################################
        #### execute() begins here (you need to update the below lines if execute() is later modified in DefaultTimer())
        # getElapsedDurationSinceTheLastCheck() provides the time during execution of checkStateChangeUpdateStrainDurationAndSave()
        currentActivity, currentTime = defaultTimer.checkStateChangeUpdateStrainDurationAndSave()
        # getCurrentTime() gets called once during execution of notifyUserIfTheyNeedToTakeRest_afterCheckingForSuspend()
        assert currentActivity == timers.NatureOfActivity.EYES_STRAINED
        if currentActivity == timers.NatureOfActivity.EYES_STRAINED:
            defaultTimer.notifyUserIfTheyNeedToTakeRest_afterCheckingForSuspend(currentTime)         
        #### execute() ends here
        #########################################
        #---notifier should not have got called because of the long suspend time
        assert notifier.notified == False 
        #---ensure that suspend state was detected
        latestTimeData = timeManager.historicalStrainData[timers.OtherConstants.LAST_INDEX_OF_LIST]
        latestTime = timeManager.getNatureOfActivityFromData(latestTimeData)
        assert latestTime == timers.NatureOfActivity.SUSPENDED

#There should ideally be a few more test cases for conditions of screen lock and pause via GUI
