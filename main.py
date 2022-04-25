#!/usr/bin/env python

from timer import timers
from operatingSystemFunctions import operatingSystemDiversifier


if __name__ == '__main__':
    operatingSystemCheck = operatingSystemDiversifier.OperatingSystemChecker()
    operatingSystemAdapter = operatingSystemCheck.getOperatingSystemAdapterInstance()    
    timers = timers.Timer()
    timers.addThisNotifierToListOfNotifiers(operatingSystemAdapter.getAudioNotifier()) #TODO: take notifiers from the config file
    timers.registerOperatingSystemAdapter(operatingSystemAdapter)#If OS was not identified, the adapter will be None

    while True:
        timers.check()
    
    
