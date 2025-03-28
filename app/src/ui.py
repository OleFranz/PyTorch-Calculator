import src.variables as variables
import src.settings as settings
import src.console as console
import src.pytorch as pytorch
import src.updater as updater
import src.canvas as canvas
import src.mouse as mouse
import src.file as file

import SimpleWindow
import numpy as np
import subprocess
import ImageUI
import cv2


AvailableLanguages = list(ImageUI.Translations.GetAvailableLanguages().keys())
HideConsoleSwitch = settings.Get("Console", "HideConsole", False)
ShowGrid = settings.Get("Draw", "ShowGrid", True)
LineGrid = settings.Get("Draw", "LineGrid", False)
SmoothLines = settings.Get("Draw", "SmoothLines", False)
UpscaleLines = settings.Get("Draw", "UpscaleLines", True)
AntiAliasedLines = settings.Get("Draw", "AntiAliasedLines", True)
SmoothInterpolation = settings.Get("Draw", "SmoothInterpolation", False)
ShowContextMenu = False


def Initialize():
    WindowWidth = settings.Get("UI", "Width", 960)
    WindowHeight = settings.Get("UI", "Height", 540)
    WindowX = settings.Get("UI", "X", 100)
    WindowY = settings.Get("UI", "Y", 100)

    if WindowWidth < 50 or WindowHeight < 50:
        settings.Set("UI", "Width", 960)
        settings.Set("UI", "Height", 540)
        WindowWidth = 960
        WindowHeight = 540

    variables.CanvasPosition = round(WindowWidth / 2), round(WindowHeight / 2)

    variables.Background = np.zeros((WindowHeight, WindowWidth, 3), np.uint8)
    variables.Background[:] = (28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)
    cv2.rectangle(variables.Background, (0, 0), (WindowWidth - 1, 49), (47, 47, 47) if variables.Theme == "Dark" else (231, 231, 231), -1)

    variables.Canvas = np.zeros((WindowHeight - 50, WindowWidth, 3), np.uint8)
    variables.Canvas[:] = (28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)

    SimpleWindow.Initialize(Name=variables.Name,
                            Size=(WindowWidth, WindowHeight),
                            Position=(WindowX, WindowY),
                            TitleBarColor=(47, 47, 47) if variables.Theme == "Dark" else (231, 231, 231),
                            Resizable=False,
                            TopMost=False,
                            Undestroyable=False,
                            Icon=f"{variables.Path}app/assets/{'icon_dark' if variables.Theme == 'Dark' else 'icon_light'}.ico")

    SimpleWindow.Show(variables.Name, variables.Background)

    ImageUI.Settings.CachePath = f"{variables.Path}cache"

    ImageUI.SetTranslator(SourceLanguage="English", DestinationLanguage=variables.Language)
    ImageUI.SetTheme(variables.Theme)
    Update()


def SetTheme(Theme):
    settings.Set("UI", "Theme", Theme)
    variables.Theme = Theme
    variables.Background = np.zeros((variables.WindowHeight, variables.WindowWidth, 3), np.uint8)
    variables.Background[:] = (28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)
    cv2.rectangle(variables.Background, (0, 0), (variables.WindowWidth - 1, 49), (47, 47, 47) if variables.Theme == "Dark" else (231, 231, 231), -1)
    variables.Canvas = np.zeros((variables.WindowHeight - 50, variables.WindowWidth, 3), np.uint8)
    variables.Canvas[:] = (28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)
    variables.DrawColor = (255, 255, 255) if Theme == "Dark" else (0, 0, 0)
    ImageUI.SetTheme(Theme)
    SimpleWindow.SetTitleBarColor(variables.Name, (47, 47, 47) if variables.Theme == "Dark" else (231, 231, 231))
    SimpleWindow.SetIcon(variables.Name, f"{variables.Path}app/assets/{'icon_dark' if variables.Theme == 'Dark' else 'icon_light'}.ico")


def Popup(Text, Progress = 0):
    Right = variables.WindowWidth - 1
    Bottom = variables.WindowHeight - 1
    ImageUI.Popup(Text,
                  StartX1=Right * 0.3,
                  StartY1=Bottom,
                  StartX2=Right * 0.7,
                  StartY2=Bottom + 20,
                  EndX1=Right * 0.2,
                  EndY1=Bottom - 50,
                  EndX2=Right * 0.8,
                  EndY2=Bottom - 10,
                  Progress=Progress,
                  ID="MainPopup")


