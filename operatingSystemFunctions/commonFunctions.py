import subprocess
import logging
import time

class Constants:
    FIRST_ELEMENT_OF_ARRAY = 0
    SECOND_ELEMENT_OF_ARRAY = 1

class CommonFunctions_Linux:
    def __init__(self) -> None:
        pass

    def isThisAppInstalled(self, appName):
        appInstalled = False
        logging.info(f"Checking if {appName} is installed...")
        status = subprocess.getstatusoutput("dpkg-query -W -f='${Status}' " + appName)
        if not status[Constants.FIRST_ELEMENT_OF_ARRAY]:
            if 'installed' in status[Constants.SECOND_ELEMENT_OF_ARRAY]:
                appInstalled = True
        return appInstalled
    
    def executeBashCommand(self, theCommand):
        theProcess = subprocess.Popen(theCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        receivedOutput = " ".join(str(x) for x in theProcess.stdout.readlines()) #readlines() returns a list. This line converts the list to a string
        return receivedOutput
    
