from src.crashreport import CrashReport
import src.variables as variables
import src.settings as settings
import src.console as console
from bs4 import BeautifulSoup
import src.ui as ui
import subprocess
import threading
import traceback
import requests
import ImageUI
import GPUtil
import psutil
import torch
import time
import sys
import os

RED = "\033[91m"
GREEN = "\033[92m"
GRAY = "\033[90m"
YELLOW = "\033[93m"
NORMAL = "\033[0m"

try:
    from torchvision import transforms
    import torch
    TorchAvailable = True
except:
    TorchAvailable = False
    CrashReport("PyTorch - PyTorch import error.", str(traceback.format_exc()))

MODELS = {}

def Initialize(Owner="", Model="", Folder="", Threaded=True):
    Identifier = f"{Model}/{Folder}"
    MODELS[Identifier] = {}
    MODELS[Identifier]["Device"] = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MODELS[Identifier]["Path"] = f"{variables.Path}cache/{Identifier}"
    MODELS[Identifier]["Threaded"] = Threaded
    MODELS[Identifier]["ModelOwner"] = str(Owner)
    MODELS[Identifier]["UpdateThread"] = None
    MODELS[Identifier]["LoadThread"] = None
    return Identifier


def Popup(Text="", Progress=0):
    ui.Popup(Text=Text, Progress=Progress)


