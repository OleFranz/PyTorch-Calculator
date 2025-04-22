import SimpleWindow
import threading
import traceback
import ctypes
import pynput
import random
import mouse
import numpy
import math
import time
import cv2
import os


PATH = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
if PATH[-1] != "/":
    PATH += "/"

DATA_FOLDER = PATH + "dataset/raw/"

WINDOW: SimpleWindow.Window = None
WINDOWNAME = "PyTorch-Calculator - Dataset Creator"
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
WINDOW_X = 100
WINDOW_Y = 100
SIDEBAR = 200
LINE_THICKNESS = 2

CLASSES = [
           "0",
           "1",
           "2",
           "3",
           "4",
           "5",
           "6",
           "7",
           "8",
           "9",
           "+",
           "-",
           "*",
           "/",
           "~",
           "^",
           "%",
           "?",
           "!",
           ".",
           ",",
           ":",
           ";",
           "=",
           ">",
           "<",
           ">=",
           "<=",
           "|",
           "(",
           ")",
           "[",
           "]",
           "{",
           "}",
           "pi (symbol)",
           "sqrt (symbol)",
           "None"
]

AMOUNT = [0] * len(CLASSES)
if os.path.exists(f"{DATA_FOLDER}") == False:
    os.makedirs(f"{DATA_FOLDER}")
for File in os.listdir(f"{DATA_FOLDER}"):
    if File.endswith(".txt"):
        with open(f"{DATA_FOLDER}{File}", "r") as F:
            try:
                Content = F.read()
                Class, ClassIndex, CanvasContent = Content.split("###")
                AMOUNT[CLASSES.index(Class)] += 1
            except:
                print(f"Error reading file: {File}")
    elif File.endswith(".md") == False:
        os.remove(f"{DATA_FOLDER}{File}")

print("Starting with the following dataset:")
Largest = max(len(Class) for Class in CLASSES)
for i in range(len(CLASSES)):
    print(f"'{CLASSES[i]}':{' ' * (Largest-len(CLASSES[i]))} {AMOUNT[i]}")
print()


FPS = 60
BREAK = False
THEME = "Dark"

FONT_SIZE = 11
FONT_TYPE = cv2.FONT_HERSHEY_SIMPLEX
TEXT_COLOR = (255, 255, 255) if THEME == "Dark" else (0, 0, 0)
DRAW_COLOR = (255, 255, 255) if THEME == "Dark" else (0, 0, 0)
GRAYED_TEXT_COLOR = (155, 155, 155) if THEME == "Dark" else (100, 100, 100)
BACKGROUND_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)

BUTTON_COLOR = (42, 42, 42) if THEME == "Dark" else (236, 236, 236)
BUTTON_HOVER_COLOR = (47, 47, 47) if THEME == "Dark" else (231, 231, 231)
BUTTON_SELECTED_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)
BUTTON_SELECTED_HOVER_COLOR = (28, 28, 28) if THEME == "Dark" else (250, 250, 250)

CANVAS_CONTENT = []
CANVAS_POSITION = 0, 0
CANVAS_ZOOM = 1
CANVAS_SHOW_GRID = True
CANVAS_LINE_GRID = False
CANVAS_TEMP = []
CANVAS_DELETE_LIST = []

FRAME = numpy.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), numpy.uint8)
FRAME[:] = BACKGROUND_COLOR
CANVAS = numpy.zeros((WINDOW_HEIGHT, WINDOW_WIDTH - SIDEBAR, 3), numpy.uint8)
CANVAS[:] = BACKGROUND_COLOR


