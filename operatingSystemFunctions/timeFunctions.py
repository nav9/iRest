import time

""" This class needed to be created to be able to have dependency injection for time functions. 
It was necessary to be able to create a separate TimeFunctions class in test cases to be able to
test supplying various time values to the Timer class. Without that, it'd be very hard to write
test cases that need to check for elapses of large units of time """
class TimeFunctions:
    def getCurrentTime(self):
        return time.time()
    
    def getTimeFormattedAsHMS(self, timestamp):
        return time.strftime("%Hh %Mm %Ss", time.gmtime(timestamp))    

""" Used to periodically check whether a certain amount of time has elapsed"""
class TimeElapseChecker:
    def __init__(self, maxDuration_seconds) -> None:
        self.DURATION = maxDuration_seconds
        self.pastTime = time.time()

    def didTimeElapse(self):
        timeElapsed = False
        currentTime = time.time()
        if self.pastTime - currentTime >= self.DURATION:
            timeElapsed = True
            self.pastTime = currentTime
        else:
            if self.pastTime - currentTime < 0:
                raise ValueError(f"Past time {self.pastTime} cannot be higher than current time {currentTime}.")
        return timeElapsed
