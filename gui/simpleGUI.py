import os
import PySimpleGUI as simpleGUI

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
    

class DefaultTimerLayout:#The layouts will be initialized in the timer classes and then be passed to the main interface
    def __init__(self, backendRef) -> None:
        self.timer = backendRef
        self.warmthApp = backendRef.getWarmthAppReference()
        if not self.warmthApp.isAppPresent():
            self.warmthApp = None        
        self.layout = [                        
                        [simpleGUI.Text("Strained time: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.STRAINED_TIME_TEXT), simpleGUI.Text("Allowed strain: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.ALLOWED_STRAIN_TEXT)],
                        [simpleGUI.Text(f"Program Status: "), simpleGUI.Text(WidgetConstants.DEFAULT_TIMER_RUNNING_MESSAGE, size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.DEFAULT_TIMER_STATUS_TEXT), simpleGUI.Text(f"Audio Status: "), simpleGUI.Text(WidgetConstants.AUDIO_ACTIVE_MESSAGE, size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.AUDIO_STATUS_TEXT)],
                        [simpleGUI.Button(WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON), simpleGUI.Button(WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON)],
                    ]
        if self.warmthApp:
            self.__addWarmthToLayoutUI()
        
    def getLayout(self):
        return self.layout
    
    def runEventLoop(self, window, event, values):
        strainedDuration, allowedStrainDuration, formattedStrainedTime = self.timer.getStrainDetails()
        window[WidgetConstants.STRAINED_TIME_TEXT].update(formattedStrainedTime)
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
            if toggleState == None: pass
            else:
                if toggleState: message = WidgetConstants.AUDIO_ACTIVE_MESSAGE
                else: message = "Audio muted"
            window[WidgetConstants.AUDIO_STATUS_TEXT].update(message)
        if self.warmthApp:
            if event == WidgetConstants.SCT_SLIDER:
                warmthValue = values[WidgetConstants.SCT_SLIDER]
                self.warmthApp.setCustomWarmth(warmthValue)  
    
    def __addWarmthToLayoutUI(self):
        minVal, maxVal, defaultVal = self.warmthApp.getMinMaxDefaultValues()
        warmthLayout = [simpleGUI.Text("Warmth:"), simpleGUI.Slider(size=WidgetConstants.SCT_SLIDER_SIZE, tick_interval=3000, range=(minVal, maxVal), default_value=defaultVal, expand_x=True, enable_events=True, orientation='horizontal', key=WidgetConstants.SCT_SLIDER)]
        self.layout.insert(MoreConstants.FIRST_ELEMENT_OF_ARRAY, warmthLayout) #add to the beginning of the list
        self.warmthApp.setCustomWarmth(defaultVal) 

class MainInterface:
    def __init__(self):
        #simpleGUI.theme('Dark Blue 13') 
        self.WINDOW_WAIT_TIMEOUT_MILLISECOND = 100 #the amount of time the window waits for user input before relinquishing control to other processes
        self.programRunning = True
        self.window = None #will be instantiated when layout is created
        self.backends = [] #the backend objects related to the GUI section being displayed
        self.backendGUIRefs = [] #the GUI layout objects 
        self.layout = []
        self.iconFile = os.path.join("icons", "iRest_icon.png")
        
    def addThisBackend(self, backendRef):
        self.backends.append(backendRef)
        self.backendGUIRefs.append(backendRef.getGUIRef())
        
    def createLayout(self):
        for guiRef in self.backendGUIRefs:#iterate all the supplied layouts and append them in the main interface
            self.layout.extend(guiRef.getLayout()) 
        #---create the window using all supplied layouts
        self.window = simpleGUI.Window(WidgetConstants.WINDOW_TITLE, icon = self.iconFile, layout = self.layout)
    
    def runEventLoop(self):#this function should get called repeatedly from an external while loop
        event, values = self.window.read(timeout = self.WINDOW_WAIT_TIMEOUT_MILLISECOND) 
        if event == simpleGUI.WIN_CLOSED or event == simpleGUI.Exit:
            self.closeWindow()
        for guiRef in self.backendGUIRefs:
            guiRef.runEventLoop(self.window, event, values)       
    
    def closeWindow(self):
        self.window.close()
        self.programRunning = False
        
    def checkIfNotClosedGUI(self):
        return self.programRunning