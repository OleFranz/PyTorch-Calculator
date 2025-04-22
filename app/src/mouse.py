from src.crashreport import CrashReport
import src.variables as variables
import src.ui as ui

import threading
import traceback
import ctypes
import pynput
import mouse
import numpy
import time


def Run():
    try:
        def RunThread():
            try:
                LastLeftClicked = False
                LastRightClicked = False
                LastMouseX = 0
                LastMouseY = 0
                WasDisabled = False
                MoveStart = 0, 0
                while variables.Break == False:
                    if variables.Window.get_foreground() == False or variables.Page != "Canvas" or ui.ShowContextMenu:
                        time.sleep(0.1)
                        WasDisabled = True
                        continue

                    WindowX = variables.WindowX
                    WindowY = variables.WindowY
                    WindowWidth = variables.WindowWidth
                    WindowHeight = variables.WindowHeight
                    MouseX, MouseY = mouse.get_position()
                    WindowY += 50
                    WindowHeight -= 50

                    LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                    RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight

                    if WasDisabled:
                        while True:
                            WindowX = variables.WindowX
                            WindowY = variables.WindowY
                            WindowWidth = variables.WindowWidth
                            WindowHeight = variables.WindowHeight
                            MouseX, MouseY = mouse.get_position()
                            WindowY += 50
                            WindowHeight -= 50

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
                                CanvasX = (MouseX - WindowX - variables.CanvasPosition[0]) / variables.CanvasZoom
                                CanvasY = (MouseY - WindowY - variables.CanvasPosition[1]) / variables.CanvasZoom
                                if variables.CanvasZoom < 10000:
                                    variables.CanvasZoom = variables.CanvasZoom * 1.1 if Event.dy > 0 else variables.CanvasZoom / 1.1
                                elif Event.dy < 0:
                                    variables.CanvasZoom /= 1.1
                                variables.CanvasPosition = (MouseX - WindowX - CanvasX * variables.CanvasZoom, MouseY - WindowY - CanvasY * variables.CanvasZoom)

                        if RightClicked == False:
                            MoveStart = MouseX - variables.CanvasPosition[0], MouseY - variables.CanvasPosition[1]
                        else:
                            variables.CanvasPosition = (MouseX - MoveStart[0]), (MouseY - MoveStart[1])

                        if LeftClicked == True and (MouseX - WindowX, MouseY - WindowY) not in variables.CanvasTemp:
                            variables.CanvasTemp.append(((MouseX - WindowX - variables.CanvasPosition[0]) * 1/variables.CanvasZoom, (MouseY - WindowY - variables.CanvasPosition[1]) * 1/variables.CanvasZoom))

                        if LeftClicked == False and LastLeftClicked == True:
                            if variables.SmoothLines:
                                TEMP = []
                                for Point in variables.CanvasTemp:
                                    if Point not in TEMP:
                                        TEMP.append(Point)
                                variables.CanvasTemp = TEMP
                                Smoothness = len(variables.CanvasTemp) // 50
                                for _ in range(Smoothness):
                                    TEMP = []
                                    for i in range(len(variables.CanvasTemp)):
                                        if i < Smoothness:
                                            XAvg = sum(P[0] for P in variables.CanvasTemp[:i+Smoothness+1]) // (i+Smoothness+1)
                                            YAvg = sum(P[1] for P in variables.CanvasTemp[:i+Smoothness+1]) // (i+Smoothness+1)
                                            TEMP.append((XAvg, YAvg))
                                        elif i >= len(variables.CanvasTemp) - Smoothness:
                                            XAvg = sum(P[0] for P in variables.CanvasTemp[i-Smoothness:]) // (len(variables.CanvasTemp) - i + Smoothness)
                                            YAvg = sum(P[1] for P in variables.CanvasTemp[i-Smoothness:]) // (len(variables.CanvasTemp) - i + Smoothness)
                                            TEMP.append((XAvg, YAvg))
                                        else:
                                            XAvg = sum(P[0] for P in variables.CanvasTemp[i-Smoothness:i+Smoothness+1]) // (2*Smoothness + 1)
                                            YAvg = sum(P[1] for P in variables.CanvasTemp[i-Smoothness:i+Smoothness+1]) // (2*Smoothness + 1)
                                            TEMP.append((XAvg, YAvg))
                                    variables.CanvasTemp = TEMP

                            if variables.UpscaleLines:
                                TEMP = []
                                for _ in range(15):
                                    for i in range(len(variables.CanvasTemp)-2):
                                        X1, Y1 = variables.CanvasTemp[i]
                                        X2, Y2 = variables.CanvasTemp[i+1]
                                        X3, Y3 = variables.CanvasTemp[i+2]
                                        X = (X1*0.3 + X2*0.4 + X3*0.3)
                                        Y = (Y1*0.3 + Y2*0.4 + Y3*0.3)
                                        TEMP.append((X, Y))
                                TEMP.append(variables.CanvasTemp[-1])
                                variables.CanvasTemp = TEMP

                            if variables.SmoothInterpolation:
                                if len(variables.CanvasTemp) > 1:
                                    TEMP = []
                                    for i in range(len(variables.CanvasTemp) - 1):
                                        p0 = variables.CanvasTemp[max(i - 1, 0)]
                                        p1 = variables.CanvasTemp[i]
                                        p2 = variables.CanvasTemp[min(i + 1, len(variables.CanvasTemp) - 1)]
                                        p3 = variables.CanvasTemp[min(i + 2, len(variables.CanvasTemp) - 1)]
                                        for t in numpy.linspace(0, 1, 50):
                                            X = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t**2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t**3)
                                            Y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t**2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t**3)
                                            TEMP.append([X, Y])
                                    variables.CanvasTemp = TEMP

                            TEMP = []
                            TEMP.append((min(P[0] for P in variables.CanvasTemp), min(P[1] for P in variables.CanvasTemp), max(P[0] for P in variables.CanvasTemp), max(P[1] for P in variables.CanvasTemp)))
                            for Point in variables.CanvasTemp:
                                if Point not in TEMP:
                                    TEMP.append(Point)
                            variables.CanvasContent.append(TEMP)
                            variables.CanvasTemp = []

                    LastMouseX, LastMouseY = MouseX, MouseY
                    LastLeftClicked, LastRightClicked = LeftClicked, RightClicked
            except:
                CrashReport("Mouse - Error in function RunThread.", str(traceback.format_exc()))
        threading.Thread(target=RunThread, daemon=True).start()
    except:
        CrashReport("Mouse - Error in function Run.", str(traceback.format_exc()))