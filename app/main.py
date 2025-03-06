import os
import sys
sys.path.append(os.path.dirname(__file__))
os.system("cls" if os.name == "nt" else "clear")
print("\nPyTorch-Calculator\n------------------\n")

import src.variables as variables
import src.keyboard as keyboard
import src.settings as settings
import src.analyze as analyze
import src.console as console
import src.pytorch as pytorch
import src.updater as updater
import src.canvas as canvas
import src.mouse as mouse
import src.file as file
import src.ui as ui

import time
import sys

for Argument in sys.argv:
    if "--dev" in Argument.lower():
        variables.DevelopmentMode = True
    elif os.path.exists(Argument) and Argument.lower().endswith(".txt"):
        file.Open(Argument)

if os.path.exists(f"{variables.Path}cache") == False:
    os.makedirs(f"{variables.Path}cache")

if settings.Get("Console", "HideConsole", False):
    console.HideConsole()

pytorch.CheckCUDA()
ui.Initialize()
analyze.Initialize()
updater.CheckForUpdates()

mouse.Run()
keyboard.Run()

if variables.DevelopmentMode:
    import hashlib
    Scripts = []
    Scripts.append(("Main", f"{variables.Path}app/main.py"))
    for Object in os.listdir(f"{variables.Path}app/src"):
        Scripts.append((Object, f"{variables.Path}app/src/{Object}"))
    LastScripts = {}
    for i, (Script, Path) in enumerate(Scripts):
        try:
            Hash = hashlib.md5(open(Path, "rb").read()).hexdigest()
            LastScripts[i] = Hash
        except:
            pass

while variables.Break == False:
    Start = time.time()

    if variables.DevelopmentMode:
        for i, (Script, Path) in enumerate(Scripts):
            try:
                Hash = hashlib.md5(open(Path, "rb").read()).hexdigest()
                if Hash != LastScripts[i]:
                    ui.Restart()
                    LastScripts[i] = Hash
                    break
            except:
                pass

    canvas.Update()

    analyze.Update()

    ui.Update()

    TimeToSleep = 1/60 - (time.time() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)

if settings.Get("Console", "HideConsole", False):
    console.RestoreConsole()
    console.CloseConsole()