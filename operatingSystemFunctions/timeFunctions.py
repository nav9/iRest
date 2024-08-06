import time
import logging
import traceback

# time.clock() gives the best timer accuracy on Windows, while the time.time() function gives the best accuracy on Unix/Linux. 
# So these classes were necessary to build OS-specific time functions.

""" This class needed to be created to be able to have dependency injection for time functions. 
It was necessary to be able to create a separate TimeFunctions class in test cases to be able to
test supplying various time values to the Timer class. Without that, it'd be very hard to write
test cases that need to check for elapses of large units of time """
class TimeFunctions_Linux:
    def __init__(self) -> None:
        self.pastTime = time.time()
        self.MAX_TOLERABLE_NEGATIVE_ELAPSED_TIME = 3 #number of seconds considered acceptable if elapsed time is negative. This should ideally be at least 2 second more than TEXT_UPDATE_INTERVAL_SECOND, since it can take time for functions like the one that determines screenlock, to return
    
    def getElapsedDurationSinceThisTime(self, timestamp):
        """ Is not concerned with pastTime. Returns elapsedDuration, currentTime """
        currentTime = time.time()
        elapsedDuration = self.__raiseAndLogErrorIfSignificantNegativeDuration(currentTime, timestamp)        
        return elapsedDuration, currentTime
    
    def getElapsedDuration(self):
        """ Does not update pastTime. Returns elapsedDuration, currentTime """
        currentTime = time.time()
        elapsedDuration = self.__raiseAndLogErrorIfSignificantNegativeDuration(currentTime, self.pastTime)
        return elapsedDuration, currentTime
    
    def getElapsedDurationSinceTheLastCheck(self):
        """ Updates past time. Returns elapsedDuration, currentTime """
        elapsedDuration, currentTime = self.getElapsedDuration()
        self.pastTime = currentTime
        return elapsedDuration, currentTime
    
    def setPastTimeToCurrentTime(self, currentTime):
        self.pastTime = currentTime
    
    def getCurrentTime(self):
        return time.time()
    
    def getTimeFormattedAsHMS(self, timestamp):
        return time.strftime("%Hh %Mm %Ss", time.gmtime(timestamp))  
    
    def __raiseAndLogErrorIfSignificantNegativeDuration(self, currentTime, pastTime):  
        """ returns abs(duration) if the difference in current and past time is very small. Such a negative value can occur due to system delays (like querying for screen lock), but it helps to check if there's a bug """
        duration = currentTime - pastTime #elapsed duration
        if duration < 0:#this should be logged even if an error isn't thrown (to be able to investigate the cause)
            errorMessage = f"Elapsed duration {duration} is negative. Past time {pastTime} cannot be higher than current time {currentTime}. Call Stack {"".join(traceback.format_stack())}."
            logging.error(errorMessage)
            if abs(duration) > self.MAX_TOLERABLE_NEGATIVE_ELAPSED_TIME:
                raise ValueError(errorMessage)  
            else:#the difference in time is too small, so ignore the negative time
                duration = abs(duration)
        return duration
    
    def isNight(self):
        night = False
        currentTime = time.time()
        hour = int(time.strftime("%H", time.localtime(currentTime)))
        if hour >= 19 or hour <= 6:#time between 7pm and 6am
            night = True
        return night
            
""" Used to periodically check whether a certain amount of time has elapsed"""
class TimeElapseChecker_Linux:
    def __init__(self, maxDuration_seconds) -> None:
        self.DURATION = maxDuration_seconds
        self.timeFunc = TimeFunctions_Linux()

    def didDurationElapse(self):
        elapsed = False
        elapsedDuration, currentTime = self.timeFunc.getElapsedDuration()
        if elapsedDuration >= self.DURATION:
            elapsed = True
            self.timeFunc.setPastTimeToCurrentTime(currentTime)
        return elapsed, elapsedDuration, currentTime #when used in a statement like "if didTimeElapse():", the timeElapsed bool will be considered even if elapsedDuration is also returned
