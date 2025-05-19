import FreeSimpleGUI as simpleGUI
from abc import ABC, abstractmethod
from diskOperations import fileAndFolderOperations
from configuration import configHandler as config
from operatingSystemFunctions import timeFunctions

#TODO: Switch to https://github.com/hoffstadt/DearPyGui or pyside

themeName = 'Dark'
simpleGUI.theme(themeName) 
backgroundColorOfGUI = simpleGUI.LOOK_AND_FEEL_TABLE[themeName]['BACKGROUND']

#class MoreConstants:#TODO: consolidate these into one place where all constants are found
    #FIRST_ELEMENT_OF_ARRAY = 0 #this is available in the config file
    #ICON_PATH = "icons"

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
        self.buttonStrings = dict()
        self.__loadButtonImages()
        self.buttonHoverBackgroundColor = 'grey'
        self.borderWidth = 0
        TEXT_UPDATE_INTERVAL_SECOND = 1 #to update the text each second
        self.textUpdateInterval = timeFunctions.TimeElapseChecker_Linux(TEXT_UPDATE_INTERVAL_SECOND)
        self.lastKnownTime = 0
        #TODO: if there's no audio notifier available, the audio/mute button shouldn't be shown at all
        self.layout = [                        
                        [simpleGUI.Text("Strained time: "), simpleGUI.Text(size = config.WidgetConstants.TEXT_SIZE, key = config.WidgetConstants.STRAINED_TIME_TEXT), simpleGUI.Text("Allowed strain: "), simpleGUI.Text(size = config.WidgetConstants.TEXT_SIZE, key = config.WidgetConstants.ALLOWED_STRAIN_TEXT)],
                        [simpleGUI.Button('', key=config.WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON, image_data=self.buttonStrings[config.WidgetConstants.PAUSE_ICON], button_color=(self.buttonHoverBackgroundColor, backgroundColorOfGUI), border_width=self.borderWidth, tooltip='Pause the timer or continue running it. Pausing is considered the equivalent of taking rest', metadata=False), 
                         simpleGUI.Button('', key=config.WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON, image_data=self.buttonStrings[config.WidgetConstants.AUDIO_ICON], button_color=(self.buttonHoverBackgroundColor, backgroundColorOfGUI), border_width=self.borderWidth,  tooltip='Mute or un-mute the audio notification', metadata=False),
                         simpleGUI.Button('', key=config.WidgetConstants.VIEW_TIMEFILE_BUTTON, image_data=self.buttonStrings[config.WidgetConstants.VIEW_FILE_ICON], button_color=(self.buttonHoverBackgroundColor, backgroundColorOfGUI), border_width=self.borderWidth,  tooltip='View the file that logs time information recorded by this program.', metadata=False)], 
                    ]
    
    def getLayout(self):
        return self.layout
    
    def __loadButtonImages(self):
        fileOps = fileAndFolderOperations.FileOperations()
        imagesToLoad = [config.WidgetConstants.PLAY_ICON, config.WidgetConstants.PAUSE_ICON, config.WidgetConstants.AUDIO_ICON, config.WidgetConstants.MUTE_ICON, config.WidgetConstants.VIEW_FILE_ICON]
        for image in imagesToLoad:
            self.buttonStrings[image] = fileOps.getFileAsBase64EncodedString(config.Names.ICON_PATH, image)

    def runEventLoop(self, event, values):#this gets invoked from the main GUI interface class
        durationElapsed, elapsedDuration, currentTime = self.textUpdateInterval.didDurationElapse()
        if durationElapsed:
            strainedDuration, allowedStrainDuration, formattedStrainedTime = self.timer.getStrainDetails()
            self.mainWindow[config.WidgetConstants.STRAINED_TIME_TEXT].update(formattedStrainedTime) #update the info shown about strained time
            self.mainWindow[config.WidgetConstants.ALLOWED_STRAIN_TEXT].update(allowedStrainDuration)
        if event == None and values == None:
            return        
        if event == config.WidgetConstants.PAUSE_RUN_TOGGLE_BUTTON:
            self.__togglePlayPause(event)
            self.timer.togglePauseStrainedTimeMeasurement()
        if event == config.WidgetConstants.MUTE_UNMUTE_TOGGLE_BUTTON:
            self.__toggleAudioMute(event)
            self.timer.toggleAllAudioNotifiers() 
        if event == config.WidgetConstants.VIEW_TIMEFILE_BUTTON:
            reversedTimeData = self.timer.getTimeFileData() 
            reversedTimeData.reverse() 
            simpleGUI.popup_scrolled(*reversedTimeData, title="iRest time data written to disk", font=("Arial", 10), size=(1024, 768), background_color="black", text_color="white", non_blocking=True)
    
    def __togglePlayPause(self, event):
        element = self.mainWindow[event]
        if element.metadata:#toggle the button image
            element.update(image_data=self.buttonStrings[config.WidgetConstants.PAUSE_ICON])                
        else:
            element.update(image_data=self.buttonStrings[config.WidgetConstants.PLAY_ICON])                
        element.metadata = not element.metadata

    def __toggleAudioMute(self, event):
        element = self.mainWindow[event]
        if element.metadata:#toggle the button image
            element.update(image_data=self.buttonStrings[config.WidgetConstants.AUDIO_ICON])                
        else:
            element.update(image_data=self.buttonStrings[config.WidgetConstants.MUTE_ICON])                
        element.metadata = not element.metadata

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
                            [simpleGUI.Text("Warmth:"), simpleGUI.Slider(size=config.WidgetConstants.SCT_SLIDER_SIZE, tick_interval=3000, range=(minVal, maxVal), default_value=defaultVal, expand_x=True, enable_events=True, orientation='horizontal', key=config.WidgetConstants.SCT_SLIDER, tooltip="Adjusts the 'wramth' colour of the screen")],
                        ]
        
    def getLayout(self):
        return self.layout
    
    def runEventLoop(self, event, values):    
        if self.warmthApp:
            if event == config.WidgetConstants.SCT_SLIDER:
                warmthValue = values[config.WidgetConstants.SCT_SLIDER]
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
        if backendRef:#if not None
            self.backends.append(backendRef)        
            self.backendGUIRefs.append(backendRef.getGUIRef())
        
    def createLayout(self):
        for guiRef in self.backendGUIRefs:#iterate all the supplied layouts and append them in the main interface
            receivedLayout = guiRef.getLayout()
            if receivedLayout:#the layout received can be [] if the backend does not need to implement a GUI
                self.layout.extend(receivedLayout) 
        #---create the window using all supplied layouts
        iconFile = self.__loadMainProgramIcon() 
        self.window = simpleGUI.Window(config.WidgetConstants.WINDOW_TITLE, icon = iconFile, layout = self.layout)        
        #---register the main window in all GUI layouts
        for guiRef in self.backendGUIRefs:
            guiRef.registerMainWindowReference(self.window)
        event, values = self.window.read(timeout = 0) #this dummy read has to be there to be able to call minimize. Either this or the window needs to have finalize=True. https://stackoverflow.com/questions/71580321/run-code-after-the-window-has-been-initialized
        self.window.minimize()
    
    def runEventLoop(self):#this function should get called repeatedly from an external while loop
        event, values = self.window.read(timeout = self.WINDOW_WAIT_TIMEOUT_MILLISECOND) 
        if event == simpleGUI.WIN_CLOSED or event == simpleGUI.Exit:#somehow, this line works only if placed above the check for event and values being None
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
        return fileOps.joinPathAndFilename(config.Names.ICON_PATH, config.WidgetConstants.MAIN_PROGRAM_ICON)
    
