import time
import logging
#from plyer.utils import platform #this is needed only for icon display
from plyer import notification
from abc import ABC, abstractmethod
from configuration import configHandler

class GraphicalNotifier(ABC):#Abstract parent class
    category = configHandler.NotifierConstants.GRAPHICAL_NOTIFIER
    #Note: Abstract methods have to be implemented by child classes because they would be invoked by other classes
    @abstractmethod
    def __init__(self):
        #self.id = "someUniqueNotifierName" #has to be implemented in the child class
        pass

    @abstractmethod
    def execute(self):
        """ Displays a notification to remind the user to take rest. Function does not return anything """
        pass

    def toggleNotifierActiveState(self):
        """ Toggles the isActive boolean """
        pass
    
    # @abstractmethod
    # def notifyUserThatRestPeriodIsOver(self):
    #     """ Displays a notification to inform the user that the resting period completed. Function does not return anything """
    #     pass

#Note: This is a crossplatform notifier (but does not work on Raspberry Pi due to some dbus error. For Raspberry Pi, use the notifier class below).
class PlyerGraphicalNotifier(GraphicalNotifier):
    def __init__(self):
        self.id = "Plyer Notifier"
        #self.SECONDS_TO_DISPLAY_MESSAGE = 10
        self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION = 60 #After the first audio notification, no more notifications would happen during a cooldown period, even if execute() is called repeatedly
        self.userNotified = False
        self.notifiedTime = None
        self.isActive = True

    def execute(self):#This function may get called multiple times, so it has to take care of not annoying the User with too many notifications. So a cooldown time was used to allow for some time until the next notification
        #Note: Notification cooling time was used within the class itself (instead of externally) since other notifiers may do notification at their own frequencies
        if self.userNotified:            
            elapsedTime = time.monotonic() - self.notifiedTime
            logging.debug(f"Plyer notification cooldown elapsed time: {elapsedTime}. Cooldown seconds: {self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION}")
            if elapsedTime >= self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION:#So actual time until the next notification will be COOLDOWN_SECONDS + number of seconds until execute() is invoked again
                self.userNotified = False            
        else:#notify User
            logging.debug("Audio notifier sending notification")
            #Note: notify command documentation: https://plyer.readthedocs.io/en/latest/index.html?highlight=notify#plyer.facades.Notification.notify and https://stackoverflow.com/a/42085439/453673       
            notification.notify(title = 'iRest reminder', message = "Please take rest now. You've strained your eyes.", app_name = 'iRest')
            self.notifiedTime = time.monotonic()
            self.userNotified = True

    def toggleNotifierActiveState(self):
        self.isActive = not self.isActive
        return self.isActive   
        
class WfPanelRaspberryPiNotifier(GraphicalNotifier):
    #Note: Could alternatively install dunst and use the dunstify command as this give more control
    def __init__(self):
        self.id = "wfpanel Notifier"
        #self.SECONDS_TO_DISPLAY_MESSAGE = 10
        self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION = 60 #After the first audio notification, no more notifications would happen during a cooldown period, even if execute() is called repeatedly
        self.userNotified = False
        self.notifiedTime = None
        self.isActive = True
        self.notifierProgram = "wfpanelctl"
        self.notificationNormal = "notify"
        self.notificationCritical = "critical"
        self.fullCommand = [self.notifierProgram, self.notificationNormal] #can add more parameters using comma
        self.takeRestMessage = "Please take rest now. You've strained your eyes."

    def execute(self):#This function may get called multiple times, so it has to take care of not annoying the User with too many notifications. So a cooldown time was used to allow for some time until the next notification
        #Note: Notification cooling time was used within the class itself (instead of externally) since other notifiers may do notification at their own frequencies
        if self.userNotified:            
            elapsedTime = time.monotonic() - self.notifiedTime
            logging.debug(f"Notification cooldown elapsed time: {elapsedTime}. Cooldown seconds: {self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION}")
            if elapsedTime >= self.SECONDS_TO_WAIT_UNTIL_REPEAT_NOTIFICATION:#So actual time until the next notification will be COOLDOWN_SECONDS + number of seconds until execute() is invoked again
                self.userNotified = False            
        else:#notify User
            logging.debug("Audio notifier sending notification")
            graphicCommand = self.fullCommand[:] #shallow copy by value
            graphicCommand.append(self.takeRestMessage)
            subprocess.run(graphicCommand)
            self.notifiedTime = time.monotonic()
            self.userNotified = True

    def toggleNotifierActiveState(self):
        self.isActive = not self.isActive
        return self.isActive           