def Resize(WindowX, WindowY, WindowWidth, WindowHeight):
    variables.WindowX = WindowX
    variables.WindowY = WindowY
    variables.WindowWidth = WindowWidth
    variables.WindowHeight = WindowHeight
    variables.Background = np.zeros((WindowHeight, WindowWidth, 3), np.uint8)
    variables.Background[:] = (28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)
    cv2.rectangle(variables.Background, (0, 0), (WindowWidth - 1, 49), (47, 47, 47) if variables.Theme == "Dark" else (231, 231, 231), -1)
    variables.Canvas = np.zeros((WindowHeight - 50, WindowWidth, 3), np.uint8)
    variables.Canvas[:] = (28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)
    if variables.DevelopmentMode == True:
        SimpleWindow.SetPosition("PyTorch-Calculator (Dev Mode)", (variables.WindowX + variables.WindowWidth + 5, variables.WindowY + 430 + 5))
    SimpleWindow.SetPosition("PyTorch-Calculator Detection", (variables.WindowX + variables.WindowWidth + 5, variables.WindowY))


def Restart():
    file.Save(Path=f"{variables.Path}cache/LastSession.txt")
    if variables.DevelopmentMode == True:
        subprocess.Popen(f"{variables.Path}python/python.exe {variables.Path}app/main.py --dev {variables.Path}cache/LastSession.txt", cwd=variables.Path)
    else:
        subprocess.Popen(f"{variables.Path}Start.bat {variables.Path}cache/LastSession.txt", cwd=variables.Path, creationflags=subprocess.CREATE_NEW_CONSOLE)
    Close(SaveCanvas=False)


def Close(SaveCanvas=True):
    if SaveCanvas:
        file.Save(Path=f"{variables.Path}cache/LastSession.txt")
    ImageUI.Exit()
    settings.Set("UI", "X", variables.WindowX)
    settings.Set("UI", "Y", variables.WindowY)
    settings.Set("UI", "Width", variables.WindowWidth)
    settings.Set("UI", "Height", variables.WindowHeight)
    console.RestoreConsole()
    console.CloseConsole()
    variables.Break = True


