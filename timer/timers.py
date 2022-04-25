import time

class Timer:#Checks for how much time elapsed and notifies the User
    def __init__(self):
        self.workInterval = 60 * 20 #how long to work (in seconds)
        self.restRatio = 20 / 5 #Five minutes of rest for every 20 minutes of work
        self.sleepDuration = 10 #how long to sleep before checking system state (in seconds)
        self.workedTime = 0
        self.lastCheckedTime = time.monotonic()
        self.notifiers = {} #references to various objects that can be used to notify the user
        self.operatingSystemAdapter = None
        
    def addThisNotifierToListOfNotifiers(self, notifier):
        if notifier.id not in self.notifiers:#is notifier not already registered here
            print("Registering notifier: ", notifier.id)
            self.notifiers[notifier.id] = notifier
        else:
            print(notifier.id, 'is already registered.')

    def unregisterAudioNotifier(self, notifier):
        if notifier.id in self.notifiers:
            print("Deregistering notifier: ", notifier.id)
            del self.notifiers[notifier.id]
        else:
            print("No such notifier registered: ", notifier)

    def check(self):
        time.sleep(self.sleepDuration)
        if self.operatingSystemAdapter != None:#because the program should work on any OS
            if self.operatingSystemAdapter.isScreenLocked():   
                if self.workedTime > 0:
                    self.workedTime = abs(self.workedTime - (self.sleepDuration / self.restRatio))                    
                print("Screen locked. Worked time = ", self.workedTime)
                return
        elapsedTime = time.monotonic() - self.lastCheckedTime
        self.workedTime = self.workedTime + self.sleepDuration
        print('Time elapsed: ', elapsedTime, 's. Worked time: ', self.workedTime)
        if self.workedTime >= self.workInterval:
            self.lastCheckedTime = time.monotonic()
            for notifierID, notifierRef in self.notifiers.items(): #If operating system was not recognized, the operating system adapter will be None, and no notifier will be registered
                notifierRef.takeRestNotification()
                
    def registerOperatingSystemAdapter(self, operatingSystemAdapter):
        self.operatingSystemAdapter = operatingSystemAdapter
        