import PySimpleGUI as simpleGUI

class WidgetConstants:
    TEXT_SIZE = (12, 1)
    STRAINED_TIME_TEXT = 'statusTextfield'
    ALLOWED_STRAIN_TEXT = 'allowedStrain'
    STRAINED_INFO_TEXT = 'strainedInfoTextfield'
    PAUSE_BUTTON = 'Pause'
    PLAY_BUTTON = 'Continue'
    MUTE_BUTTON = 'Mute'
    UNMUTE_BUTTON = 'Un-mute'
    WINDOW_TITLE = 'iRest'
    

class DefaultTimerLayout:#The layouts will be initialized in the timer classes and then be passed to the main interface
    def __init__(self, backendReference) -> None:
        self.timer = backendReference
        self.layout = [
                        [simpleGUI.Text("Strained time: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.STRAINED_TIME_TEXT)],
                        [simpleGUI.Text("Allowed strain: "), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.ALLOWED_STRAIN_TEXT)],
                        #[simpleGUI.Text(self.strainInfo), simpleGUI.Text(size = WidgetConstants.TEXT_SIZE, key = WidgetConstants.STRAINED_INFO_TEXT)],
                        [simpleGUI.Button(WidgetConstants.PAUSE_BUTTON), simpleGUI.Button(WidgetConstants.PLAY_BUTTON)]
                    ]
        
    def getLayout(self):
        return self.layout
    
    def runEventLoop(self, window, event, values):
        strainedDuration, allowedStrainDuration, formattedStrainedTime = self.timer.getStrainDetails()
        window[WidgetConstants.STRAINED_TIME_TEXT].update(formattedStrainedTime)
        window[WidgetConstants.ALLOWED_STRAIN_TEXT].update(allowedStrainDuration)
        # if event == WidgetConstants.PAUSE_BUTTON:
        #     self.window[WidgetConstants.STRAINED_TIME_TEXT].update('Paused program')        
        # if event == WidgetConstants.PLAY_BUTTON:
        #     self.window[WidgetConstants.STRAINED_TIME_TEXT].update('Program running') 
    
    
class MainInterface:
    def __init__(self):
        simpleGUI.theme('Dark Blue 13') 
        self.programRunning = True
        self.window = None #will be instantiated when layout is created
        self.backends = []
        self.backendGUIRefs = []
        self.layout = []
        
    def addThisBackend(self, backendReference):
        self.backends.append(backendReference)
        self.backendGUIRefs.append(backendReference.getGUIRef())
        
    def createLayout(self):
        for guiRef in self.backendGUIRefs:#iterate all the supplied layouts and append them in the main interface
            self.layout.extend(guiRef.getLayout()) 
        #---create the window using all supplied layouts
        self.window = simpleGUI.Window(WidgetConstants.WINDOW_TITLE, self.layout)
    
    def runEventLoop(self):#this function should get called repeatedly from an external while loop
        event, values = self.window.read()
        print(event, values)
        if event == simpleGUI.WIN_CLOSED or event == simpleGUI.Exit:
            self.closeWindow()
        for guiRef in self.backendGUIRefs:
            guiRef.runEventLoop(self.window, event, values)       
    
    def closeWindow(self):
        self.window.close()
        self.programRunning = False
        
    def notClosedGUI(self):
        return self.programRunning