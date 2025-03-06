from src.crashreport import CrashReport
import src.variables as variables
import traceback
import numpy
import math
import cv2

LastContent = None
Frame = None

def Update():
    try:
        global LastContent
        global Frame

        Content = (len(variables.CanvasContent),
                   variables.CanvasPosition,
                   variables.CanvasZoom,
                   variables.CanvasShowGrid,
                   variables.CanvasLineGrid,
                   len(variables.CanvasTemp),
                   len(variables.CanvasDeleteList),
                   variables.Theme)

        if variables.Page == "Canvas" and LastContent != Content:
            if variables.Canvas.shape != (variables.WindowHeight - 50, variables.WindowWidth, 3):
                variables.Canvas = numpy.zeros((variables.WindowHeight - 50, variables.WindowWidth, 3), numpy.uint8)
                variables.Canvas[:] = ((250, 250, 250) if variables.Theme == "Light" else (28, 28, 28))
            Frame = variables.Canvas.copy()
            CANVAS_CONTENT = variables.CanvasContent
            CANVAS_POSITION = variables.CanvasPosition
            CANVAS_ZOOM = variables.CanvasZoom
            if variables.CanvasShowGrid == True:
                GridSize = 50
                GridWidth = math.ceil(Frame.shape[1] / (GridSize * CANVAS_ZOOM))
                GridHeight = math.ceil(Frame.shape[0] / (GridSize * CANVAS_ZOOM))
                if CANVAS_ZOOM > 0.05:
                    if variables.CanvasLineGrid == True:
                        for X in range(0, GridWidth):
                            PointX = round((X * GridSize + CANVAS_POSITION[0] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                            cv2.line(Frame, (PointX, 0), (PointX, Frame.shape[0]), (127, 127, 127), 1, cv2.LINE_AA if variables.AntiAliasedLines == True else cv2.LINE_8)
                        for Y in range(0, GridHeight):
                            PointY = round((Y * GridSize + CANVAS_POSITION[1] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                            cv2.line(Frame, (0, PointY), (Frame.shape[1], PointY), (127, 127, 127), 1, cv2.LINE_AA if variables.AntiAliasedLines == True else cv2.LINE_8)
                    else:
                        for X in range(0, GridWidth):
                            PointX = round((X * GridSize + CANVAS_POSITION[0] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                            for Y in range(0, GridHeight):
                                PointY = round((Y * GridSize + CANVAS_POSITION[1] / CANVAS_ZOOM % GridSize) * CANVAS_ZOOM)
                                cv2.circle(Frame, (PointX, PointY), 1, (127, 127, 127), -1, cv2.LINE_AA if variables.AntiAliasedLines == True else cv2.LINE_8)

            LastPoint = None
            for X, Y in variables.CanvasTemp:
                if LastPoint != None:
                    PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointX2 = round((X + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointY2 = round((Y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    if 0 <= PointX1 < Frame.shape[1] or 0 <= PointY1 < Frame.shape[0] or 0 <= PointX2 < Frame.shape[1] or 0 <= PointY2 < Frame.shape[0]:
                        cv2.line(Frame, (PointX1, PointY1), (PointX2, PointY2), variables.DrawColor, 3, cv2.LINE_AA if variables.AntiAliasedLines == True else cv2.LINE_8)
                LastPoint = (X, Y)

            if len(variables.CanvasTemp) == 1:
                PointX = round((variables.CanvasTemp[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                PointY = round((variables.CanvasTemp[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if 0 <= PointX < Frame.shape[1] or 0 <= PointY < Frame.shape[0]:
                    cv2.circle(Frame, (PointX, PointY), 3, variables.DrawColor, -1, cv2.LINE_AA if variables.AntiAliasedLines == True else cv2.LINE_8)
            for i in CANVAS_CONTENT:
                LastPoint = None
                MinX, MinY, MaxX, MaxY = i[0]
                MinX = round((MinX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                MinY = round((MinY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                MaxX = round((MaxX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                MaxY = round((MaxY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if MaxX >= 0 and MinX < Frame.shape[1] and MaxY >= 0 and MinY < Frame.shape[0]:
                    if len(i[0]) == 4:
                        i = i[1:]
                    for X, Y in i:
                        if LastPoint != None:
                            PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointX2 = round((X + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointY2 = round((Y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            if 0 <= PointX1 < Frame.shape[1] or 0 <= PointY1 < Frame.shape[0] or 0 <= PointX2 < Frame.shape[1] or 0 <= PointY2 < Frame.shape[0]:
                                cv2.line(Frame, (PointX1, PointY1), (PointX2, PointY2), variables.DrawColor, 3, cv2.LINE_AA if variables.AntiAliasedLines == True else cv2.LINE_8)
                        LastPoint = (X, Y)
                    if len(i) == 1:
                        PointX = round((i[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        PointY = round((i[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        if 0 <= PointX < Frame.shape[1] or 0 <= PointY < Frame.shape[0]:
                            cv2.circle(Frame, (PointX, PointY), 3, variables.DrawColor, -1, cv2.LINE_AA if variables.AntiAliasedLines == True else cv2.LINE_8)

            LastContent = Content
    except:
        CrashReport("Canvas - Error in function Update.", str(traceback.format_exc()))