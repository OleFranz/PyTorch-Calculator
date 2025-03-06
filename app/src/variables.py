import src.settings as settings
import ImageUI
import cv2
import os

OS = os.name
Path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/") + "/"
with open(Path + "config/version.txt") as File: Version = File.read()
RemoteVersion = None
Changelog = None

Language = settings.Get("UI", "Language", "English")
Theme = settings.Get("UI", "Theme", "Dark")
DevelopmentMode = False
Background = None
Canvas = None

CUDAAvailable = False
CUDAInstalled = False
CUDACompatible = False
CUDADetails = None

FilePath = ""

CanvasPosition = None, None
CanvasZoom = 1
CanvasShowGrid = settings.Get("Draw", "ShowGrid", True)
CanvasLineGrid = settings.Get("Draw", "LineGrid", False)
SmoothLines = settings.Get("Draw", "SmoothLines", False)
UpscaleLines = settings.Get("Draw", "UpscaleLines", True)
AntiAliasedLines = settings.Get("Draw", "AntiAliasedLines", True)
SmoothInterpolation = settings.Get("Draw", "SmoothInterpolation", False)
CanvasContent = []
CanvasTemp = []
CanvasDeleteList = []

DrawColor = (255, 255, 255) if Theme == "Dark" else (0, 0, 0)

WindowX = settings.Get("UI", "X", 100)
WindowY = settings.Get("UI", "Y", 100)
WindowWidth = settings.Get("UI", "Width", 960)
WindowHeight = settings.Get("UI", "Height", 540)

Name = "PyTorch-Calculator"
Page = settings.Get("UI", "Page", "Canvas")
Frame = None
Break = False

ConsoleName = None
ConsoleHWND = None