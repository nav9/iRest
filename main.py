from timer import timers
import logging
from logging.handlers import RotatingFileHandler
from operatingSystemFunctions import operatingSystemDiversifier

logFileName = 'logs.log' #TODO: Shift to config file
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
log = logging.getLogger(__name__)
handler = RotatingFileHandler(logFileName , maxBytes=2000 , backupCount=5)#TODO: Shift to config file
log.addHandler(handler)
log.setLevel(logging.INFO)

if __name__ == '__main__':
    log.info("iRest program started")
    operatingSystemCheck = operatingSystemDiversifier.OperatingSystemChecker()
    operatingSystemAdapter = operatingSystemCheck.getOperatingSystemAdapterInstance()    
    timers = timers.DefaultTimer()
    timers.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getAudioNotifier()) #TODO: take notifiers from the config file
    timers.registerOperatingSystemAdapter(operatingSystemAdapter)#If OS was not identified, the adapter will be None

    while True:
        timers.checkIfUserNeedsEyeRest()
    
    