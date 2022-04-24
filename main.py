#!/usr/bin/env python

from timer import timers
from notifications import notifiers
from operatingSystemFunctions import operatingSystemDiversifier


if __name__ == '__main__':
    operatingSystemCheck = operatingSystemDiversifier.OperatingSystemChecker()
    audioNotification = notifiers.AudioNotifier()    
    timers = timers.Timer()
    timers.registerAudioNotifier(audioNotification)
    timers.registerOperatingSystemAdapter(operatingSystemCheck.getOperatingSystemAdapterInstance())#If OS was not identified, the adapter will be None

    while True:
        timers.check()
    
    
