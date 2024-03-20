import math
import sys

import numpy as np
from PyQt5.QtCore import QPoint, Qt, QSettings, QRect
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QApplication, QScrollBar, QLabel

from src.algo import GraphicAlgo
from src.geometry import degToRad, radToDeg, SimpleRect, GeometryUtils, Point2D
from src.modules import FileOpener, Bin10Parser, ColorControl, TimeCost, ShapeToOffsets, NearObsParser
from src.utils import GridCanvas


class NearObsViewer(GridCanvas):

    MAP_SCALE = 3  # mm

    def __init__(self):

        super().__init__()

        self.initData()

        self.horzBar = QScrollBar(self)
        self.horzBar.setGeometry(QRect(100, 10, 2000, 16))
        self.horzBar.setOrientation(Qt.Horizontal)
        self.horzBar.setObjectName("horzBar")
        self.horzBar.setMaximum(len(self.parser.timestamp) - 1)
        self.horzBar.valueChanged.connect(self.horzBarChanged)

        self.timeLabel = QLabel(self)
        self.timeLabel.setGeometry(QRect(50, 0, 200, 16))
        self.timeLabel.setText("haha")

        self.initUI('NearObs.Test')


    def initData(self):

        startTime = 0

        fileOpener = FileOpener(self, "NearObsPath")

        tc = TimeCost()

        filename = fileOpener.getPath()
        self.parser = NearObsParser(filename, startTime)


        print(ColorControl.BrFgGreen)
        print("filename: {}".format(filename))
        print("starTime: {}".format(startTime))
        print(ColorControl.BrFgRed)
        print("Parse File TimeCost: {}".format(tc.countDown()))
        print(ColorControl.End)

        self.frameNo = 0

        self.robotR = 175
        self.robotRwithGlue = self.robotR + 3.5


        self.rightBrushXOffset = 97
        self.rightBrushYOffset = -117
        self.rightBrushR = 73
        self.rightBrushRange = math.hypot(self.rightBrushYOffset, self.rightBrushXOffset)
        self.rightBrushBearing = math.atan2(self.rightBrushYOffset, self.rightBrushXOffset)

        self.robotPosX = 800
        self.robotPosY = 500


    def horzBarChanged(self, value):

        self.frameNo = value
        self.update()


    def drawRay(self, x, y, length, rad, penColor, penWidth):

        x = round(x)
        y = round(y)
        self.qp.setPen(QPen(penColor, penWidth))
        self.qp.drawLine(x, y, int(x + length * math.cos(rad)), int(y + length * math.sin(rad)))

    def drawCircle(self, x, y, r, penColor, penWidth):

        x = round(x)
        y = round(y)
        self.qp.setPen(QPen(penColor, penWidth))
        self.qp.drawEllipse(QPoint(x, y), r, r)

    def drawRobot(self, x, y, rad):

        # body
        self.drawCircle(x, y, self.robotR, QColor(0, 255, 0), 1)

        # glue
        self.drawCircle(x, y, self.robotRwithGlue, QColor(0, 200, 0), 1)

        # right brush
        self.drawCircle(x + self.rightBrushRange * math.cos(rad + self.rightBrushBearing),
                        y + self.rightBrushRange * math.sin(rad + self.rightBrushBearing),
                        self.rightBrushR, QColor(0, 255, 0), 1)

        # bearing
        self.drawRay(x, y, 250, rad, QColor(0, 255, 0), 1)


    def calcNearObs(self, data, extend):

        ts = data.timestamp
        x0, y0 = data.robotPos.x, data.robotPos.y

        nearObs = dict()
        nearShadowObs = dict()

        for dx in range(-extend, extend + 1, self.MAP_SCALE):
            for dy in range(-extend, extend + 1, self.MAP_SCALE):
                x = x0 + dx
                y = y0 + dy
                obsV = self.getObsMap(x, y)

                # timeout shadow point, remove
                if obsV < 0:
                    if ts > (-obsV) + 10000:
                        self.removeObsMap(x, y)
                        obsV = 0

                if obsV != 0:
                    deg = int(radToDeg(GeometryUtils.clipAngle(math.atan2(dy, dx))))
                    result = nearObs if obsV > 0 else nearShadowObs
                    v = result.get(deg)
                    if v is None or math.hypot(dx, dy) < math.hypot(v.x, v.y):
                        result[deg] = Point2D(dx, dy)

        self.nearObs = nearObs
        self.nearShadowObs = nearShadowObs
        print("NearObs: {} nearShadowObs: {}".format(len(nearObs), len(nearShadowObs)))


    def drawObs(self, data, color):

        self.qp.setPen(QPen(color, 1))

        for dx, dy in data:
            x, y = self.robotPosX + dx, self.robotPosY + dy
            self.qp.drawRect(x, y, 2, 2)



    def drawVisitMap(self, color):

        self.qp.setPen(QPen(color, 1))
        visitMap = self.visitMap
        for k, v in visitMap.items():
            x, y = self.visitKeyToGraphXY(k)
            self.qp.drawRect(x, y, 9, 9)



    def drawOccupyMap(self, robotPos, color):
        self.qp.setPen(QPen(color, 1))
        x0 = round(robotPos.x)
        y0 = round(robotPos.y)
        offsetX = 100
        offsetY = 100
        scale = 10
        occupyMap = self.occupyMap
        if occupyMap is not None:
            cnt = 0
            for dx in range(-50, 50):
                for dy in range(-50, 50):
                    v = occupyMap[dx + offsetX][dy + offsetY]
                    if v > 0:
                        self.qp.drawRect(x0 + dx * scale + self.paintOffsetX,
                                         y0 + dy * scale + self.paintOffsetY, 9, 9)
                        cnt += 1
            # print("cnt = ", cnt)


    def paintObjects(self):

        self.qp.setBrush(Qt.NoBrush)

        ts = self.parser.timestamp[self.frameNo]
        data = self.parser.obsData[self.frameNo]

        self.timeLabel.setText(str(ts))

        self.drawObs(data, QColor(255, 0, 0))

        # self.drawOccupyMap(robotPos, QColor(0, 255, 255))

        self.drawRobot(self.robotPosX, self.robotPosY, 0)

        # self.drawTargets(QColor(255, 255, 0))




    def keyPressEvent(self, e):
        # if QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_S:

        if e.key() == Qt.Key_A or e.key() == Qt.Key_Left:
            if self.frameNo > 0:
                self.frameNo -= 1
                self.horzBar.setSliderPosition(self.frameNo)
                # self.updateObs(self.parser.frontSpotData[self.frameNo])
                self.update()

        elif e.key() == Qt.Key_D or e.key() == Qt.Key_Right:
            if self.frameNo < len(self.parser.timestamp) - 1:
                self.frameNo += 1
                self.horzBar.setSliderPosition(self.frameNo)
                # self.updateObs(self.parser.frontSpotData[self.frameNo])
                self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = NearObsViewer()
    sys.exit(app.exec_())

