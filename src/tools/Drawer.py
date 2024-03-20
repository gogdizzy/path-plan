from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMessageBox, QInputDialog, QApplication, QFileDialog
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import QBasicTimer, QPoint, Qt, QSettings
import numpy as np
import sys, math
import struct

from src.utils import GridCanvas


class Drawer(GridCanvas):

    def __init__(self):

        super().__init__()

        self.initData()
        self.initUI('Drawer')

    def initData(self):

        pass


    def drawHouse(self):

        offsetX = 100
        offsetY = 100
        vertex = [(0, 0), (320, 0), (320, 255), (330, 255), (330, 285), (290, 285), (290, 359), (0,359), (0, 0)]

        self.qp.setPen(QPen(QColor(0, 0, 0), 2))

        for i in range(len(vertex) - 1):
            self.qp.drawLine(vertex[i][0] + offsetX, vertex[i][1] + offsetY,
                             vertex[i+1][0] + offsetX, vertex[i+1][1] + offsetY)

        self.qp.setPen(QPen(QColor(0, 255, 0), 1))
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawRect(10 + offsetX, 0 + offsetY, 150, 180)
        self.qp.drawRect(160 + offsetX, 0 + offsetY, 150, 180)
        self.qp.drawRect(10 + offsetX, 180 + offsetY, 250, 180)
        # self.qp.drawRect(150 + offsetX, 180 + offsetY, 150, 180)

        # self.qp.drawRect(0 + offsetX, 0 + offsetY, 150, 180)
        # self.qp.drawRect(150 + offsetX, 180 + offsetY, 150, 180)


    def drawRobot(self):

        robotR = 175
        robotRwithGlue = 179

        offsetX = 700
        offsetY = 250

        self.qp.setPen(QPen(QColor(0, 255, 0), 2))
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotR, robotR)
        self.qp.setPen(QPen(QColor(0, 255, 0), 1))
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotRwithGlue, robotRwithGlue)

        self.qp.setPen(QPen(QColor(0, 0, 255), 1))

        for x in range(-2, 3):
            for y in range(-2, 3):
                if math.hypot(x, y) <= 2:
                    self.qp.drawRect(x * 50 - 25 + offsetX, y * 50 - 25 + offsetY, 50, 50)

        offsetX = 1200
        offsetY = 250

        self.qp.setPen(QPen(QColor(0, 255, 0), 2))
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotR, robotR)
        self.qp.setPen(QPen(QColor(0, 255, 0), 1))
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotRwithGlue, robotRwithGlue)

        self.qp.setPen(QPen(QColor(0, 0, 255), 1))

        for x in range(-3, 4):
            for y in range(-3, 4):
                if math.hypot(x, y) <= 3:
                    self.qp.drawRect(x * 50 - 25 + offsetX, y * 50 - 25 + offsetY, 50, 50)

        offsetX = 700
        offsetY = 700

        self.qp.setPen(QPen(QColor(0, 255, 0), 2))
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotR, robotR)
        self.qp.setPen(QPen(QColor(0, 255, 0), 1))
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotRwithGlue, robotRwithGlue)

        self.qp.setPen(QPen(QColor(0, 0, 255), 1))

        for x in range(-3, 4):
            for y in range(-3, 4):
                if math.hypot(x, y) <= 3.5:
                    self.qp.drawRect(x * 50 - 25 + offsetX, y * 50 - 25 + offsetY, 50, 50)

        offsetX = 1200
        offsetY = 700

        self.qp.setPen(QPen(QColor(0, 255, 0), 2))
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotR, robotR)
        self.qp.setPen(QPen(QColor(0, 255, 0), 1))
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotRwithGlue, robotRwithGlue)

        self.qp.setPen(QPen(QColor(0, 0, 255), 1))

        for x in range(-3, 4):
            for y in range(-3, 4):
                if math.hypot(x, y) <= 4:
                    self.qp.drawRect(x * 50 - 25 + offsetX, y * 50 - 25 + offsetY, 50, 50)

        #self.redzoneR = self.robotRwithGlue + 12
        ##self.rightBrushX = self.robotX + 92
        #self.rightBrushY = self.robotY - 113
        #self.rightBrushR = 73

    def drawRobotAndCarpet(self):

        robotR = 175
        robotRwithGlue = 179

        offsetX = 1700
        offsetY = 450

        self.qp.setPen(QPen(QColor(0, 255, 0), 2))
        self.qp.setBrush(Qt.NoBrush)
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotR, robotR)
        self.qp.setPen(QPen(QColor(0, 255, 0), 1))
        self.qp.drawEllipse(QPoint(0 + offsetX, 0 + offsetY), robotRwithGlue, robotRwithGlue)

        self.qp.setPen(QPen(QColor(0, 0, 255), 3))
        for x in range(-2, 3):
            for y in range(-2, 3):
                if math.hypot(x, y) <= 1.5:
                    self.qp.drawRect(x * 50 - 25 + offsetX, y * 50 - 25 + offsetY, 50, 50)

        self.qp.setPen(QPen(QColor(255, 0, 0), 1))
        for x in range(0, 6):
            for y in range(-6, 6):
                if math.hypot(x, y) <= 5:
                    self.qp.drawRect(x * 50 - 25 + offsetX, y * 50 - 25 + offsetY, 50, 50)



    def paintObjects(self):

        self.drawHouse()
        self.drawRobot()
        self.drawRobotAndCarpet()

        #
        # self.qp.drawLine(self.robotX, self.robotY, self.robotX + 200, self.robotY)
        # self.qp.setPen(QColor(0, 200, 0))
        # self.qp.drawEllipse(QPoint(self.robotX, self.robotY), self.robotRwithGlue, self.robotRwithGlue)
        # self.qp.setPen(QColor(0, 100, 0))
        # self.qp.drawEllipse(QPoint(self.robotX, self.robotY), self.redzoneR, self.redzoneR)
        #
        # self.qp.setPen(QColor(0, 255, 0))
        # self.qp.drawEllipse(QPoint(self.rightBrushX, self.rightBrushY), self.rightBrushR, self.rightBrushR)
        #
        # self.qp.setPen(QColor(0, 0, 255))
        # for pt in self.oldPts:
        #     x, y = map(int, pt.split(","))
        #     self.qp.drawRect(self.robotX + x, self.robotY + y, 2, 2)
        #
        # self.qp.setPen(QColor(255, 0, 0))
        # for pt in self.newPts:
        #     x, y = map(int, pt.split(","))
        #     self.qp.drawRect(self.robotX + x, self.robotY + y, 2, 2)





    def drawLabel(self):

        self.qp.setPen(self.DefaultTextColor)
        self.qp.drawText(50, 50, "pos {} {} -> {} {}".format(self.mousePosBeg.x(), self.mousePosBeg.y(),
                                                             self.mousePosEnd.x(), self.mousePosEnd.y()))


    def mousePressEvent(self, e):
        self.mousePosBeg = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.mouseDown = True


    def mouseMoveEvent(self, e):
        self.mousePosEnd = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.update()


    def mouseReleaseEvent(self, e):
        self.mousePosEnd = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.mouseDown = False


    def keyPressEvent(self, e):
        if QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_S:
            self.map.saveData(self.getSaveFileName())

        elif QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_O:
            self.map.loadData(self.getOpenFileName())

        elif e.key() == Qt.Key_Backspace:
            self.data.fill(self.DEFAULT_VALUE)
            self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Drawer()
    sys.exit(app.exec_())
