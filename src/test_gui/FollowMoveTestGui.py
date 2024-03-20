import math
import sys
import time

import numpy as np
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QApplication

from src.modules import ShapeToOffsets
from src.utils import GridCanvas


def degToRad(deg):
    return deg / 180.0 * math.pi


def radToDeg(rad):
    return rad / math.pi * 180.0


def clipAngle(rad):
    while rad >= math.pi:
        rad -= math.pi * 2
    while rad < -math.pi:
        rad += math.pi * 2


def clipValue(v, minv, maxv):
    if v < minv:
        return minv
    if v > maxv:
        return maxv
    return v


class FollowMoveTestGui(GridCanvas):

    def __init__(self):

        super().__init__()

        self.initUI('FollowMove.Test')
        self.initData()

    def initData(self):

        self.robotR = 175
        self.robotRwithGlue = self.robotR + 15

        r = self.robotRwithGlue // 10
        self.circleOffsets = ShapeToOffsets.getCircle(r)

        self.rightBrushXOffset = 97
        self.rightBrushYOffset = -117
        self.rightBrushR = 73
        self.rightBrushRange = math.hypot(self.rightBrushYOffset, self.rightBrushXOffset)
        self.rightBrushBearing = math.atan2(self.rightBrushYOffset, self.rightBrushXOffset)

        self.speed = 100.0
        self.yawSpeed = degToRad(10)

        self.robotPosX = 600
        self.robotPosY = 300
        self.robotBearing = degToRad(0)

        self.obsPts = []
        for y in range(100, 800, 5):
            self.obsPts.append((800, y))
        for y in range(150, 600, 50):
            self.obsPts.append((790, y))
        for x in range(790, 1300, 10):
            self.obsPts.append((x, 800))
        for x in range(900, 1200, 80):
            self.obsPts.append((x, 810))

        ptsStr = "-34,-9 -24,-44 -17,-57 28,-113 48,-141 63,-166 77,-191 66,-156 68,-147 92,-174 102,-177 109,-182 125,-166 172,-220 136,-168 144,-172 138,-159 156,-173 189,-196 186,-173 179,-161 172,-149 209,-169 201,-157 186,-140 204,-148 215,-150 207,-139"
        self.obsPts = []
        for s in ptsStr.split(" "):
            x, y = map(int, s.split(","))
            print(x, y)
            self.obsPts.append((self.robotPosX + x, self.robotPosY + y))

        self.centerPts = []

        self.targetPts = []

        self.occupyMap = None



    def updateRobotPos(self):
        for i in range(self.FrameSpeed):
            dis = self.speed * 0.001
            self.robotPosX += dis * math.cos(self.robotBearing)
            self.robotPosY += dis * math.sin(self.robotBearing)
            self.robotBearing += self.yawSpeed * 0.001

        if self.speed > 0:
            self.centerPts.append((self.robotPosX, self.robotPosY))

    def calcNewSpeed(self):

        partPts = []
        occupyMap = np.zeros((100, 100), dtype=int)
        offsetX = 50
        offsetY = 50

        def getMapV(xx, yy):
            return occupyMap[xx + offsetX][yy + offsetY]

        def setMapV(xx, yy, v):
            occupyMap[xx + offsetX][yy + offsetY] = v

        x0, y0 = self.robotPosX, self.robotPosY
        circleOffsets = self.circleOffsets
        for pt in self.obsPts:
            x, y = pt
            dx, dy = round(x - x0), round(y - y0)
            if math.fabs(dx) < 250 and math.fabs(dy) < 250:
                partPts.append(pt)
                for offset in circleOffsets:
                    offsetX2, offsetY2 = offset
                    setMapV(dx // 10 + offsetX2, dy // 10 + offsetY2, 1)

        dis = 30
        bearing0 = self.robotBearing

        def isClear(deg):
            newX = round(dis * math.cos(bearing0 + degToRad(deg)))
            newY = round(dis * math.sin(bearing0 + degToRad(deg)))
            return getMapV(newX // 10, newY // 10) == 0

        goodDiffBearing = -10000
        if isClear(0):
            goodDiffBearing = 0
            for deg in range(-1, -360, -1):
                if isClear(deg):
                    goodDiffBearing = degToRad(deg)
                else:
                    break
        else:
            for deg in range(1, 360, 1):
                if isClear(deg):
                    goodDiffBearing = degToRad(deg)
                    break

        self.targetPts.append((x0 + dis * math.cos(bearing0 + goodDiffBearing),
                               y0 + dis * math.sin(bearing0 + goodDiffBearing)))



        if goodDiffBearing != -10000:
            if abs(goodDiffBearing) < degToRad(15):
                self.speed = 150
                self.yawSpeed = goodDiffBearing
                #self.yawSpeed = clipValue(goodDiffBearing / (self.FrameSpeed / 1000), -degToRad(30), degToRad(30))
            elif abs(goodDiffBearing) < degToRad(30):
                self.speed = 50
                if goodDiffBearing > 0:
                    self.yawSpeed = degToRad(45)
                else:
                    self.yawSpeed = degToRad(-45)
            else:
                self.speed = 0
                if goodDiffBearing > 0:
                    self.yawSpeed = degToRad(45)
                else:
                    self.yawSpeed = degToRad(-45)

            print("goodBearing: {} {} speed: {} yawSpeed: {}".format(
                goodDiffBearing, radToDeg(goodDiffBearing), self.speed, radToDeg(self.yawSpeed)))
        else:
            print("can't follow")
            self.occupyMap = occupyMap
            self.speed = 0
            self.yawSpeed = 0




        # print("all: {} * {} = {}".format(len(partPts), len(circleOffsets), len(partPts) * len(circleOffsets)))




        #     range = math.hypot(dx, dy)
        #     bearing = clipAngle(math.atan2(dy, dx) - bearing0)
        #     if range < 30
        #
        # pass


    # def run(self):
    #
    #     self.routine = self.algo.searchGenerator(self.onNewPoint)
    #     self.routine.send(None)

    # def timerEvent(self, event):
    #     '''handles timer event'''
    #
    #     if self.state == States.Init:
    #         self.state = States.Searching
    #         self.run()
    #
    #     if event.timerId() == self.timer.timerId():
    #         self.update()
    #         if self.state == States.Searching:
    #             try:
    #                 self.routine.send(self.onNewPoint)
    #             except StopIteration:
    #                 self.state = States.Over
    #     else:
    #         super(FollowMoveTestGui, self).timerEvent(event)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            t1 = time.perf_counter()
            self.updateRobotPos()
            t2 = time.perf_counter()
            self.update()
            t3 = time.perf_counter()
            self.calcNewSpeed()
            t4 = time.perf_counter()
            # print(t2 - t1, t3 - t2, t4 - t3)
        else:
            super(FollowMoveTestGui, self).timerEvent(event)



    def drawRay(self, x, y, length, rad, penColor, penWidth):

        x = round(x)
        y = round(y)
        self.qp.setPen(QPen(penColor, penWidth))
        self.qp.drawLine(x, y, x + length * math.cos(rad), y + length * math.sin(rad))

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
        self.drawCircle(x + self.rightBrushRange * math.cos(self.robotBearing + self.rightBrushBearing),
                        y + self.rightBrushRange * math.sin(self.robotBearing + self.rightBrushBearing),
                        self.rightBrushR, QColor(0, 255, 0), 1)

        # bearing
        self.drawRay(x, y, 250, rad, QColor(0, 255, 0), 1)



    def drawObs(self, points, color, withShadow):

        self.qp.setPen(QPen(color, 1))
        for pt in points:
            x, y = pt
            self.qp.drawRect(x, y, 2, 2)

        if withShadow:
            for pt in points:
                x, y = pt
                self.drawCircle(x, y, self.robotRwithGlue, QColor(200, 200, 200), 1)


    def drawOccupyMap(self, color):
        self.qp.setPen(QPen(color, 1))
        x0 = round(self.robotPosX)
        y0 = round(self.robotPosY)
        offsetX = 50
        offsetY = 50
        occupyMap = self.occupyMap
        if self.occupyMap is not None:
            cnt = 0
            for dx in range(-50, 50):
                for dy in range(-50, 50):
                    if occupyMap[dx + offsetX][dy + offsetY] == 1:
                        self.qp.drawRect(x0 + dx * 10, y0 + dy * 10, 9, 9)
                        cnt += 1
            print("cnt = ", cnt)


    def paintObjects(self):

        self.qp.setBrush(Qt.NoBrush)

        self.drawObs(self.obsPts, QColor(255, 0, 0), True)

        self.drawObs(self.centerPts, QColor(0, 0, 255), False)

        self.drawObs(self.targetPts, QColor(255, 255, 0), False)

        # self.drawOccupyMap(QColor(0, 255, 255))

        self.drawRobot(self.robotPosX, self.robotPosY, self.robotBearing)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = FollowMoveTestGui()
    sys.exit(app.exec_())

