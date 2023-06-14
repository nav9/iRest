import time

""" This class needed to be created to be able to have dependency injection for time functions. 
It was necessary to be able to create a separate TimeFunctions class in test cases to be able to
test supplying various time values to the Timer class. Without that, it'd be very hard to write
test cases that need to check for elapses of large units of time """
class TimeFunctions_Linux:
    def getCurrentTime(self):
        return time.time()
    
    def getTimeFormattedAsHMS(self, timestamp):
        return time.strftime("%Hh %Mm %Ss", time.gmtime(timestamp))
    