def RunMouse():
    try:
        def RunMouseThread():
            try:
                LastLeftClicked = False
                LastRightClicked = False
                LastMouseX = 0
                LastMouseY = 0
                WasDisabled = False
                MoveStart = 0, 0
                while BREAK == False:
                    if WINDOW.get_foreground() == False:
                        time.sleep(0.1)
                        WasDisabled = True
                        continue

                    global CANVAS_POSITION, CANVAS_ZOOM, CANVAS_TEMP

                    WindowX, WindowY = WINDOW.get_position()
                    WindowWidth, WindowHeight = WINDOW.get_size()
                    MouseX, MouseY = mouse.get_position()

                    WindowWidth -= SIDEBAR

                    LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                    RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight

                    if WasDisabled:
                        while True:
                            WindowX, WindowY = WINDOW.get_position()
                            WindowWidth, WindowHeight = WINDOW.get_size()
                            MouseX, MouseY = mouse.get_position()

                            LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                            RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                            if LeftClicked == False and RightClicked == False:
                                WasDisabled = False
                                LastLeftClicked = False
                                LastRightClicked = False
                                break

                    if WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight:

                        with pynput.mouse.Events() as Events:
                            Event = Events.get()
                            if isinstance(Event, pynput.mouse.Events.Scroll):
                                CanvasX = (MouseX - WindowX - CANVAS_POSITION[0]) / CANVAS_ZOOM
                                CanvasY = (MouseY - WindowY - CANVAS_POSITION[1]) / CANVAS_ZOOM
                                if CANVAS_ZOOM < 10000:
                                    CANVAS_ZOOM = CANVAS_ZOOM * 1.1 if Event.dy > 0 else CANVAS_ZOOM / 1.1
                                elif Event.dy < 0:
                                    CANVAS_ZOOM /= 1.1
                                CANVAS_POSITION = (MouseX - WindowX - CanvasX * CANVAS_ZOOM, MouseY - WindowY - CanvasY * CANVAS_ZOOM)

                        if RightClicked == False:
                            MoveStart = MouseX - CANVAS_POSITION[0], MouseY - CANVAS_POSITION[1]
                        else:
                            CANVAS_POSITION = (MouseX - MoveStart[0]), (MouseY - MoveStart[1])

                        if LeftClicked == True and (MouseX - WindowX, MouseY - WindowY) not in CANVAS_TEMP:
                            CANVAS_TEMP.append(((MouseX - WindowX - CANVAS_POSITION[0]) * 1/CANVAS_ZOOM, (MouseY - WindowY - CANVAS_POSITION[1]) * 1/CANVAS_ZOOM))

                        if LeftClicked == False and LastLeftClicked == True:
                            TEMP = []
                            TEMP.append((min(P[0] for P in CANVAS_TEMP), min(P[1] for P in CANVAS_TEMP), max(P[0] for P in CANVAS_TEMP), max(P[1] for P in CANVAS_TEMP)))
                            for Point in CANVAS_TEMP:
                                if Point not in TEMP:
                                    TEMP.append(Point)
                            CANVAS_CONTENT.append(TEMP)
                            CANVAS_TEMP = []

                    LastMouseX, LastMouseY = MouseX, MouseY
                    LastLeftClicked, LastRightClicked = LeftClicked, RightClicked
            except:
                print("Mouse - Error in function RunMouseThread.", str(traceback.format_exc()))
        threading.Thread(target=RunMouseThread, daemon=True).start()
    except:
        print("Mouse - Error in function RunMouse.", str(traceback.format_exc()))


def RunKeyboard():
    try:
        def RunKeyboardThread():
            try:
                LastCtrlZClicked, LastCtrlYClicked = False, False
                while BREAK == False:
                    Start = time.time()

                    if WINDOW.get_foreground() == False:
                        time.sleep(0.1)
                        continue

                    CtrlZClicked = ctypes.windll.user32.GetKeyState(0x5A) & 0x8000 != 0
                    CtrlYClicked = ctypes.windll.user32.GetKeyState(0x59) & 0x8000 != 0

                    if CtrlZClicked == True and LastCtrlZClicked == False:
                        if len(CANVAS_CONTENT) > 0:
                            CANVAS_DELETE_LIST.append(CANVAS_CONTENT[-1])
                            CANVAS_CONTENT.pop()

                    if CtrlYClicked == True and LastCtrlYClicked == False:
                        if len(CANVAS_DELETE_LIST) > 0:
                            CANVAS_CONTENT.append(CANVAS_DELETE_LIST[-1])
                            CANVAS_DELETE_LIST.pop()

                    LastCtrlZClicked = CtrlZClicked
                    LastCtrlYClicked = CtrlYClicked

                    TimeToSleep = 1/FPS - (time.time() - Start)
                    if TimeToSleep > 0:
                        time.sleep(TimeToSleep)
            except:
                print("Keyboard - Error in function RunKeyboardThread.", str(traceback.format_exc()))
        threading.Thread(target=RunKeyboardThread, daemon=True).start()
    except:
        print("Keyboard - Error in function RunKeyboard.", str(traceback.format_exc()))


