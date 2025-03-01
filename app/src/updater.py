from src.crashreport import CrashReport
import src.variables as variables
import src.settings as settings
import src.ui as ui

import subprocess
import traceback
import requests
import time

def CheckForUpdates():
    try:
        if variables.DEVMODE:
            variables.POPUP = ["Ignoring update check because of development mode.", 0, 0.65]
            return
        if settings.Get("Updater", "LastRemoteCheck", 0) + 600 < time.time():
            try:
                RemoteVersion = requests.get("https://raw.githubusercontent.com/OleFranz/PyTorch-Calculator/main/config/version.txt").text.strip()
                Changelog = requests.get("https://raw.githubusercontent.com/OleFranz/PyTorch-Calculator/main/config/changelog.txt").text.strip()
            except:
                RemoteVersion = "404: Not Found"
                Changelog = "404: Not Found"
            if RemoteVersion != "404: Not Found" and Changelog != "404: Not Found":
                settings.Set("Updater", "LastRemoteCheck", time.time())
                settings.Set("Updater", "RemoteVersion", RemoteVersion)
                settings.Set("Updater", "Changelog", Changelog)
        else:
            RemoteVersion = settings.Get("Updater", "RemoteVersion")
            Changelog = settings.Get("Updater", "Changelog")
        variables.REMOTE_VERSION = RemoteVersion
        variables.CHANGELOG = Changelog
        if RemoteVersion != variables.VERSION:
            variables.PAGE = "Update"
            ui.SetTitleBarHeight(0)
        else:
            variables.POPUP = ["No updates available.", 0, 0.5]
    except:
        CrashReport("Updater - Error in function CheckForUpdates.", str(traceback.format_exc()))

def Update():
    try:
        if variables.DEVMODE:
            variables.POPUP = ["Ignoring update request because of development mode.", 0, 0.65]
            ui.SetTitleBarHeight(50)
            variables.PAGE = "Menu"
            return
        ui.Close()
        subprocess.Popen(f"{variables.PATH}Update.bat", cwd=variables.PATH, creationflags=subprocess.CREATE_NEW_CONSOLE)
    except:
        CrashReport("Updater - Error in function Update.", str(traceback.format_exc()))