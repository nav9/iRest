import PySimpleGUI as simpleGUI
from abc import ABC, abstractmethod
from diskOperations import fileAndFolderOperations

simpleGUI.theme('Dark') 
backgroundColorOfGUI = simpleGUI.LOOK_AND_FEEL_TABLE['Dark']['BACKGROUND']

class MoreConstants:#TODO: consolidate these into one place
    FIRST_ELEMENT_OF_ARRAY = 0
    ICON_PATH = "icons"

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
    MAIN_PROGRAM_ICON = 'iRest_icon.png'
    PLAY_ICON = 'play.png' #TODO: shift these paths to config file
    PAUSE_ICON = 'pause.png'
    AUDIO_ICON = 'audio.png'
    MUTE_ICON = 'mute.png'

#Note: This abstract class specifies what functions all GUI sections should implement
class RestTimers(ABC): #Abstract parent class
    #Note: Any abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def getLayout(self):
        """ Returns the GUI arrangement for a section of the UI that needs to be displayed """
        pass

    @abstractmethod
    def runEventLoop(self, event, values):
        """ Allows processing any GUI events that are relevant to this UI section """
        pass

    @abstractmethod
    def registerMainWindowReference(self, window):
        """ To perform updates on the layout, each mini GUI needs to have a reference to the main window """
        pass    

class DefaultTimerLayout:#The layouts will be initialized in the timer classes and then be passed to the main interface
    def __init__(self, backendRef) -> None:
        self.timer = backendRef  
        self.mainWindow = None #a reference to the main GUI window which will get set via a registerMainWindowReference function
        self.playButton = b'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'
        self.buttonStrings = dict()
        self.__loadButtonImages()
        self.buttonHoverBackgroundColor = 'grey'
        self.borderWidth = 0
        self.layout = [                        
                        [simpleGUI.Text("Strained time: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.STRAINED_TIME_TEXT), simpleGUI.Text("Allowed strain: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.ALLOWED_STRAIN_TEXT)],
                        [simpleGUI.Text(f"Program Status: "), simpleGUI.Text(WidgetConstants.DEFAULT_TIMER_RUNNING_MESSAGE, size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.DEFAULT_TIMER_STATUS_TEXT), simpleGUI.Text(f"Audio Status: "), simpleGUI.Text(WidgetConstants.AUDIO_ACTIVE_MESSAGE, size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.AUDIO_STATUS_TEXT)],
                        #[simpleGUI.Button(WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON), simpleGUI.Button(WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON)],
                        [simpleGUI.Button('', key=WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON, image_data=self.buttonStrings[WidgetConstants.PLAY_ICON], button_color=(self.buttonHoverBackgroundColor, backgroundColorOfGUI), border_width=self.borderWidth), simpleGUI.Button(WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON, key=WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON)],
                    ]
        
    def getLayout(self):
        return self.layout
    
    def __loadButtonImages(self):
        fileOps = fileAndFolderOperations.FileOperations()
        imagesToLoad = [WidgetConstants.PLAY_ICON, WidgetConstants.PAUSE_ICON, WidgetConstants.AUDIO_ICON, WidgetConstants.MUTE_ICON]
        for image in imagesToLoad:
            self.buttonStrings[image] = fileOps.getFileAsBase64EncodedString(MoreConstants.ICON_PATH, image)

    def runEventLoop(self, event, values):#this gets invoked from the main GUI interface class
        strainedDuration, allowedStrainDuration, formattedStrainedTime = self.timer.getStrainDetails()
        self.mainWindow[WidgetConstants.STRAINED_TIME_TEXT].update(formattedStrainedTime) #update the info shown about strained time
        self.mainWindow[WidgetConstants.ALLOWED_STRAIN_TEXT].update(allowedStrainDuration)
        if event == WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON:
            paused = self.timer.togglePauseStrainedTimeMeasurement()
            message = "Unknown"
            if paused: message = "Paused"
            else: message = WidgetConstants.DEFAULT_TIMER_RUNNING_MESSAGE    
            self.mainWindow[WidgetConstants.DEFAULT_TIMER_STATUS_TEXT].update(message)
        if event == WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON:
            toggleState = self.timer.toggleAllAudioNotifiers()
            message = "No audio notifiers"
            if toggleState == None: 
                pass
            else:
                if toggleState: message = WidgetConstants.AUDIO_ACTIVE_MESSAGE
                else: message = "Audio muted"
            self.mainWindow[WidgetConstants.AUDIO_STATUS_TEXT].update(message)
    
    # def playPauseClicked(self):
    #     print("called")
    #     paused = self.timer.togglePauseStrainedTimeMeasurement()
    #     message = "Unknown"
    #     if paused: message = "Paused"
    #     else: message = WidgetConstants.DEFAULT_TIMER_RUNNING_MESSAGE    
    #     self.mainWindow[WidgetConstants.DEFAULT_TIMER_STATUS_TEXT].update(message)

    def loadPlayButton(self):
        pass

    def registerMainWindowReference(self, window):    
        self.mainWindow = window

class WarmthLayout:#This is an optional layout that gets created only if the specified colour temperature app is installed
    def __init__(self, appRef) -> None:        
        self.warmthApp = appRef
        self.mainWindow = None
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
    
    def runEventLoop(self, event, values):    
        if self.warmthApp:
            if event == WidgetConstants.SCT_SLIDER:
                warmthValue = values[WidgetConstants.SCT_SLIDER]
                self.warmthApp.setCustomWarmth(warmthValue)  

    def registerMainWindowReference(self, window):    
        self.mainWindow = window

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
        
    def addThisBackend(self, backendRef):
        self.backends.append(backendRef)
        self.backendGUIRefs.append(backendRef.getGUIRef())
        
    def createLayout(self):
        for guiRef in self.backendGUIRefs:#iterate all the supplied layouts and append them in the main interface
            receivedLayout = guiRef.getLayout()
            if receivedLayout:#the layout received can be [] if the backend does not need to implement a GUI
                self.layout.extend(receivedLayout) 
        #---create the window using all supplied layouts
        iconFile = self.__loadMainProgramIcon() 
        self.window = simpleGUI.Window(WidgetConstants.WINDOW_TITLE, icon = iconFile, layout = self.layout)
        #---register the main window in all GUI layouts
        for guiRef in self.backendGUIRefs:
            guiRef.registerMainWindowReference(self.window)
    
    def runEventLoop(self):#this function should get called repeatedly from an external while loop
        event, values = self.window.read(timeout = self.WINDOW_WAIT_TIMEOUT_MILLISECOND) 
        if event == simpleGUI.WIN_CLOSED or event == simpleGUI.Exit:
            self.closeWindow()
        for guiRef in self.backendGUIRefs:
            if guiRef:#this value can be None if the backend has no GUI
                guiRef.runEventLoop(event, values)       
    
    def closeWindow(self):
        self.window.close()
        self.programRunning = False
        
    def checkIfNotClosedGUI(self):
        return self.programRunning
    
    def __loadMainProgramIcon(self):
        fileOps = fileAndFolderOperations.FileOperations()
        return fileOps.joinPathAndFilename(MoreConstants.ICON_PATH, WidgetConstants.MAIN_PROGRAM_ICON)
    