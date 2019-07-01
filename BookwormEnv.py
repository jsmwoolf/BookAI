import subprocess
import sys
import time
if sys.platform == "darwin":
    from AppKit import NSWorkspace
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGWindowListOptionIncludingWindow,
        kCGNullWindowID
    )
import numpy as np
import cv2
import pyautogui

class BookwormEnv():
    def __init__(self):
        self.osType = sys.platform
        self.windowNumber = None

    def _launchProgram(self):
        if self.osType == "darwin":
            retcode = subprocess.call(['open', '-a', '/Applications/Bookworm.app'])
            print(retcode)
        if retcode != 0:
            raise Exception("Could not find Bookworm!")

    def _getWindow(self):
        return CGWindowListCopyWindowInfo(
            kCGWindowListOptionIncludingWindow, 
            self.windowNumber
        )[0]

    def getCoordinates(self):
        coord = self._getWindow()['kCGWindowBounds']
        return (
            coord["X"], 
            coord["Y"], 
            coord["X"] + coord["Width"], 
            coord["Y"] + coord["Height"]
        )

    def _findWindow(self, pid):
        if self.windowNumber != None:
            return 
        print('Finding window number...')
        window = None
        while True:
            options = kCGWindowListOptionOnScreenOnly
            windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            pidList = [app['kCGWindowOwnerPID'] for app in windowList]
            if pid in pidList:
                window = windowList[pidList.index(pid)]
                break
        self.windowNumber = window['kCGWindowNumber']
    
    def _getPid(self):
        active_app_name = None
        app_pid = None
        print('Getting pid...')
        # Wait until application is frontmost
        while active_app_name != "Bookworm": 
            apps = NSWorkspace.sharedWorkspace().runningApplications()
            for app in apps:
                active_app_name = app.localizedName()
                app_pid = app.processIdentifier()
        return app_pid

    def _translateCoordinates(self, x, y):
        coords = self.getCoordinates()
        return (coords[0] + x, coords[1] + y)

    def moveMouse(self, x, y):
        coords = self._translateCoordinates(x, y)
        pyautogui.moveTo(coords[0], coords[1])

    def getWindowShot(self, region=None):
        if region == None:
            region = self.getCoordinates()
        coord = (region[:])
        print(coord)
        img = pyautogui.screenshot(region=region)
        img = np.array(img)
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    def getProgram(self):
        if sys.platform == "darwin":
            if self.windowNumber != None:
                return 
            self._launchProgram()
            pid = self._getPid()
            self._findWindow(pid)
            geometry = self.getCoordinates()
            print(geometry)

    def _checkContinueBar(self):
        x, y = self._translateCoordinates(357, 171)
        img = self.getWindowShot(region=(x, y, 110, 22))
        filtered = cv2.inRange(img, np.array([0, 200, 200]), np.array([0, 255, 255]))
        _, counts = np.unique(filtered, return_counts=True)
        if len(counts) == 2:
            self.moveMouse(507, 337)
            pyautogui.click()


    def selectClassicMode(self):
        if self.windowNumber == None:
            self.handleLoadingScreen()
        self.moveMouse(504, 118)
        pyautogui.click()
        self._checkContinueBar()

    
    def handleLoadingScreen(self):
        self.getProgram()
        while True:
            img = self.getWindowShot()
            print(img.shape)
            filtered = cv2.inRange(img, np.array([0, 240, 240]), np.array([0, 255, 255]))
            _, counts = np.unique(filtered, return_counts=True)
            if len(counts) == 2 and counts[1] >= 947:
                self.moveMouse(335, 480)
                pyautogui.click()
                break




