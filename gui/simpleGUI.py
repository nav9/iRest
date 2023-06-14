import os
import PySimpleGUI as simpleGUI
from abc import ABC, abstractmethod

simpleGUI.theme('Dark') 

class MoreConstants:#TODO: consolidate these into one place
    FIRST_ELEMENT_OF_ARRAY = 0

class WidgetConstants:
    TEXT_SIZE = (12, 1)
    STRAINED_TIME_TEXT = '-statusTextfield-'
    ALLOWED_STRAIN_TEXT = '-allowedStrain-'
    DEFAULT_TIMER_STATUS_TEXT = '-DefaultTimerStatus-'
    AUDIO_STATUS_TEXT = '-AudioStatus-'
    DEFAULT_TIMER_RUNNING_MESSAGE = "Running"
    AUDIO_ACTIVE_MESSAGE = "Audio active"
    PAUSE_RUN_TOGGLE_BUTTON = 'Pause/Run'
    MUTE_UNMUTE_TOGGLE_BUTTON = 'Mute/Unmute'
    MUTE_BUTTON = 'Mute'
    UNMUTE_BUTTON = 'Un-mute'
    WINDOW_TITLE = 'iRest'
    SCT_SLIDER = '-sct slider-'
    SCT_SLIDER_SIZE = (1, 10)
    
#Note: This abstract class specifies what functions all GUI sections should implement
class RestTimers(ABC): #Abstract parent class
    #Note: Any abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def getLayout(self):
        """ Returns the GUI arrangement for a section of the UI that needs to be displayed """
        pass

    @abstractmethod
    def runEventLoop(self, window, event, values):
        """ Allows processing any GUI events that are relevant to this UI section """
        pass

class DefaultTimerLayout:#The layouts will be initialized in the timer classes and then be passed to the main interface
    def __init__(self, backendRef) -> None:
        self.timer = backendRef      
        self.layout = [                        
                        [simpleGUI.Text("Strained time: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.STRAINED_TIME_TEXT), simpleGUI.Text("Allowed strain: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.ALLOWED_STRAIN_TEXT)],
                        [simpleGUI.Text(f"Program Status: "), simpleGUI.Text(WidgetConstants.DEFAULT_TIMER_RUNNING_MESSAGE, size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.DEFAULT_TIMER_STATUS_TEXT), simpleGUI.Text(f"Audio Status: "), simpleGUI.Text(WidgetConstants.AUDIO_ACTIVE_MESSAGE, size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.AUDIO_STATUS_TEXT)],
                        [simpleGUI.Button(WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON), simpleGUI.Button(WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON)],
                    ]
        
    def getLayout(self):
        return self.layout
    
    def runEventLoop(self, window, event, values):#this gets invoked from the main GUI interface class
        strainedDuration, allowedStrainDuration, formattedStrainedTime = self.timer.getStrainDetails()
        window[WidgetConstants.STRAINED_TIME_TEXT].update(formattedStrainedTime) #update the info shown about strained time
        window[WidgetConstants.ALLOWED_STRAIN_TEXT].update(allowedStrainDuration)
        if event == WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON:
            paused = self.timer.togglePauseStrainedTimeMeasurement()
            message = "Unknown"
            if paused: message = "Paused"
            else: message = WidgetConstants.DEFAULT_TIMER_RUNNING_MESSAGE    
            window[WidgetConstants.DEFAULT_TIMER_STATUS_TEXT].update(message)
        if event == WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON:
            toggleState = self.timer.toggleAllAudioNotifiers()
            message = "No audio notifiers"
            if toggleState == None: 
                pass
            else:
                if toggleState: message = WidgetConstants.AUDIO_ACTIVE_MESSAGE
                else: message = "Audio muted"
            window[WidgetConstants.AUDIO_STATUS_TEXT].update(message)
    

class WarmthLayout:#This is an optional layout that gets created only if the specified colour temperature app is installed
    def __init__(self, appRef) -> None:        
        self.warmthApp = appRef
        if not self.warmthApp.isAppInstalled():
            self.warmthApp = None 
            self.layout = [] #no GUI needed because there's no colour temperature app
        else:
            minVal, maxVal, defaultVal = self.warmthApp.getMinMaxDefaultValues()
            self.warmthApp.setCustomWarmth(defaultVal)                   
            self.layout = [                        
                            [simpleGUI.Text("Warmth:"), simpleGUI.Slider(size=WidgetConstants.SCT_SLIDER_SIZE, tick_interval=3000, range=(minVal, maxVal), default_value=defaultVal, expand_x=True, enable_events=True, orientation='horizontal', key=WidgetConstants.SCT_SLIDER)],
                        ]
        
    def getLayout(self):
        return self.layout
    
    def runEventLoop(self, window, event, values):    
        if self.warmthApp:
            if event == WidgetConstants.SCT_SLIDER:
                warmthValue = values[WidgetConstants.SCT_SLIDER]
                self.warmthApp.setCustomWarmth(warmthValue)  


#-------------------------------------------------------------------------------------------------
# This is the main GUI interface which aggregates multiple GUI elements which can have their own
# backend implementations.
#-------------------------------------------------------------------------------------------------
class MainInterface:
    def __init__(self):
        #simpleGUI.theme('Dark Blue 13') 
        self.WINDOW_WAIT_TIMEOUT_MILLISECOND = 100 #the amount of time the window waits for user input before relinquishing control to other processes
        self.programRunning = True
        self.window = None #will be instantiated when layout is created
        self.backends = [] #the backend objects related to the GUI section being displayed
        self.backendGUIRefs = [] #the GUI layout objects 
        self.layout = []
        self.iconFile = os.path.join("icons", "iRest_icon.png") #TODO: move strings to config file
        
    def addThisBackend(self, backendRef):
        self.backends.append(backendRef)
        self.backendGUIRefs.append(backendRef.getGUIRef())
        
    def createLayout(self):
        for guiRef in self.backendGUIRefs:#iterate all the supplied layouts and append them in the main interface
            receivedLayout = guiRef.getLayout()
            if receivedLayout:#the layout received can be [] if the backend does not need to implement a GUI
                self.layout.extend(receivedLayout) 
        #---create the window using all supplied layouts
        self.window = simpleGUI.Window(WidgetConstants.WINDOW_TITLE, icon = self.iconFile, layout = self.layout)
    
    def runEventLoop(self):#this function should get called repeatedly from an external while loop
        event, values = self.window.read(timeout = self.WINDOW_WAIT_TIMEOUT_MILLISECOND) 
        if event == simpleGUI.WIN_CLOSED or event == simpleGUI.Exit:
            self.closeWindow()
        for guiRef in self.backendGUIRefs:
            if guiRef:#this value can be None if the backend has no GUI
                guiRef.runEventLoop(self.window, event, values)       
    
    def closeWindow(self):
        self.window.close()
        self.programRunning = False
        
    def checkIfNotClosedGUI(self):
        return self.programRunning