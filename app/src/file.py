from src.crashreport import CrashReport
import src.variables as variables
import src.settings as settings
import src.ui as ui

import threading
import traceback
import win32con
import win32gui
import ImageUI
import time
import os


RED = "\033[91m"
GREEN = "\033[92m"
GRAY = "\033[90m"
NORMAL = "\033[0m"

SAVING = False
OPENING = False


def MovePathPopup(Title=""):
    try:
        def MovePathPopupThread():
            try:
                while True:
                    HWND = win32gui.FindWindow(None, Title)
                    if HWND != 0:
                        X, Y = variables.Window.get_position()
                        WIDTH, HEIGHT = variables.Window.get_size()
                        win32gui.MoveWindow(HWND, X, Y, WIDTH, HEIGHT, True)
                        win32gui.SetWindowPos(HWND, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        win32gui.SetWindowLong(HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(HWND, win32con.GWL_EXSTYLE))
                        break
                RECT = win32gui.GetClientRect(HWND)
                TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
                BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
                XOffset = X - TopLeft[0]
                YOffset = Y - TopLeft[1] + 32
                WidthOffset = WIDTH - (BottomRight[0] - TopLeft[0])
                HeightOffset = HEIGHT - (BottomRight[1] - TopLeft[1]) - 32
                while True:
                    Start = time.time()
                    X, Y = variables.Window.get_position()
                    WIDTH, HEIGHT = variables.Window.get_size()
                    if win32gui.FindWindow(None, Title) == 0:
                        break
                    RECT = win32gui.GetClientRect(HWND)
                    TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
                    BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
                    if X != TopLeft[0] or Y != TopLeft[1] or WIDTH != BottomRight[0] - TopLeft[0] or HEIGHT != BottomRight[1] - TopLeft[1]:
                        win32gui.MoveWindow(HWND, X + XOffset, Y + YOffset, WIDTH + WidthOffset, HEIGHT + HeightOffset, True)
                    TimeToSleep = 1/60 - (time.time() - Start)
                    if TimeToSleep > 0:
                        time.sleep(TimeToSleep)
            except:
                CrashReport("File - Error in function MovePathPopupThread.", str(traceback.format_exc()))
        if variables.OS != "nt":
            return
        import win32gui, win32con
        threading.Thread(target=MovePathPopupThread, daemon=True).start()
    except:
        CrashReport("File - Error in function MovePathPopup.", str(traceback.format_exc()))


def New():
    try:
        def NewThread():
            try:
                Save(Path=f"{variables.Path}cache/LastSession.txt")
                while SAVING or OPENING:
                    time.sleep(0.1)
                print(GREEN + "Creating new file..." + NORMAL)
                ui.Popup(Text="Creating new file...", Progress=-1)
                variables.FilePath = ""
                variables.CanvasPosition = variables.WindowWidth // 2, variables.WindowHeight // 2
                variables.CanvasZoom = 1
                variables.CanvasShowGrid = settings.Get("Draw", "ShowGrid", True)
                variables.CanvasLineGrid = settings.Get("Draw", "LineGrid", False)
                variables.SmoothLines = settings.Get("Draw", "SmoothLines", False)
                variables.UpscaleLines = settings.Get("Draw", "UpscaleLines", True)
                variables.AntiAliasedLines = settings.Get("Draw", "AntiAliasedLines", True)
                variables.SmoothInterpolation = settings.Get("Draw", "SmoothInterpolation", False)
                variables.CanvasContent = []
                variables.CanvasTemp = []
                variables.CanvasDeleteList = []
                print(GRAY + f"-> Show grid: {variables.CanvasShowGrid}" + NORMAL)
                print(GRAY + f"-> Line grid: {variables.CanvasLineGrid}" + NORMAL)
                print(GRAY + f"-> Smooth lines: {variables.SmoothLines}" + NORMAL)
                print(GRAY + f"-> Upscale lines: {variables.UpscaleLines}" + NORMAL)
                print(GRAY + f"-> Anti-aliased lines: {variables.AntiAliasedLines}" + NORMAL)
                print(GRAY + f"-> Smooth interpolation: {variables.SmoothInterpolation}" + NORMAL)
                print(GREEN + "Created new file successfully!\n" + NORMAL)
                variables.Page = "Canvas"
                ImageUI.SetSwitch(ID="FileShowGrid", State=variables.CanvasShowGrid)
                ImageUI.SetSwitch(ID="FileLineGrid", State=variables.CanvasLineGrid)
                ImageUI.SetSwitch(ID="FileSmoothLines", State=variables.SmoothLines)
                ImageUI.SetSwitch(ID="FileUpscaleLines", State=variables.UpscaleLines)
                ImageUI.SetSwitch(ID="FileAntiAliasedLines", State=variables.AntiAliasedLines)
                ImageUI.SetSwitch(ID="FileSmoothInterpolation", State=variables.SmoothInterpolation)
                ui.Popup(Text="Created new file successfully!", Progress=0)
            except:
                CrashReport("File - Error in function NewThread.", str(traceback.format_exc()))
                ui.Popup(Text="Error creating new file.", Progress=0)
        threading.Thread(target=NewThread, daemon=True).start()
    except:
        CrashReport("File - Error in function New.", str(traceback.format_exc()))


def Save(Path=""):
    try:
        def SaveThread(Path=""):
            global SAVING
            try:
                print(GREEN + "Saving file..." + NORMAL)
                if f"{variables.Path}cache" not in Path:
                    ui.Popup(Text="Saving file...", Progress=-1)
                if Path == "":
                    MovePathPopup(Title="Select a path to save to")
                    try:
                        variables.FilePath, _, _ = win32gui.GetSaveFileNameW(
                            InitialDir=settings.Get("File", "LastDirectory", os.path.dirname(os.path.dirname(variables.Path))),
                            Flags=win32con.OFN_OVERWRITEPROMPT | win32con.OFN_EXPLORER,
                            DefExt="txt",
                            Title="Select a path to save to",
                            Filter="PyTorch-Calculator Text Files\0*.txt\0"
                        )
                        Path = variables.FilePath
                    except win32gui.error:
                        print(RED + "File not saved!\n" + NORMAL)
                        if f"{variables.Path}cache" not in Path:
                            ui.Popup(Text="File not saved!", Progress=0)
                        SAVING = False
                        return
                if Path == "":
                    print(RED + "File not saved!\n" + NORMAL)
                    if f"{variables.Path}cache" not in Path:
                        ui.Popup(Text="File not saved!", Progress=0)
                    SAVING = False
                    return
                if Path.endswith(".txt") == False:
                    Path += ".txt"
                if os.path.exists(os.path.dirname(Path)) == False:
                    os.makedirs(os.path.dirname(Path))
                if f"{variables.Path}cache" not in Path:
                    settings.Set("File", "LastDirectory", os.path.dirname(Path))
                print(GRAY + f"-> {Path}" + NORMAL)
                with open(Path, "w") as File:
                    File.write(f"""
                        CanvasPosition#{variables.CanvasPosition}###
                        CanvasZoom#{variables.CanvasZoom}###
                        CanvasShowGrid#{variables.CanvasShowGrid}###
                        CanvasLineGrid#{variables.CanvasLineGrid}###
                        SmoothLines#{variables.SmoothLines}###
                        UpscaleLines#{variables.UpscaleLines}###
                        AntiAliasedLines#{variables.AntiAliasedLines}###
                        SmoothInterpolation#{variables.SmoothInterpolation}###
                        CanvasContent#{variables.CanvasContent}###
                        CanvasTemp#{variables.CanvasTemp}###
                        CanvasDeleteList#{variables.CanvasDeleteList}
                    """.replace(" ", "").replace("\n", ""))
                print(GREEN + "File saved successfully!\n" + NORMAL)
                if f"{variables.Path}cache" not in Path:
                    ui.Popup(Text="File saved successfully!", Progress=0)
                variables.Page = "Canvas"
            except:
                CrashReport("File - Error in function SaveThread.", str(traceback.format_exc()))
                if f"{variables.Path}cache" not in Path:
                    ui.Popup(Text="File not saved!", Progress=0)
            SAVING = False
        global SAVING
        SAVING = True
        threading.Thread(target=SaveThread, args=(Path,), daemon=True).start()
    except:
        CrashReport("File - Error in function Save.", str(traceback.format_exc()))


def Open(Path=""):
    try:
        def OpenThread(Path=""):
            global OPENING
            try:
                print(GREEN + "Opening file..." + NORMAL)
                if f"{variables.Path}cache" not in Path:
                    ui.Popup(Text="Opening file...", Progress=-1)
                if Path == "" or os.path.exists(Path) == False:
                    MovePathPopup(Title="Select a text file to open")
                    try:
                        variables.FilePath, _, _ = win32gui.GetOpenFileNameW(
                            InitialDir=settings.Get("File", "LastDirectory", os.path.dirname(os.path.dirname(variables.Path))),
                            Flags=win32con.OFN_OVERWRITEPROMPT | win32con.OFN_EXPLORER,
                            DefExt="txt",
                            Title="Select a text file to open",
                            Filter="PyTorch-Calculator Text Files\0*.txt\0"
                        )
                        Path = variables.FilePath
                    except win32gui.error:
                        print(RED + "File not opened!\n" + NORMAL)
                        if f"{variables.Path}cache" not in Path:
                            ui.Popup(Text="File not opened!", Progress=0)
                        OPENING = False
                        return
                if Path == "" or os.path.exists(Path) == False:
                    print(RED + "File not opened!\n" + NORMAL)
                    if f"{variables.Path}cache" not in Path:
                        ui.Popup(Text="File not opened!", Progress=0)
                    OPENING = False
                    return
                if f"{variables.Path}cache" not in Path:
                    settings.Set("File", "LastDirectory", os.path.dirname(Path))
                print(GRAY + f"-> {Path}" + NORMAL)
                with open(Path, "r") as File:
                    Content = str(File.read()).replace("\n", "").replace(" ", "")
                    for Item in Content.split("###"):
                        Key, Value = Item.split("#")
                        setattr(variables, Key, eval(Value))
                ImageUI.SetSwitch(ID="FileShowGrid", State=variables.CanvasShowGrid)
                ImageUI.SetSwitch(ID="FileLineGrid", State=variables.CanvasLineGrid)
                ImageUI.SetSwitch(ID="FileSmoothLines", State=variables.SmoothLines)
                ImageUI.SetSwitch(ID="FileUpscaleLines", State=variables.UpscaleLines)
                ImageUI.SetSwitch(ID="FileAntiAliasedLines", State=variables.AntiAliasedLines)
                ImageUI.SetSwitch(ID="FileSmoothInterpolation", State=variables.SmoothInterpolation)
                print(GREEN + "File opened successfully!\n" + NORMAL)
                if f"{variables.Path}cache" not in Path:
                    ui.Popup(Text="File opened successfully!", Progress=0)
                variables.Page = "Canvas"
            except:
                CrashReport("File - Error in function OpenThread.", str(traceback.format_exc()))
                if f"{variables.Path}cache" not in Path:
                    ui.Popup(Text="File not opened!", Progress=0)
            OPENING = False
        global OPENING
        OPENING = True
        threading.Thread(target=OpenThread, args=(Path,), daemon=True).start()
    except:
        CrashReport("File - Error in function Open.", str(traceback.format_exc()))