import logging
from operatingSystemFunctions import commonFunctions, timeFunctions
from gui import simpleGUI
import traceback

#Since Ubuntu has a default night light app, it is not necessary to force a user
#to ensure that iRest also has nightlight enabled. So if sct is installed, the
#feature can be displayed. Else, the option can be provided in settings, to enable
#it by having it installed. But if sct isn't available, nothing regarding nightlight
#should be displayed on the main GUI.
#TODO: consider using xsct
class WarmColour_Linux:#Also called NightLight
    def __init__(self) -> None:
        self.SCT_MIN_VALUE = 1000 #The sct program's minimum possible value for colour temperature
        self.SCT_MAX_VALUE = 10000 #The sct program's maximum possible value for colour temperature
        self.SCT_DEFAULT_VALUE = 4000 #daytime warmth
        self.commonFunctions = commonFunctions.CommonFunctions_Linux()                        
        self.appName = 'sct'          
        self.appInstalled = self.__isSimpleColorTemperatureAppInstalled()
        self.GUI_Layout = None
        if self.appInstalled:
            if self.__checkIfNight():
                self.SCT_DEFAULT_VALUE = 2300 #make it warmer than default. Night warmth
            self.GUI_Layout = simpleGUI.WarmthLayout(self)

    def getGUIRef(self):
        return self.GUI_Layout
    
    def isAppInstalled(self):
        return self.appInstalled

    def setCustomWarmth(self, warmthValue):
        sctCommand = f"{self.appName} {warmthValue}"
        logging.debug(f"Setting system color temperature to {warmthValue}")
        receivedOutput = self.commonFunctions.executeBashCommand(sctCommand)

    def getMinMaxDefaultValues(self):
        return self.SCT_MIN_VALUE, self.SCT_MAX_VALUE, self.SCT_DEFAULT_VALUE

    def __checkIfNight(self):
        timeChecker = timeFunctions.TimeFunctions_Linux()
        return timeChecker.isNight()

    def __isSimpleColorTemperatureAppInstalled(self):
        sctPresent = False        
        try:              
            sctPresent = self.commonFunctions.isThisAppInstalled(self.appName)
        except FileNotFoundError as e:
            sctPresent = False
            callstack = "".join(traceback.format_stack())
            logging.error(f"Error encountered: {e}. Stacktrace {callstack}")
        if not sctPresent:
            logging.warn("--------- OPTIONAL INSTALL ---------")                      
            logging.warn(f"{self.appName} is missing. Please install it using 'sudo apt install -y sct' and restart iRest if you want night light (warm colour temperature) features.")
        logging.info(f"{self.appName} present: {sctPresent}")
        return sctPresent    
        