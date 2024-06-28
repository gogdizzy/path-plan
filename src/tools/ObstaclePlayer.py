from PyQt5.QtWidgets import QApplication, QScrollBar
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QPoint, Qt, QRect
import math

from src.geometry import Point2D
from src.modules import RobotModel
from src.utils import GridCanvas, Colors


class ObstaclePlayer(GridCanvas):

    def __init__(self, data = None, robotPos = None, robotModel = RobotModel.getModel_2()):

        super().__init__()

        self.data = data
        self.robotModel = robotModel

        self.initData(robotPos)

        self.horzBar = QScrollBar(self)
        self.horzBar.setGeometry(QRect(100, 10, 2000, 16))
        self.horzBar.setOrientation(Qt.Horizontal)
        self.horzBar.setObjectName("horzBar")
        self.horzBar.setMaximum(len(data) - 1)
        self.horzBar.valueChanged.connect(self.horzBarChanged)

        self.initUI('ObstaclePlayer')

        self.setMouseTracking(True)

    def horzBarChanged(self, value):

        self.frameNo = value
        self.update()

    def inBullet(self, bearing, range, dx):
        return (range * range + dx * dx - 2 * range * dx * math.cos(bearing)) < self.robotRwithGlue * self.robotRwithGlue

    def initData(self, robotPos):

        self.mousePosEnd = QPoint(0, 0)

        self.frameNo = 0

        if robotPos is None:
            self.robotX = 500
            self.robotY = 500
        else:
            self.robotX = robotPos.x
            self.robotY = robotPos.y
        # self.robotR = 175
        # self.robotRwithGlue = 178.5
        self.deltaX = 25
        self.redzoneR = self.robotModel.robotRwithGlue + self.deltaX
        # self.rightBrushXOffset = 97
        # self.rightBrushYOffset = -117
        # self.rightBrushR = 73

        self.customFunctions = dict()


    def drawLabel(self):

        self.qp.setPen(Colors.DefaultTextColor)
        dx = self.mousePosEnd.x() - self.robotX
        dy = self.mousePosEnd.y() - self.robotY
        range = math.hypot(dx, dy)
        bearing = math.atan2(dy, dx)
        data = self.data[self.frameNo]
        self.qp.drawText(50, 50, "time: {} x: {} y: {}   range: {:.2f} bearing: {:.2f} | {:.2f}".format(data.timestamp, dx, dy, range, bearing / math.pi * 180, bearing))

    def drawRay(self, x, y, deg, length, penColor, penWidth):

        self.qp.setPen(QPen(penColor, penWidth))
        rad = math.pi / 180 * deg
        self.qp.drawLine(x, y, round(x + length * math.cos(rad)), round(y + length * math.sin(rad)))

    def drawRobot(self, x, y, deg):

        model = self.robotModel

        # body
        self.qp.setPen(QColor(0, 255, 0))
        self.qp.drawEllipse(QPoint(x, y), model.robotR, model.robotR)

        # glue
        self.qp.setPen(QColor(0, 200, 0))
        self.qp.drawEllipse(QPoint(x, y), model.robotRwithGlue, model.robotRwithGlue)

        # glue
        # self.qp.setPen(QColor(0, 200, 0))
        # self.qp.drawEllipse(QPoint(x, y), self.robotR + 60, self.robotR + 60)

        # right brush
        self.qp.setPen(QColor(0, 255, 0))
        self.qp.drawEllipse(QPoint(x + model.rightBrushXOffset, y + model.rightBrushYOffset), model.rightBrushR, model.rightBrushR)
        # self.qp.drawEllipse(QPoint(x + self.rightBrushXOffset, y + self.rightBrushYOffset), self.rightBrushR + 45, self.rightBrushR + 45)

        # bearing
        self.drawRay(x, y, deg, 250, QColor(0, 255, 0), 1)

        # valid_y
        # self.drawRay(x - 200, y - 200, 0, 400, QColor(64, 64, 64), 1)


    def drawRedzone(self):

        self.qp.setPen(QColor(0, 100, 0))
        self.qp.drawEllipse(QPoint(self.robotX, self.robotY), self.redzoneR, self.redzoneR)

        self.qp.setPen(QColor(0, 50, 0))
        deltaR = self.redzoneR - self.robotRwithGlue
        rr = self.robotRwithGlue
        self.qp.drawRect(self.robotX, round(self.robotY - rr), round(deltaR), round(2 * rr))
        self.qp.drawPie(QRect(round(self.robotX + deltaR - rr), round(self.robotY - rr), round(rr * 2), round(rr * 2)),
                        -90 * 16, 180 * 16)


    def drawObs(self, points, color):

        self.qp.setPen(QPen(color, 1))
        for pt in points:
            self.qp.drawRect(self.robotX + pt.x, self.robotY + pt.y, 2, 2)




    def addCustomFunction(self, fun, layer):

        self.customFunctions.setdefault(layer, []).append(fun)

    def paintObjects(self):

        print("framNo:", self.frameNo)

        self.drawLabel()

        h = self.frameGeometry().height()
        self.qp.translate(0, h)
        self.qp.scale(1, -1)

        self.qp.setBrush(Qt.NoBrush)

        data = self.data[self.frameNo]

        for layer, funs in self.customFunctions.items():
            if layer < 0:
                for fun in funs:
                    fun(self.qp, data)

        self.drawRay(self.robotX, self.robotY, -60, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, -45, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, 60, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, -70, 400, QColor(128, 128, 128), 1)

        self.drawRobot(self.robotX, self.robotY, 0)

        # self.drawRedzone()

        self.drawObs(data.points, QColor(255, 0, 0))

        for layer, funs in self.customFunctions.items():
            if layer > 0:
                for fun in funs:
                    fun(self.qp, data)


    def mouseMoveEvent(self, e):
        self.mousePosEnd = QPoint(e.x(), e.y())
        self.update()

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_A or e.key() == Qt.Key_Left:
            if self.frameNo > 0:
                self.frameNo -= 1
                self.horzBar.setSliderPosition(self.frameNo)
                self.update()

        elif e.key() == Qt.Key_D or e.key() == Qt.Key_Right:
            if self.frameNo < len(self.data) - 1:
                self.frameNo += 1
                self.horzBar.setSliderPosition(self.frameNo)
                self.update()