def InstallCUDA():
    try:
        def InstallCUDAThread():
            try:
                Command = ["cmd", "/c", f"{variables.Path}python/python.exe -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124 --progress-bar raw --force-reinstall"]
                Process = subprocess.Popen(Command, cwd=variables.Path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                with open(LockFilePath, "w") as File:
                    File.write(str(Process.pid))
                    File.close()
                while psutil.pid_exists(Process.pid):
                    time.sleep(0.1)
                    Output = Process.stdout.readline()
                    Output = str(Output.decode().strip()).replace("Progress ", "").split(" of ")
                    if len(Output) == 2:
                        TotalSize = Output[1]
                        DownloadedSize = Output[0]
                        try:
                            Popup(Text=f"Installing CUDA: {round((int(DownloadedSize) / int(TotalSize)) * 100)}%", Progress=(int(DownloadedSize) / int(TotalSize)) * 100)
                        except:
                            Popup(Text="Installing CUDA...", Progress=-1)
                    else:
                        Popup(Text="Installing CUDA...", Progress=-1)
                if os.path.exists(LockFilePath):
                    os.remove(LockFilePath)
                print(GREEN + "CUDA installation completed." + NORMAL)
                Popup(Text="CUDA installation completed.", Progress=0)
                ui.Restart()
            except:
                CrashReport("PyTorch - Error in function InstallCUDAThread.", str(traceback.format_exc()))
        print(GREEN + "Installing CUDA..." + NORMAL)
        Popup(Text="Installing CUDA...", Progress=-1)
        LockFilePath = f"{variables.Path}cache/CUDAInstall.txt"
        if os.path.exists(LockFilePath):
            with open(LockFilePath, "r") as File:
                PID = int(File.read().strip())
                File.close()
            if str(PID) in str(psutil.pids()):
                print(RED + "CUDA is already being installed." + NORMAL)
                Popup(Text="CUDA is already being installed.", Progress=0)
                return
        threading.Thread(target=InstallCUDAThread, daemon=True).start()
    except:
        CrashReport("PyTorch - Error in function InstallCUDA.", str(traceback.format_exc()))


def UninstallCUDA():
    try:
        def UninstallCUDAThread():
            try:
                Command = ["cmd", "/c", f"{variables.Path}python/python.exe -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --progress-bar raw --force-reinstall"]
                Process = subprocess.Popen(Command, cwd=variables.Path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                with open(LockFilePath, "w") as File:
                    File.write(str(Process.pid))
                    File.close()
                while psutil.pid_exists(Process.pid):
                    time.sleep(0.1)
                    Output = Process.stdout.readline()
                    Output = str(Output.decode().strip()).replace("Progress ", "").split(" of ")
                    if len(Output) == 2:
                        TotalSize = Output[1]
                        DownloadedSize = Output[0]
                        try:
                            Popup(Text=f"Uninstalling CUDA: {round((int(DownloadedSize) / int(TotalSize)) * 100)}%", Progress=(int(DownloadedSize) / int(TotalSize)) * 100)
                        except:
                            Popup(Text="Uninstalling CUDA...", Progress=-1)
                    else:
                        Popup(Text="Uninstalling CUDA...", Progress=-1)
                if os.path.exists(LockFilePath):
                    os.remove(LockFilePath)
                print(GREEN + "CUDA uninstallation completed." + NORMAL)
                Popup(Text="CUDA uninstallation completed.", Progress=0)
                ui.Restart()
            except:
                CrashReport("PyTorch - Error in function UninstallCUDAThread.", str(traceback.format_exc()))
        print(GREEN + "Uninstalling CUDA..." + NORMAL)
        Popup(Text="Uninstalling CUDA...", Progress=-1)
        LockFilePath = f"{variables.Path}cache/CUDAInstall.txt"
        if os.path.exists(LockFilePath):
            with open(LockFilePath, "r") as File:
                PID = int(File.read().strip())
                File.close()
            if str(PID) in str(psutil.pids()):
                print(RED + "CUDA is already being uninstalled." + NORMAL)
                Popup(Text="CUDA is already being uninstalled.", Progress=0)
                return
        threading.Thread(target=UninstallCUDAThread, daemon=True).start()
    except:
        CrashReport("PyTorch - Error in function UninstallCUDA.", str(traceback.format_exc()))


def CheckCUDA():
    try:
        variables.CUDAInstalled = "Loading..."
        variables.CUDAAvailable = "Loading..."
        variables.CUDACompatible = "Loading..."
        variables.CUDADetails = "Loading..."
        def CheckCUDAThread():
            try:
                Result = subprocess.run(f"{variables.Path}python/python.exe -m pip list", shell=True, capture_output=True, text=True)
                Modules = Result.stdout
                CUDAInstalled = True
                PyTorchModules = []
                for Module in Modules.splitlines():
                    if "torch " in Module:
                        PyTorchModules.append(Module)
                        if "cu" not in Module:
                            CUDAInstalled = False
                    elif "torchvision " in Module:
                        PyTorchModules.append(Module)
                        if "cu" not in Module:
                            CUDAInstalled = False
                    elif "torchaudio " in Module:
                        PyTorchModules.append(Module)
                        if "cu" not in Module:
                            CUDAInstalled = False
                GPUS = [str(GPU.name) for GPU in GPUtil.getGPUs()]
                variables.CUDAInstalled = CUDAInstalled
                variables.CUDAAvailable = torch.cuda.is_available()
                variables.CUDACompatible = ("nvidia" in str([GPU.lower() for GPU in GPUS]))
                variables.CUDADetails = "\n".join(PyTorchModules) + "\n" + "\n".join([str(GPU.name).upper() for GPU in GPUtil.getGPUs()] if len(GPUS) > 0 else ["No GPUs found."])
            except:
                CrashReport("PyTorch - Error in function CheckCUDAThread.", str(traceback.format_exc()))
        threading.Thread(target=CheckCUDAThread, daemon=True).start()
    except:
        CrashReport("PyTorch - Error in function CheckCUDA.", str(traceback.format_exc()))


def Loaded(Identifier="All"):
    if Identifier == "All":
        for Model in MODELS:
            if MODELS[Model]["Threaded"] == True:
                if MODELS[Model]["UpdateThread"] == None: return False
                if MODELS[Model]["UpdateThread"].is_alive(): return False
                if MODELS[Model]["LoadThread"] == None: return False
                if MODELS[Model]["LoadThread"].is_alive(): return False
    else:
        if MODELS[Identifier]["Threaded"] == True:
            if MODELS[Identifier]["UpdateThread"] == None: return False
            if MODELS[Identifier]["UpdateThread"].is_alive(): return False
            if MODELS[Identifier]["LoadThread"] == None: return False
            if MODELS[Identifier]["LoadThread"].is_alive(): return False
    return True


def Load(Identifier):
    try:
        def LoadFunction(Identifier):
            try:
                CheckForUpdates(Identifier)
                if "UpdateThread" in MODELS[Identifier]:
                    while MODELS[Identifier]["UpdateThread"].is_alive():
                        time.sleep(0.1)

                if GetName(Identifier) == None:
                    return

                Popup(Text="Loading the model...", Progress=0)
                print(GRAY + f"[{Identifier}] " + GREEN + "Loading the model..." + NORMAL)

                ModelFileBroken = False

                try:
                    MODELS[Identifier]["Metadata"] = {"data": []}
                    MODELS[Identifier]["Model"] = torch.jit.load(os.path.join(MODELS[Identifier]["Path"], GetName(Identifier)), _extra_files=MODELS[Identifier]["Metadata"], map_location=MODELS[Identifier]["Device"])
                    MODELS[Identifier]["Model"].eval()
                    MODELS[Identifier]["Metadata"] = eval(MODELS[Identifier]["Metadata"]["data"])
                    for Item in MODELS[Identifier]["Metadata"]:
                        Item = str(Item)
                        if "image_width" in Item:
                            MODELS[Identifier]["IMG_WIDTH"] = int(Item.split("#")[1])
                        if "image_height" in Item:
                            MODELS[Identifier]["IMG_HEIGHT"] = int(Item.split("#")[1])
                        if "image_channels" in Item:
                            MODELS[Identifier]["IMG_CHANNELS"] = str(Item.split("#")[1])
                        if "outputs" in Item:
                            MODELS[Identifier]["OUTPUTS"] = int(Item.split("#")[1])
                        if "epochs" in Item:
                            MODELS[Identifier]["EPOCHS"] = int(Item.split("#")[1])
                        if "batch" in Item:
                            MODELS[Identifier]["BATCH_SIZE"] = int(Item.split("#")[1])
                        if "class_list" in Item:
                            MODELS[Identifier]["CLASS_LIST"] = eval(Item.split("#")[1])
                        if "image_count" in Item:
                            MODELS[Identifier]["IMAGE_COUNT"] = int(Item.split("#")[1])
                        if "training_time" in Item:
                            MODELS[Identifier]["TRAINING_TIME"] = Item.split("#")[1]
                        if "training_date" in Item:
                            MODELS[Identifier]["TRAINING_DATE"] = Item.split("#")[1]
                except:
                    ModelFileBroken = True

                if ModelFileBroken == False:
                    Popup(Text="Successfully loaded the model!", Progress=100)
                    print(GRAY + f"[{Identifier}] " + GREEN + "Successfully loaded the model!" + NORMAL)
                    MODELS[Identifier]["ModelLoaded"] = True
                else:
                    Popup(Text="Failed to load the model because the model file is broken.", Progress=0)
                    print(GRAY + f"[{Identifier}] " + RED + "Failed to load the model because the model file is broken." + NORMAL)
                    MODELS[Identifier]["ModelLoaded"] = False
                    HandleBroken(Identifier)
            except:
                CrashReport("PyTorch - Loading Error.", str(traceback.format_exc()))
                Popup(Text="Failed to load the model!", Progress=0)
                print(GRAY + f"[{Identifier}] " + RED + "Failed to load the model!" + NORMAL)
                MODELS[Identifier]["ModelLoaded"] = False

        if TorchAvailable:
            if MODELS[Identifier]["Threaded"]:
                MODELS[Identifier]["LoadThread"] = threading.Thread(target=LoadFunction, args=(Identifier,), daemon=True)
                MODELS[Identifier]["LoadThread"].start()
            else:
                LoadFunction(Identifier)

    except:
        CrashReport("PyTorch - Error in function Load.", str(traceback.format_exc()))
        Popup(Text="Failed to load the model.", Progress=0)
        print(GRAY + f"[{Identifier}] " + RED + "Failed to load the model." + NORMAL)


def CheckForUpdates(Identifier):
    try:
        def CheckForUpdatesFunction(Identifier):
            try:

                if "--dev" in sys.argv:
                    if GetName(Identifier) != None:
                        print(GRAY + f"[{Identifier}] " + YELLOW + "Development mode enabled, skipping update check..." + NORMAL)
                        return
                    else:
                        print(GRAY + f"[{Identifier}] " + YELLOW + "Development mode enabled, downloading model because it doesn't exist..." + NORMAL)

                Popup(Text="Checking for model updates...", Progress=0)
                print(GRAY + f"[{Identifier}] " + GREEN + "Checking for model updates..." + NORMAL)

                if settings.Get("PyTorch", f"{Identifier}-LastUpdateCheck", 0) + 600 > time.time():
                    if settings.Get("PyTorch", f"{Identifier}-LatestModel", "unset") == GetName(Identifier):
                        print(GRAY + f"[{Identifier}] " + GREEN + "No model updates available!" + NORMAL)
                        return

                try:
                    HuggingFaceResponse = requests.get("https://huggingface.co/", timeout=3)
                    HuggingFaceResponse = HuggingFaceResponse.status_code
                except:
                    HuggingFaceResponse = None

                if HuggingFaceResponse == 200:
                    Url = f'https://huggingface.co/{MODELS[Identifier]["ModelOwner"]}/{Identifier.split("/")[0]}/tree/main/{"/".join(Identifier.split("/")[1:])}'
                    Response = requests.get(Url)
                    Soup = BeautifulSoup(Response.content, 'html.parser')

                    LatestModel = None
                    for Link in Soup.find_all("a", href=True):
                        HREF = Link["href"]
                        if HREF.startswith(f'/{MODELS[Identifier]["ModelOwner"]}/{Identifier.split("/")[0]}/blob/main/{"/".join(Identifier.split("/")[1:])}'):
                            LatestModel = HREF.split("/")[-1]
                            settings.Set("PyTorch", f"{Identifier}-LatestModel", LatestModel)
                            break
                    if LatestModel == None:
                        LatestModel = settings.Get("PyTorch", f"{Identifier}-LatestModel", "unset")

                    CurrentModel = GetName(Identifier)

                    if str(LatestModel) != str(CurrentModel):
                        Popup(Text="Updating the model...", Progress=0)
                        print(GRAY + f"[{Identifier}] " + GREEN + "Updating the model..." + NORMAL)
                        Delete(Identifier)
                        StartTime = time.time()
                        Response = requests.get(f'https://huggingface.co/{MODELS[Identifier]["ModelOwner"]}/{Identifier.split("/")[0]}/resolve/main/{"/".join(Identifier.split("/")[1:])}/{LatestModel}?download=true', stream=True, timeout=15)
                        with open(os.path.join(MODELS[Identifier]["Path"], f"{LatestModel}"), "wb") as ModelFile:
                            TotalSize = int(Response.headers.get('content-length', 1))
                            DownloadedSize = 0
                            ChunkSize = 1024
                            for Data in Response.iter_content(chunk_size=ChunkSize):
                                DownloadedSize += len(Data)
                                ModelFile.write(Data)
                                Progress = (DownloadedSize / TotalSize) * 100
                                ETA = time.strftime('%H:%M:%S' if (time.time() - StartTime) / Progress * (100 - Progress) >= 3600 else '%M:%S', time.gmtime((time.time() - StartTime) / Progress * (100 - Progress)))
                                Popup(Text=f"Downloading the model: {round(Progress)}% - ETA: {ETA}", Progress=Progress)
                        Popup(Text="Successfully updated the model!", Progress=100)
                        print(GRAY + f"[{Identifier}] " + GREEN + "Successfully updated the model!" + NORMAL)
                    else:
                        Popup(Text="No model updates available!", Progress=100)
                        print(GRAY + f"[{Identifier}] " + GREEN + "No model updates available!" + NORMAL)
                    settings.Set("PyTorch", f"{Identifier}-LastUpdateCheck", time.time())

                else:

                    console.RestoreConsole()
                    Popup(Text="Connection to 'https://huggingface.co' is not available. Unable to check for updates.", Progress=0)
                    print(GRAY + f"[{Identifier}] " + RED + "Connection to 'https://huggingface.co' is not available. Unable to check for updates." + NORMAL)

            except:
                CrashReport("PyTorch - Error in function CheckForUpdatesFunction.", str(traceback.format_exc()))
                Popup(Text="Failed to check for model updates or update the model.", Progress=0)
                print(GRAY + f"[{Identifier}] " + RED + "Failed to check for model updates or update the model." + NORMAL)

        if MODELS[Identifier]["Threaded"]:
            MODELS[Identifier]["UpdateThread"] = threading.Thread(target=CheckForUpdatesFunction, args=(Identifier,), daemon=True)
            MODELS[Identifier]["UpdateThread"].start()
        else:
            CheckForUpdatesFunction(Identifier)

    except:
        CrashReport("PyTorch - Error in function CheckForUpdates.", str(traceback.format_exc()))
        Popup(Text="Failed to check for model updates or update the model.", Progress=0)
        print(GRAY + f"[{Identifier}] " + RED + "Failed to check for model updates or update the model." + NORMAL)


def FolderExists(Identifier):
    try:
        if os.path.exists(MODELS[Identifier]["Path"]) == False:
            os.makedirs(MODELS[Identifier]["Path"])
    except:
        CrashReport("PyTorch - Error in function FolderExists.", str(traceback.format_exc()))


def GetName(Identifier):
    try:
        FolderExists(Identifier)
        for File in os.listdir(MODELS[Identifier]["Path"]):
            if File.endswith(".pt"):
                return File
        return None
    except:
        CrashReport("PyTorch - Error in function GetName.", str(traceback.format_exc()))
        return None


def Delete(Identifier):
    try:
        if "--dev" in sys.argv and os.listdir(MODELS[Identifier]["Path"]) != []:
            print(GRAY + f"[{Identifier}] " + YELLOW + "Development mode enabled, skipping model deletion..." + NORMAL)
            return
        FolderExists(Identifier)
        for File in os.listdir(MODELS[Identifier]["Path"]):
            if File.endswith(".pt"):
                os.remove(os.path.join(MODELS[Identifier]["Path"], File))
    except PermissionError:
        global TorchAvailable
        TorchAvailable = False
        print(GRAY + f"[{Identifier}] " + RED + "PyTorch - PermissionError in function Delete:\n" + NORMAL + str(traceback.format_exc()))
        console.RestoreConsole()
    except:
        CrashReport("PyTorch - Error in function Delete.", str(traceback.format_exc()))


def HandleBroken(Identifier):
    try:
        if "--dev" in sys.argv:
            print(GRAY + f"[{Identifier}] " + RED + "Can't handle broken models in development mode, all pytorch loader actions paused..." + NORMAL)
            while True: time.sleep(1)
        Delete(Identifier)
        CheckForUpdates(Identifier)
        if "UpdateThread" in MODELS[Identifier]:
            while MODELS[Identifier]["UpdateThread"].is_alive():
                time.sleep(0.1)
        time.sleep(0.5)
        if TorchAvailable == True:
            Load(Identifier)
    except:
        CrashReport("PyTorch - Error in function HandleBroken.", str(traceback.format_exc()))