def GetTextSize(Text="NONE", TextWidth=100, Fontsize=FONT_SIZE):
    try:
        Fontscale = 1
        Textsize, _ = cv2.getTextSize(Text, FONT_TYPE, Fontscale, 1)
        WidthCurrentText, HeightCurrentText = Textsize
        maxCountCurrentText = 3
        while WidthCurrentText != TextWidth or HeightCurrentText > Fontsize:
            Fontscale *= min(TextWidth / Textsize[0], Fontsize / Textsize[1])
            Textsize, _ = cv2.getTextSize(Text, FONT_TYPE, Fontscale, 1)
            maxCountCurrentText -= 1
            if maxCountCurrentText <= 0:
                break
        Thickness = round(Fontscale * 2)
        if Thickness <= 0:
            Thickness = 1
        return Text, Fontscale, Thickness, Textsize[0], Textsize[1]
    except:
        print("UIComponents - Error in function GetTextSize.", str(traceback.format_exc()))
        return "", 1, 1, 100, 100


def Label(Text="NONE", X1=0, Y1=0, X2=100, Y2=100, Align="Center", Fontsize=FONT_SIZE, TextColor=TEXT_COLOR):
    try:
        Texts = Text.split("\n")
        LineHeight = ((Y2-Y1) / len(Texts))
        for i, t in enumerate(Texts):
            Text, Fontscale, Thickness, Width, Height = GetTextSize(t, round((X2-X1)), LineHeight / 1.5 if LineHeight / 1.5 < Fontsize else Fontsize)
            if Align == "Center":
                x = round(X1 + (X2-X1) / 2 - Width / 2)
            elif Align == "Left":
                x = round(X1)
            elif Align == "Right":
                x = round(X1 + (X2-X1) - Width)
            cv2.putText(Frame, Text, (x, round(Y1 + (i + 0.5) * LineHeight + Height / 2)), FONT_TYPE, Fontscale, TextColor, Thickness, cv2.LINE_AA)
    except:
        print("UIComponents - Error in function Label.", str(traceback.format_exc()))
        return False, False, False


def Button(Text="NONE", X1=0, Y1=0, X2=100, Y2=100, Fontsize=FONT_SIZE, RoundCorners=5, ButtonSelected=False, TextColor=TEXT_COLOR, ButtonColor=BUTTON_COLOR, ButtonHoverColor=BUTTON_HOVER_COLOR, ButtonSelectedColor=BUTTON_SELECTED_COLOR, ButtonSelectedHoverColor=BUTTON_SELECTED_HOVER_COLOR):
    try:
        global WINDOW_WIDTH, WINDOW_HEIGHT, MouseX, MouseY, LeftClicked, RightClicked, LastLeftClicked, LastRightClicked
        if X1 <= MouseX * WINDOW_WIDTH <= X2 and Y1 <= MouseY * WINDOW_HEIGHT <= Y2:
            ButtonHovered = True
        else:
            ButtonHovered = False
        if ButtonSelected == True:
            if ButtonHovered == True:
                cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedHoverColor, RoundCorners, cv2.LINE_AA)
                cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedHoverColor, -1, cv2.LINE_AA)
            else:
                cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedColor, RoundCorners, cv2.LINE_AA)
                cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonSelectedColor, -1, cv2.LINE_AA)
        elif ButtonHovered == True:
            cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonHoverColor, RoundCorners, cv2.LINE_AA)
            cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonHoverColor, -1, cv2.LINE_AA)
        else:
            cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonColor, RoundCorners, cv2.LINE_AA)
            cv2.rectangle(Frame, (round(X1+RoundCorners/2), round(Y1+RoundCorners/2)), (round(X2-RoundCorners/2), round(Y2-RoundCorners/2)), ButtonColor, -1, cv2.LINE_AA)
        Text, Fontscale, Thickness, Width, Height = GetTextSize(Text, round((X2-X1)), Fontsize)
        cv2.putText(Frame, Text, (round(X1 + (X2-X1) / 2 - Width / 2), round(Y1 + (Y2-Y1) / 2 + Height / 2)), FONT_TYPE, Fontscale, TextColor, Thickness, cv2.LINE_AA)
        if X1 <= MouseX * WINDOW_WIDTH <= X2 and Y1 <= MouseY * WINDOW_HEIGHT <= Y2 and LeftClicked == False and LastLeftClicked == True:
            return True, LeftClicked and ButtonHovered, ButtonHovered
        else:
            return False, LeftClicked and ButtonHovered, ButtonHovered
    except:
        print("UIComponents - Error in function Button.", str(traceback.format_exc()))
        return False, False, False