def Update():
    if SimpleWindow.GetMinimized(variables.Name):
        SimpleWindow.Show(variables.Name, variables.Frame)
        return

    if SimpleWindow.GetOpen(variables.Name) != True:
        Close()
        return

    WindowX, WindowY = SimpleWindow.GetPosition(variables.Name)
    WindowWidth, WindowHeight = SimpleWindow.GetSize(variables.Name)
    if (WindowX, WindowY, WindowWidth, WindowHeight) != (variables.WindowX, variables.WindowY, variables.WindowWidth, variables.WindowHeight):
        Resize(WindowX, WindowY, WindowWidth, WindowHeight)

    Left = 0
    Top = 0
    Right = WindowWidth - 1
    Bottom = WindowHeight - 1


    global ShowContextMenu
    if ImageUI.States.RightClicked:
        ShowContextMenu = True
    if ImageUI.States.LeftClicked:
        ShowContextMenu = False
    if variables.Page == "Canvas":
        ShowContextMenu = False

    if ShowContextMenu:
        ImageUI.Button("Restart",
                       X1=ImageUI.States.RightClickPosition[0],
                       Y1=ImageUI.States.RightClickPosition[1],
                       X2=ImageUI.States.RightClickPosition[0] + 200,
                       Y2=ImageUI.States.RightClickPosition[1] + 30,
                       ID="ContextMenuRestart",
                       Layer=1,
                       OnPress=lambda: Restart())

        ImageUI.Button("Close",
                       X1=ImageUI.States.RightClickPosition[0],
                       Y1=ImageUI.States.RightClickPosition[1] + 35,
                       X2=ImageUI.States.RightClickPosition[0] + 200,
                       Y2=ImageUI.States.RightClickPosition[1] + 65,
                       ID="ContextMenuClose",
                       Layer=1,
                       OnPress=lambda: Close())

        ImageUI.Button("Search for updates",
                       X1=ImageUI.States.RightClickPosition[0],
                       Y1=ImageUI.States.RightClickPosition[1] + 70,
                       X2=ImageUI.States.RightClickPosition[0] + 200,
                       Y2=ImageUI.States.RightClickPosition[1] + 100,
                       ID="ContextMenuUpdate",
                       Layer=1,
                       OnPress=lambda: updater.CheckForUpdates())

    Tabs = ["Canvas", "File", "Settings"]
    for i, Tab in enumerate(Tabs):
        ImageUI.Button(Text=Tab,
                       X1=Left + i / len(Tabs) * Right + 5,
                       Y1=Top + 5,
                       X2=Left + (i + 1)  / len(Tabs) * Right - 5,
                       Y2=Top + 44,
                       ID=f"{Tab}TabButton",
                       OnPress=lambda Tab = Tab: {setattr(variables, "Page", Tab), settings.Set("UI", "Page", Tab)},
                       Color=((28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)) if Tab == variables.Page else ((47, 47, 47) if variables.Theme == "Dark" else (231, 231, 231)),
                       HoverColor=((28, 28, 28) if variables.Theme == "Dark" else (250, 250, 250)) if Tab == variables.Page else ((41, 41, 41) if variables.Theme == "Dark" else (244, 244, 244)))

    if variables.Page == "Update":
        ImageUI.Label(Text=f"Update Available:\n{variables.Version} -> {variables.RemoteVersion}",
                      X1=Left,
                      Y1=Top + 50,
                      X2=Right,
                      Y2=Top + 100,
                      ID="UpdateAvailable")

        ImageUI.Label(Text=f"Changelog:\n\n{variables.Changelog}",
                      X1=Left,
                      Y1=Top + 100,
                      X2=Right,
                      Y2=Bottom - 50,
                      ID="Changelog")

        ImageUI.Button(Text="Update",
                       X1=Left + 10,
                       Y1=Bottom - 50,
                       X2=Right / 2 - 5,
                       Y2=Bottom - 10,
                       ID="UpdateButton",
                       OnPress=lambda: updater.Update())

        ImageUI.Button(Text="Don't Update",
                       X1=Right / 2 + 5,
                       Y1=Bottom - 50,
                       X2=Right - 10,
                       Y2=Bottom - 10,
                       ID="Don'tUpdateButton",
                       OnPress=lambda: setattr(variables, "Page", "Canvas"))

    if variables.Page == "CUDA":
        if variables.CUDAInstalled != "Loading..." and variables.CUDAAvailable != "Loading..." and variables.CUDACompatible != "Loading..." and variables.CUDADetails != "Loading...":
            if variables.CUDAInstalled == False and variables.CUDAAvailable == False and variables.CUDACompatible == False:
                Message = "CUDA is not installed, not available and not compatible."
            elif variables.CUDAInstalled == True and variables.CUDAAvailable == False and variables.CUDACompatible == False:
                Message = "CUDA is installed but not available and not compatible."
            elif variables.CUDAInstalled == True and variables.CUDAAvailable == False and variables.CUDACompatible == True:
                Message = "CUDA is installed but not available, probably\nbecause your NVIDIA GPU is not compatible."
            elif variables.CUDAInstalled == False and variables.CUDAAvailable == False and variables.CUDACompatible == True:
                Message = "CUDA is not installed and not available, but it is compatible."
            elif variables.CUDAInstalled == False and variables.CUDAAvailable == True and variables.CUDACompatible == True:
                Message = "CUDA is not installed but available and compatible,\nprobably because Python is using a CUDA installation\noutside of the app environment."
            elif variables.CUDAInstalled == True and variables.CUDAAvailable == True and variables.CUDACompatible == True:
                Message = "CUDA is installed, available and compatible."
            else:
                Message = f"INSTALLED: {variables.CUDAInstalled} AVAILABLE: {variables.CUDAAvailable} COMPATIBLE: {variables.CUDACompatible}"
            ImageUI.Label(Text="When CUDA is installed and available, the app will run AI models\non your NVIDIA GPU which will result in a significant speed increase.",
                          X1=Left + 10,
                          Y1=Top + 60,
                          X2=Right - 10,
                          Y2=Top + 110,
                          ID="CUDATitle")

            ImageUI.Label(Text=f"{Message}",
                          X1=Left + 10,
                          Y1=Top + 110,
                          X2=Right - 10,
                          Y2=Top + 160,
                          ID="CUDAMessage")

            ImageUI.Label(Text=f"Details:\n{variables.CUDADetails}",
                          X1=Left + 10,
                          Y1=Top + 160,
                          X2=Right - 10,
                          Y2=Top + 280,
                          ID="CUDADetails")

            ImageUI.Label(Text="WARNING:\nThis app is using embedded Python which causes problems with Torch + CUDA!\nBecause of this, installing CUDA probably won't work or break the app!",
                          X1=Left + 10,
                          Y1=Top + 280,
                          X2=Right - 10,
                          Y2=Top + 320,
                          ID="CUDAWarning",
                          TextColor=(0, 0, 255))

            if variables.CUDAInstalled == False and variables.CUDACompatible == True:
                ImageUI.Button(Text="Install CUDA libraries (3GB)",
                               X1=Right / 2 + 5,
                               Y1=Bottom - 50,
                               X2=Right - 10,
                               Y2=Bottom - 10,
                               ID="InstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas"), pytorch.InstallCUDA()})

                ImageUI.Button(Text="Keep running on CPU",
                               X1=Left + 10,
                               Y1=Bottom - 50,
                               X2=Right / 2 - 5,
                               Y2=Bottom - 10,
                               ID="Don'tInstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas")})
            elif variables.CUDAInstalled == False and variables.CUDAAvailable == False and variables.CUDACompatible == False:
                ImageUI.Button(Text="Install CUDA libraries anyway (3GB)",
                               X1=Right / 2 + 5,
                               Y1=Bottom - 50,
                               X2=Right - 10,
                               Y2=Bottom - 10,
                               ID="InstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas"), pytorch.InstallCUDA()})

                ImageUI.Button(Text="Keep running on CPU",
                               X1=Left + 10,
                               Y1=Bottom - 50,
                               X2=Right / 2  - 5,
                               Y2=Bottom - 10,
                               ID="Don'tInstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas")})
            elif variables.CUDAInstalled == True and variables.CUDAAvailable == True and variables.CUDACompatible == True:
                ImageUI.Button(Text="Uninstall CUDA libraries",
                               X1=Right / 2 + 5,
                               Y1=Bottom - 50,
                               X2=Right - 10,
                               Y2=Bottom - 10,
                               ID="UninstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas"), pytorch.UninstallCUDA()})

                ImageUI.Button(Text="Keep running on GPU with CUDA",
                               X1=Left + 10,
                               Y1=Bottom - 50,
                               X2=Right / 2 - 5,
                               Y2=Bottom - 10,
                               ID="Don'tUninstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas")})
            else:
                ImageUI.Button(Text="Uninstall CUDA libraries",
                               X1=Right / 2 + 5,
                               Y1=Bottom - 50,
                               X2=Right - 10,
                               Y2=Bottom - 10,
                               ID="UninstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas"), pytorch.UninstallCUDA()})

                ImageUI.Button(Text="Keep running on CPU with CUDA",
                               X1=Left + 10,
                               Y1=Bottom - 50,
                               X2=Right / 2 - 5,
                               Y2=Bottom - 10,
                               ID="Don'tUninstallCUDAButton",
                               OnPress=lambda: {setattr(variables, "Page", "Canvas")})
        else:
            ImageUI.Label(Text=f"Checking your CUDA compatibility, please wait...",
                          X1=Left + 10,
                          Y1=Top + 10,
                          X2=Right - 10,
                          Y2=Bottom - 10,
                          ID="CUDAChecking")

    if variables.Page == "Canvas":
        ImageUI.Image(Image=canvas.Frame,
                      X1=Left,
                      Y1=Top + 50,
                      X2=Right,
                      Y2=Bottom,
                      ID="CanvasImage",
                      RoundCorners=0)

    if variables.Page == "File":
        ImageUI.Button(Text="Save",
                       X1=Left + 10,
                       Y1=Top + 60,
                       X2=Right / 2 - 5,
                       Y2=Top + 95,
                       ID="FileSave",
                       OnPress=lambda: {file.Save(Path=variables.FilePath)})

        ImageUI.Button(Text="Save as...",
                       X1=Right / 2 + 5,
                       Y1=Top + 60,
                       X2=Right - 10,
                       Y2=Top + 95,
                       ID="FileSaveAs",
                       OnPress=lambda: {file.Save()})

        ImageUI.Button(Text="Open",
                       X1=Left + 10,
                       Y1=Top + 105,
                       X2=Right / 2 - 5,
                       Y2=Top + 140,
                       ID="FileOpen",
                       OnPress=lambda: {file.Open()})

        ImageUI.Button(Text="New",
                       X1=Right / 2 + 5,
                       Y1=Top + 105,
                       X2=Right - 10,
                       Y2=Top + 140,
                       ID="FileNew",
                       OnPress=lambda: {file.New()})

        ImageUI.Switch(Text="Show grid",
                       X1=Left + 10,
                       Y1=Top + 153,
                       X2=Right - 10,
                       Y2=Top + 173,
                       ID="FileShowGrid",
                       State=variables.CanvasShowGrid,
                       OnChange=lambda State: setattr(variables, "CanvasShowGrid", State))

        ImageUI.Switch(Text="Line grid",
                       X1=Left + 10,
                       Y1=Top + 183,
                       X2=Right - 10,
                       Y2=Top + 203,
                       ID="FileLineGrid",
                       State=variables.CanvasLineGrid,
                       OnChange=lambda State: setattr(variables, "CanvasLineGrid", State))

        ImageUI.Switch(Text="Smooth lines",
                       X1=Left + 10,
                       Y1=Top + 213,
                       X2=Right - 10,
                       Y2=Top + 233,
                       ID="FileSmoothLines",
                       State=variables.SmoothLines,
                       OnChange=lambda State: setattr(variables, "SmoothLines", State))

        ImageUI.Switch(Text="Upscale lines",
                       X1=Left + 10,
                       Y1=Top + 243,
                       X2=Right - 10,
                       Y2=Top + 263,
                       ID="FileUpscaleLines",
                       State=variables.UpscaleLines,
                       OnChange=lambda State: setattr(variables, "UpscaleLines", State))

        ImageUI.Switch(Text="Anti-aliased lines",
                       X1=Left + 10,
                       Y1=Top + 273,
                       X2=Right - 10,
                       Y2=Top + 293,
                       ID="FileAntiAliasedLines",
                       State=variables.AntiAliasedLines,
                       OnChange=lambda State: setattr(variables,  "AntiAliasedLines", State))

        ImageUI.Switch(Text="Smooth interpolation",
                       X1=Left + 10,
                       Y1=Top + 303,
                       X2=Right - 10,
                       Y2=Top + 323,
                       ID="FileSmoothInterpolation",
                       State=variables.SmoothInterpolation,
                       OnChange=lambda State: setattr(variables, "SmoothInterpolation", State))

    if variables.Page == "Settings":
        ImageUI.Dropdown(Title="Language",
                         Items=AvailableLanguages,
                         DefaultItem=variables.Language,
                         X1=Left + 10,
                         Y1=Top + 60,
                         X2=Right / 2 - 5,
                         Y2=Top + 95,
                         ID="SettingsLanguage",
                         OnChange=lambda Item: {settings.Set("UI", "Language", Item), setattr(variables, "Language", Item), ImageUI.Translations.SetTranslator(SourceLanguage="English", DestinationLanguage=Item)})

        ImageUI.Dropdown(Title="Theme",
                         Items=["Dark", "Light"],
                         DefaultItem=variables.Theme,
                         X1=Right / 2 + 5,
                         Y1=Top + 60,
                         X2=Right -10,
                         Y2=Top + 95,
                         ID="SettingsTheme",
                         OnChange=SetTheme)

        ImageUI.Button(Text="Check CUDA (GPU) support",
                       X1=Left + 10,
                       Y1=Top + 105,
                       X2=Right / 2 - 5,
                       Y2=Top + 140,
                       ID="SettingsCheckCUDA",
                       OnPress=lambda: {setattr(variables, "Page", "CUDA"), pytorch.CheckCUDA()})

        ImageUI.Button(Text="Restart app in normal mode" if variables.DevelopmentMode else "Restart app in development mode",
                       X1=Right / 2 + 5,
                       Y1=Top + 105,
                       X2=Right - 10,
                       Y2=Top + 140,
                       ID="SettingsRestartApp",
                       OnPress=lambda: {
                            file.Save(Path=f"{variables.Path}cache/LastSession.txt"),
                            subprocess.Popen(f"{variables.Path}Start.bat {variables.Path}cache/LastSession.txt" if variables.DevelopmentMode else f"{variables.Path}Start.bat --dev {variables.Path}cache/LastSession.txt", cwd=variables.Path, creationflags=subprocess.CREATE_NEW_CONSOLE),
                            Close(SaveCanvas=False)
                       })

        ImageUI.Switch(Text="Hide Console",
                       X1=Left + 10,
                       Y1=Top + 153,
                       X2=Right / 2 - 5,
                       Y2=Top + 173,
                       ID="SettingsHideConsole",
                       State=HideConsoleSwitch,
                       OnChange=lambda State: {settings.Set("Console", "HideConsole", State), console.HideConsole() if State else console.RestoreConsole()})

        ImageUI.Switch(Text="Show grid",
                       X1=Left + 10,
                       Y1=Top + 203,
                       X2=Right - 10,
                       Y2=Top + 223,
                       ID="SettingsShowGrid",
                       State=ShowGrid,
                       OnChange=lambda State: settings.Set("Draw", "ShowGrid", State))

        ImageUI.Switch(Text="Line grid",
                       X1=Left + 10,
                       Y1=Top + 233,
                       X2=Right - 10,
                       Y2=Top + 253,
                       ID="SettingsLineGrid",
                       State=LineGrid,
                       OnChange=lambda State: settings.Set("Draw", "LineGrid", State))

        ImageUI.Switch(Text="Smooth lines",
                       X1=Left + 10,
                       Y1=Top + 263,
                       X2=Right - 10,
                       Y2=Top + 283,
                       ID="SettingsSmoothLines",
                       State=SmoothLines,
                       OnChange=lambda State: settings.Set("Draw", "SmoothLines", State))

        ImageUI.Switch(Text="Upscale lines",
                       X1=Left + 10,
                       Y1=Top + 293,
                       X2=Right - 10,
                       Y2=Top + 313,
                       ID="SettingsUpscaleLines",
                       State=UpscaleLines,
                       OnChange=lambda State: settings.Set("Draw", "UpscaleLines", State))

        ImageUI.Switch(Text="Anti-aliased lines",
                       X1=Left + 10,
                       Y1=Top + 323,
                       X2=Right - 10,
                       Y2=Top + 343,
                       ID="SettingsAntiAliasedLines",
                       State=AntiAliasedLines,
                       OnChange=lambda State: settings.Set("Draw",  "AntiAliasedLines", State))

        ImageUI.Switch(Text="Smooth interpolation",
                       X1=Left + 10,
                       Y1=Top + 353,
                       X2=Right - 10,
                       Y2=Top + 373,
                       ID="SettingsSmoothInterpolation",
                       State=SmoothInterpolation,
                       OnChange=lambda State: settings.Set("Draw", "SmoothInterpolation", State))

        ImageUI.Button(Text="Apply global canvas settings to current file",
                       X1=Left + 10,
                       Y1=Top + 383,
                       X2=Right / 2 - 5,
                       Y2=Top + 418,
                       ID="SettingsApplyGlobalCanvasSettingsToCurrentFile",
                       OnPress=lambda: {
                           setattr(variables, "Page", "File"),
                           setattr(variables, "SmoothLines", settings.Get("Draw", "SmoothLines", False)),
                           setattr(variables, "UpscaleLines", settings.Get("Draw", "UpscaleLines", True)),
                           setattr(variables, "AntiAliasedLines", settings.Get("Draw", "AntiAliasedLines", True)),
                           setattr(variables, "SmoothInterpolation", settings.Get("Draw", "SmoothInterpolation", False)),
                           setattr(variables, "CanvasShowGrid", settings.Get("Draw", "ShowGrid", True)),
                           setattr(variables, "CanvasLineGrid", settings.Get("Draw", "LineGrid", False)),
                           ImageUI.SetSwitch(ID="FileSmoothLines", State=variables.SmoothLines),
                           ImageUI.SetSwitch(ID="FileUpscaleLines", State=variables.UpscaleLines),
                           ImageUI.SetSwitch(ID="FileAntiAliasedLines", State=variables.AntiAliasedLines),
                           ImageUI.SetSwitch(ID="FileSmoothInterpolation", State=variables.SmoothInterpolation),
                           ImageUI.SetSwitch(ID="FileShowGrid", State=variables.CanvasShowGrid),
                           ImageUI.SetSwitch(ID="FileLineGrid", State=variables.CanvasLineGrid),
                           ImageUI.Popup(Text="Applied global canvas settings to current file",
                                         StartX1=Right * 0.3,
                                         StartY1=Bottom,
                                         StartX2=Right * 0.7,
                                         StartY2=Bottom + 20,
                                         EndX1=Right * 0.2,
                                         EndY1=Bottom - 50,
                                         EndX2=Right * 0.8,
                                         EndY2=Bottom - 10,
                                         ID="AppliedCanvasSettingsPopup")
                       })

    Frame = variables.Background.copy()
    variables.Frame = ImageUI.Update(WindowHWND=SimpleWindow.GetHandle(variables.Name), Frame=Frame)
    SimpleWindow.Show(variables.Name, Frame=variables.Frame)