WINDOW = SimpleWindow.Window(name=WINDOWNAME,
                             size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                             position=(WINDOW_X, WINDOW_Y),
                             title_bar_color=BACKGROUND_COLOR,
                             resizable=False,
                             icon=f"{PATH}assets/icon.ico")


LastLeftClicked = False
LastRightClicked = False

List = []
Points = []
Drawlist = []
CanvasFrame = None
PreviewFrame = None
LastContent = None
LastFinalContent = None
NoneExample = random.sample([Item for Item in CLASSES if Item != "None"], random.randint(2, 4))

RunMouse()
RunKeyboard()

while True:
    Start = time.time()

    WindowX, WindowY = WINDOW.get_position()
    WindowWidth, WindowHeight = WINDOW.get_size()
    MouseX, MouseY = mouse.get_position()
    MouseRelativeWindow = MouseX - WindowX, MouseY - WindowY
    if WindowWidth != 0 and WindowHeight != 0:
        MouseX = MouseRelativeWindow[0]/WindowWidth
        MouseY = MouseRelativeWindow[1]/WindowHeight
    else:
        MouseX = 0
        MouseY = 0

    LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and 0 <= MouseX <= 1 and 0 <= MouseY <= 1
    RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and 0 <= MouseX <= 1 and 0 <= MouseY <= 1

    if AMOUNT[CLASSES.index("None")] // 10 < min([AMOUNT[i] for i in range(len(CLASSES)) if CLASSES[i] != "None"]):
        CurrentClassIndex = CLASSES.index("None")
        CurrentClass = "None"
    else:
        CurrentClassIndex = AMOUNT.index(min([AMOUNT[i] for i in range(len(CLASSES)) if CLASSES[i] != "None"]))
        CurrentClass = CLASSES[CurrentClassIndex]

    Frame = FRAME.copy()

    Content = (len(CANVAS_CONTENT),
                    CANVAS_POSITION,
                    CANVAS_ZOOM,
                    CANVAS_SHOW_GRID,
                    CANVAS_LINE_GRID,
                    len(CANVAS_TEMP),
                    len(CANVAS_DELETE_LIST),
                    DRAW_COLOR)

    if LastContent != Content:
        if FRAME.shape != (WINDOW_HEIGHT, WINDOW_WIDTH, 3):
            FRAME = numpy.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), numpy.uint8)
            FRAME[:] = BACKGROUND_COLOR
        CanvasFrame = CANVAS.copy()
        if CANVAS_SHOW_GRID == True:
            GridSize = 50
            GridWidth = math.ceil(CanvasFrame.shape[1] / (GridSize * CANVAS_ZOOM))
            GridHeight = math.ceil(CanvasFrame.shape[0] / (GridSize * CANVAS_ZOOM))
            if CANVAS_ZOOM > 0.05:
                if CANVAS_LINE_GRID == True:
                    for X in range(0, GridWidth):
                        PointX = round((X * GridSize + CANVAS_POSITION[0] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                        cv2.line(CanvasFrame, (PointX, 0), (PointX, CanvasFrame.shape[0]), (127, 127, 127), 1, cv2.LINE_AA)
                    for Y in range(0, GridHeight):
                        PointY = round((Y * GridSize + CANVAS_POSITION[1] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                        cv2.line(CanvasFrame, (0, PointY), (CanvasFrame.shape[1], PointY), (127, 127, 127), 1, cv2.LINE_AA)
                else:
                    for X in range(0, GridWidth):
                        PointX = round((X * GridSize + CANVAS_POSITION[0] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                        for Y in range(0, GridHeight):
                            PointY = round((Y * GridSize + CANVAS_POSITION[1] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                            cv2.circle(CanvasFrame, (PointX, PointY), 1, (127, 127, 127), -1, cv2.LINE_AA)

        LastPoint = None
        for X, Y in CANVAS_TEMP:
            if LastPoint != None:
                PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                PointX2 = round((X + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                PointY2 = round((Y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if 0 <= PointX1 < CanvasFrame.shape[1] or 0 <= PointY1 < CanvasFrame.shape[0] or 0 <= PointX2 < CanvasFrame.shape[1] or 0 <= PointY2 < CanvasFrame.shape[0]:
                    cv2.line(CanvasFrame, (PointX1, PointY1), (PointX2, PointY2), DRAW_COLOR, 3, cv2.LINE_AA)
            LastPoint = (X, Y)

        if len(CANVAS_TEMP) == 1:
            PointX = round((CANVAS_TEMP[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            PointY = round((CANVAS_TEMP[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            if 0 <= PointX < CanvasFrame.shape[1] or 0 <= PointY < CanvasFrame.shape[0]:
                cv2.circle(CanvasFrame, (PointX, PointY), 3, DRAW_COLOR, -1, cv2.LINE_AA)

        for i in CANVAS_CONTENT:
            LastPoint = None
            MinX, MinY, MaxX, MaxY = i[0]
            MinX = round((MinX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            MinY = round((MinY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            MaxX = round((MaxX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            MaxY = round((MaxY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
            if MaxX >= 0 and MinX < CanvasFrame.shape[1] and MaxY >= 0 and MinY < CanvasFrame.shape[0]:
                if len(i[0]) == 4:
                    i = i[1:]
                for X, Y in i:
                    if LastPoint != None:
                        PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        PointX2 = round((X + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        PointY2 = round((Y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        if 0 <= PointX1 < CanvasFrame.shape[1] or 0 <= PointY1 < CanvasFrame.shape[0] or 0 <= PointX2 < CanvasFrame.shape[1] or 0 <= PointY2 < CanvasFrame.shape[0]:
                            cv2.line(CanvasFrame, (PointX1, PointY1), (PointX2, PointY2), DRAW_COLOR, 3, cv2.LINE_AA)
                    LastPoint = (X, Y)
                if len(i) == 1:
                    PointX = round((i[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointY = round((i[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    if 0 <= PointX < CanvasFrame.shape[1] or 0 <= PointY < CanvasFrame.shape[0]:
                        cv2.circle(CanvasFrame, (PointX, PointY), 3, DRAW_COLOR, -1, cv2.LINE_AA)

        CANVAS_CHANGED = True
        LastContent = Content


    if LastFinalContent != CANVAS_CONTENT:
        Image = numpy.zeros((50, 50, 3), numpy.uint8)
        if len(CANVAS_CONTENT) > 0:
            MinX = min([Point[0] if len(Point) == 2 else float("inf") for Line in CANVAS_CONTENT for Point in Line])
            MinY = min([Point[1] if len(Point) == 2 else float("inf") for Line in CANVAS_CONTENT for Point in Line])
            MaxX = max([Point[0] if len(Point) == 2 else float("-inf") for Line in CANVAS_CONTENT for Point in Line])
            MaxY = max([Point[1] if len(Point) == 2 else float("-inf") for Line in CANVAS_CONTENT for Point in Line])
            ScaleX = ((Image.shape[1] - 1 - LINE_THICKNESS) / (MaxX - MinX)) if MaxX - MinX != 0 else 1e9
            ScaleY = ((Image.shape[0] - 1 - LINE_THICKNESS)  / (MaxY - MinY)) if MaxY - MinY != 0 else 1e9
            Scale = min(ScaleX, ScaleY)
            XOffset = ((Image.shape[1] - 1 - LINE_THICKNESS) - (MaxX - MinX) * Scale) / 2
            YOffset = ((Image.shape[0] - 1 - LINE_THICKNESS) - (MaxY - MinY) * Scale) / 2
            for Line in CANVAS_CONTENT:
                if len(Line[0]) == 4:
                    Line = Line[1:]
                LastPoint = None
                for Point in Line:
                    if LastPoint != None:
                        cv2.line(Image, (round((LastPoint[0] - MinX) * Scale + XOffset + LINE_THICKNESS / 2), round((LastPoint[1] - MinY) * Scale + YOffset + LINE_THICKNESS / 2)), (round((Point[0] - MinX) * Scale + XOffset + LINE_THICKNESS / 2), round((Point[1] - MinY) * Scale + YOffset + LINE_THICKNESS / 2)), (255, 255, 255), LINE_THICKNESS)
                    elif len(Line) == 1:
                        cv2.circle(Image, (round((Point[0] - MinX) * Scale + XOffset + LINE_THICKNESS / 2), round((Point[1] - MinY) * Scale + YOffset + LINE_THICKNESS / 2)), LINE_THICKNESS, (255, 255, 255), -1)
                    LastPoint = Point
        PreviewFrame = Image


    Label(Text=f"Draw:\n> {CurrentClass} <" if CurrentClass != "None" else "Draw:\n",
          X1=CanvasFrame.shape[1],
          Y1=10,
          X2=WINDOW_WIDTH,
          Y2=75,
          Fontsize=15)

    if CurrentClass == "None":
        Label(Text=f"Anything the AI\nshould ignore when\nshown in the app.\nFor example multiple\nsymbols at once\nin one image.\nFor example include:\n{', '.join(NoneExample)}",
              X1=CanvasFrame.shape[1],
              Y1=50,
              X2=WINDOW_WIDTH,
              Y2=180)

    Label(Text="Preview:",
          X1=CanvasFrame.shape[1],
          Y1=WINDOW_HEIGHT - 85 - SIDEBAR - 35,
          X2=WINDOW_WIDTH,
          Y2=WINDOW_HEIGHT - 85 - SIDEBAR)

    Changed, Pressed, Hovered = Button(Text="Continue",
                                       X1=CanvasFrame.shape[1] + 5,
                                       Y1=WINDOW_HEIGHT - 50,
                                       X2=WINDOW_WIDTH - 5,
                                       Y2=WINDOW_HEIGHT - 5)

    if Changed:
        if len(CANVAS_CONTENT) > 0:
            if os.path.exists(f"{DATA_FOLDER}") == False:
                os.mkdir(f"{DATA_FOLDER}")
            Name = len([File for File in os.listdir(DATA_FOLDER) if File.endswith(".txt")]) + 1
            while os.path.exists(f"{DATA_FOLDER}{Name}.txt"):
                Name += 1
            with open(f"{DATA_FOLDER}{Name}.txt", "w") as F:
                F.write(f"{CurrentClass}###{CurrentClassIndex}###{CANVAS_CONTENT}")
            CANVAS_CONTENT = []
            CANVAS_TEMP = []
            CANVAS_DELETE_LIST = []
            AMOUNT[CurrentClassIndex] += 1
            NoneExample = random.sample([Item for Item in CLASSES if Item != "None"], random.randint(2, 4))

    Changed, Pressed, Hovered = Button(Text="Undo",
                                       X1=CanvasFrame.shape[1] + 5,
                                       Y1=WINDOW_HEIGHT - 90,
                                       X2=CanvasFrame.shape[1] + (WINDOW_WIDTH - CanvasFrame.shape[1]) / 2 - 2.5,
                                       Y2=WINDOW_HEIGHT - 55)
    if Changed:
        if len(CANVAS_CONTENT) > 0:
            CANVAS_DELETE_LIST.append(CANVAS_CONTENT[-1])
            CANVAS_CONTENT.pop()

    Changed, Pressed, Hovered = Button(Text="Redo",
                                       X1=CanvasFrame.shape[1] + (WINDOW_WIDTH - CanvasFrame.shape[1]) / 2 + 2.5,
                                       Y1=WINDOW_HEIGHT - 90,
                                       X2=WINDOW_WIDTH - 5,
                                       Y2=WINDOW_HEIGHT - 55)
    if Changed:
        if len(CANVAS_DELETE_LIST) > 0:
            CANVAS_CONTENT.append(CANVAS_DELETE_LIST[-1])
            CANVAS_DELETE_LIST.pop()


    LastLeftClicked = LeftClicked
    LastRightClicked = RightClicked

    Frame[0:WINDOW_HEIGHT, 0:WINDOW_WIDTH - SIDEBAR] = CanvasFrame

    Frame[WINDOW_HEIGHT - 85 - SIDEBAR:WINDOW_HEIGHT - 95, CanvasFrame.shape[1] + 5:WINDOW_WIDTH - 5] = cv2.resize(PreviewFrame, (SIDEBAR - 10, SIDEBAR - 10))

    cv2.line(Frame, (CanvasFrame.shape[1] - 1, 0), (CanvasFrame.shape[1] - 1, CanvasFrame.shape[0] - 1), (255, 255, 255), 1, cv2.LINE_AA)

    WINDOW.show(Frame)

    if WINDOW.get_open() != True:
        break

    TimeToSleep = 1/FPS - (time.time() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)

print("Ending with the following dataset:")
Largest = max(len(Class) for Class in CLASSES)
for i in range(len(CLASSES)):
    print(f"'{CLASSES[i]}':{' ' * (Largest-len(CLASSES[i]))} {AMOUNT[i]}")