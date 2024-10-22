import math
import sys

import numpy as np
from PyQt5.QtCore import QPoint, Qt, QSettings, QRect
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QApplication, QScrollBar, QLabel

from src.algo import GraphicAlgo
from src.geometry import degToRad, radToDeg, SimpleRect, GeometryUtils, Point2D
from src.modules import FileOpener, Bin10Parser, ColorControl, TimeCost, ShapeToOffsets
from src.utils import GridCanvas


class GotoDwaTestGui(GridCanvas):

    MAP_SCALE = 3  # mm

    def __init__(self):

        super().__init__()

        self.initData()

        self.horzBar = QScrollBar(self)
        self.horzBar.setGeometry(QRect(100, 10, 2000, 16))
        self.horzBar.setOrientation(Qt.Horizontal)
        self.horzBar.setObjectName("horzBar")
        self.horzBar.setMaximum(len(self.parser.frontSpotData) - 1)
        self.horzBar.valueChanged.connect(self.horzBarChanged)

        self.timeLabel = QLabel(self)
        self.timeLabel.setGeometry(QRect(50, 0, 200, 16))
        self.timeLabel.setText("haha")

        self.initUI('GotoDwa.Test')


    def initData(self):

        startTime = 0

        fileOpener = FileOpener(self, "GotoDwaPath")

        filename = fileOpener.getPath()

        tc = TimeCost()

        self.parser = Bin10Parser(filename, startTime)


        print(ColorControl.BrFgGreen)
        print("filename: {}".format(filename))
        print("starTime: {}".format(startTime))
        print(ColorControl.BrFgRed)
        print("Parse File TimeCost: {}".format(tc.countDown()))
        print(ColorControl.End)

        bound = SimpleRect()
        for data in self.parser.frontSpotData:
            bound.expand(data.robotPos.x, data.robotPos.y)

        print(ColorControl.BrFgGreen)
        print("bound: {} {} {} {}".format(bound.left, bound.bottom, bound.right, bound.top))
        print(ColorControl.End)
        self.paintOffsetX = 400 - bound.left
        self.paintOffsetY = 200 - bound.bottom

        self.frameNo = 0

        self.robotR = 175
        self.robotRwithGlue = self.robotR + 3.5

        r = round(self.robotRwithGlue) // self.MAP_SCALE
        self.circleOffsets = ShapeToOffsets.getCircle(r)
        print("circlePoints size: {}".format(len(self.circleOffsets)))

        self.rightBrushXOffset = 97
        self.rightBrushYOffset = -117
        self.rightBrushR = 73
        self.rightBrushRange = math.hypot(self.rightBrushYOffset, self.rightBrushXOffset)
        self.rightBrushBearing = math.atan2(self.rightBrushYOffset, self.rightBrushXOffset)

        self.obsMap = dict()
        self.visitMap = dict()

        self.nearObs = dict()
        self.nearShadowObs = dict()

        self.targetPts = []

        self.occupyMap = None


        # self.speed = 100.0
        # self.yawSpeed = degToRad(10)
        #
        # self.robotPosX = 600
        # self.robotPosY = 300
        # self.robotBearing = degToRad(0)
        #
        # self.obsPts = []
        # for y in range(100, 800, 5):
        #     self.obsPts.append((800, y))
        # for y in range(150, 600, 50):
        #     self.obsPts.append((790, y))
        # for x in range(790, 1300, 10):
        #     self.obsPts.append((x, 800))
        # for x in range(900, 1200, 80):
        #     self.obsPts.append((x, 810))
        #
        # ptsStr = "-34,-9 -24,-44 -17,-57 28,-113 48,-141 63,-166 77,-191 66,-156 68,-147 92,-174 102,-177 109,-182 125,-166 172,-220 136,-168 144,-172 138,-159 156,-173 189,-196 186,-173 179,-161 172,-149 209,-169 201,-157 186,-140 204,-148 215,-150 207,-139"
        # self.obsPts = []
        # for s in ptsStr.split(" "):
        #     x, y = map(int, s.split(","))
        #     # print(x, y)
        #     self.obsPts.append((self.robotPosX + x, self.robotPosY + y))
        #
        # self.centerPts = []
        #

        #
        # self.occupyMap = None


    def robotToSlam(self, robotPos, x, y):
        b0 = robotPos.bearing
        c, s = math.cos(b0), math.sin(b0)
        return int(robotPos.x + x * c - y * s), int(robotPos.y + x * s + y * c)

    def slamToRobot(self, robotPos, x, y):

        b0 = robotPos.bearing
        c, s = math.cos(-b0), math.sin(-b0)
        return int(robotPos.x + x * c - y * s), int(robotPos.y + x * s + y * c)

    def slamToLocal(self, x, y):

        return (x + self.paintOffsetX) // self.MAP_SCALE, (y + self.paintOffsetY) // self.MAP_SCALE

    def localToSlam(self, x, y):

        return x * self.MAP_SCALE - self.paintOffsetX, y * self.MAP_SCALE - self.paintOffsetY

    def localToGraph(self, x, y):

        return x * self.MAP_SCALE, y * self.MAP_SCALE

    def robotToLocal(self, robotPos, x, y):

        return self.slamToLocal(*self.robotToSlam(robotPos, x, y))

    def localToRobot(self, robotPos, x, y):

        return self.slamToRobot(robotPos, *self.localToSlam(x, y))

    def slamToGraph(self, x, y):

        return x + self.paintOffsetX, y + self.paintOffsetY

    def graphToSlam(self, x, y):

        return x - self.paintOffsetX, y - self.paintOffsetY

    def localXYToKey(self, x, y):

        return (x << 16) | y

    def localKeyToXY(self, k):

        return k >> 16, k & 0xFFFF

    def slamToLocalKey(self, x, y):

        x1, y1 = self.slamToLocal(x, y)
        return self.localXYToKey(x1, y1)

    def setObsMapLocal(self, x, y, v):

        k = self.localXYToKey(x, y)
        self.obsMap[k] = v

    def removeObsMapLocal(self, x, y):

        k = self.localXYToKey(x, y)
        v = self.obsMap.get(k)
        if v is not None:
            del self.obsMap[k]

    def shadowObsMapLocal(self, x, y):

        k = self.localXYToKey(x, y)
        v = self.obsMap.get(k)
        if v is not None and v > 0:
            self.obsMap[k] = -v

    def setObsMap(self, x, y, v):

        self.obsMap[self.slamToLocalKey(x, y)] = v

    def getObsMap(self, x, y):

        return self.obsMap.get(self.slamToLocalKey(x, y), 0)

    def shadowObsMap(self, x, y, newV = -1):

        k = self.slamToLocalKey(x, y)
        v = self.obsMap.get(k)
        if v is not None:
            self.obsMap[k] = newV

    def removeObsMap(self, x, y):

        k = self.slamToLocalKey(x, y)
        v = self.obsMap.get(k)
        if v is not None:
            del self.obsMap[k]

    def slamToVisitKey(self, x, y):

        mapX = (x + self.paintOffsetX) // 10
        mapY = (y + self.paintOffsetY) // 10

        return (mapX << 16) | mapY

    def visitKeyToGraphXY(self, k):

        x = k >> 16
        y = k & 0xFFFF
        return x * 10, y * 10


    def setVisitMap(self, x, y, v):

        self.visitMap[self.slamToVisitKey(x, y)] = v


    def horzBarChanged(self, value):

        self.frameNo = value
        self.update()


    def updateRobotPos(self):
        for i in range(self.FrameSpeed):
            dis = self.speed * 0.001
            self.robotPosX += dis * math.cos(self.robotBearing)
            self.robotPosY += dis * math.sin(self.robotBearing)
            self.robotBearing += self.yawSpeed * 0.001

        if self.speed > 0:
            self.centerPts.append((self.robotPosX, self.robotPosY))

    def calcNewSpeed(self, robotPos):

        tc = TimeCost()

        occupyMap = np.zeros((200, 200), dtype=int)
        offsetX = 100
        offsetY = 100

        def getMapV(xx, yy):
            return occupyMap[xx + offsetX][yy + offsetY]

        def setMapV(xx, yy, v):
            occupyMap[xx + offsetX][yy + offsetY] = v

        def updateMapV(xx, yy, v):
            if v > occupyMap[xx + offsetX][yy + offsetY]:
                occupyMap[xx + offsetX][yy + offsetY] = v

        x0, y0, b0 = robotPos.x, robotPos.y, robotPos.bearing
        scale = 10
        circleOffsets = ShapeToOffsets.getCircle(round(self.robotRwithGlue + 30) // scale)
        for k, v in self.nearObs.items():
            for offX, offY in circleOffsets:
                dist = math.hypot(offX, offY)
                if dist <= self.robotRwithGlue:
                    cost = int(100 - dist)
                else:
                    cost = int(40 - dist)
                updateMapV(v.x // scale + offX, v.y // scale + offY, cost)

        print("nearObs {} cost {}".format(len(self.nearObs), tc.countDown()))

        for k, v in self.nearShadowObs.items():
            for offX, offY in circleOffsets:
                x, y = v.x // scale + offX, v.y // scale + offY
                dist = math.hypot(offX, offY)
                if dist <= self.robotRwithGlue:
                    cost = int(98 - math.hypot(offX, offY))
                else:
                    cost = int(30 - dist)
                updateMapV(x, y, cost)

        print("nearShadowObs {} cost {}".format(len(self.nearShadowObs), tc.countDown()))

        checkDis = 160
        minV = 1000000
        goodDiffBearing = -10000

        def check(dis, deg):
            nonlocal minV
            nonlocal goodDiffBearing
            dx = round(dis * math.cos(b0 + degToRad(deg)))
            dy = round(dis * math.sin(b0 + degToRad(deg)))
            v = getMapV(dx // scale, dy // scale)
            if v < minV:
                minV = v
                goodDiffBearing = degToRad(deg)


        for deg in range(60):
            check(checkDis, deg)
            check(checkDis, -deg)

        print("minV {} goodDiffBearing {} check 60 cost {}".format(minV, goodDiffBearing, tc.countDown()))


        if goodDiffBearing != -10000:

            print("target: {} {}", x0 + checkDis * math.cos(b0 + goodDiffBearing), y0 + checkDis * math.sin(b0 + goodDiffBearing))

            self.targetPts.append((int(x0 + checkDis * math.cos(b0 + goodDiffBearing)),
                                   int(y0 + checkDis * math.sin(b0 + goodDiffBearing))))

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

            self.speed = 0
            self.yawSpeed = 0

        self.occupyMap = occupyMap

        print("calc speed cost {}".format(tc.countDown()))


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
    #         super(GotoDwaTestGui, self).timerEvent(event)

    # def timerEvent(self, event):
    #     if event.timerId() == self.timer.timerId():
    #         t1 = time.perf_counter()
    #         self.updateRobotPos()
    #         t2 = time.perf_counter()
    #         self.update()
    #         t3 = time.perf_counter()
    #         self.calcNewSpeed()
    #         t4 = time.perf_counter()
    #         # print(t2 - t1, t3 - t2, t4 - t3)
    #     else:
    #         super(GotoDwaTestGui, self).timerEvent(event)



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

        gx, gy = self.slamToGraph(x, y)

        # body
        self.drawCircle(gx, gy, self.robotR, QColor(0, 255, 0), 1)

        # glue
        self.drawCircle(gx, gy, self.robotRwithGlue, QColor(0, 200, 0), 1)

        # right brush
        self.drawCircle(gx + self.rightBrushRange * math.cos(rad + self.rightBrushBearing),
                        gy + self.rightBrushRange * math.sin(rad + self.rightBrushBearing),
                        self.rightBrushR, QColor(0, 255, 0), 1)

        # bearing
        self.drawRay(gx, gy, 250, rad, QColor(0, 255, 0), 1)


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

    def updateObs(self, data):

        tc = TimeCost()

        ts = data.timestamp
        points = data.points
        robotPos = data.robotPos
        x0, y0, b0 = robotPos.x, robotPos.y, robotPos.bearing
        d45 = degToRad(45)

        if self.frameNo > 0:
            prevData = self.parser.frontSpotData[self.frameNo-1]
            prevRobotPos = prevData.robotPos
            slamDist = math.hypot(robotPos.x - prevRobotPos.x, robotPos.y - prevRobotPos.y)
            print("posDist {}".format(slamDist))
            prevOdoPos = prevData.odoPos
            curOdoPos = data.odoPos
            odoDist = math.hypot(curOdoPos.x - prevOdoPos.x, curOdoPos.y - prevOdoPos.y)
            print("odoPosDist {}".format(odoDist))
            if math.fabs(slamDist - odoDist) > 5:
                print("pos mismatch, ignore!")
                return


        # tof camera pos
        cameraX, cameraY = self.robotR, 0
        cameraSlamX, cameraSlamY = self.robotToSlam(data.robotPos, cameraX, cameraY)
        cameraLocalX, cameraLocalY = self.slamToLocal(cameraSlamX, cameraSlamY)

        obsPoints = set()
        spacePoints = set()

        countAll = 0
        for pt in points:
            x, y, z = pt.x, pt.y, pt.z
            dist = math.hypot(pt.x, pt.y)
            if 20 <= z < 80 and -d45 < math.atan2(y - cameraY, x - cameraX) < d45 and dist > 205:
                pointLocalX, pointLocalY = self.robotToLocal(data.robotPos, x, y)
                if (int(pointLocalX), int(pointLocalY)) in obsPoints:
                    continue
                obsPoints.add((int(pointLocalX), int(pointLocalY)))
                spaceLocal = GraphicAlgo.getBresenhamPoints8(
                    QPoint(cameraLocalX, cameraLocalY), QPoint(pointLocalX, pointLocalY))
                countAll += len(spaceLocal)
                for spc in spaceLocal:
                    spacePoints.add((spc.x(), spc.y()))

        print("======= countAll {} spaceCount {}   {} ==============".format(
              countAll, len(spacePoints), countAll / len(spacePoints)))

        for pt in spacePoints:
            x, y = pt
            self.removeObsMapLocal(x, y)
            self.setVisitMap(*self.localToSlam(x, y), 1)

        for pt in obsPoints:
            x, y = pt
            self.setObsMapLocal(x, y, ts)

        circleOffsets = self.circleOffsets
        localX, localY = self.slamToLocal(x0, y0)
        for offX, offY in circleOffsets:
            self.removeObsMapLocal(localX + offX, localY + offY)



        # print("{}: map has {} pts".format(self.frameNo, len(self.obsMap)))

        # print("update obsMap cost: {}".format(tc.countDown()))

        self.calcNearObs(data, 300)

        # print("calc nearObs cost: {}".format(tc.countDown()))

        # self.calcNewSpeed(robotPos)

        # print("calc newSpeed cost: {}".format(tc.countDown()))


    def drawTargets(self, color):

        self.qp.setPen(QPen(color, 1))
        pts = self.targetPts

        for x, y in pts:
            x1, y1 = self.slamToGraph(x, y)
            self.qp.drawRect(x1, y1, 2, 2)

        if len(pts) > 0:
            self.qp.setPen(QPen(QColor(255, 0, 0), 1))
            self.qp.drawRect(*self.slamToGraph(*pts[-1]), 2, 2)

    def drawObs(self, color):

        self.qp.setPen(QPen(color, 1))
        obsMap = self.obsMap

        for k, v in obsMap.items():
            if v > 0:
                x, y = self.localToGraph(*self.localKeyToXY(k))
                self.qp.drawRect(x, y, 2, 2)

    def drawShadowObs(self, color):

        self.qp.setPen(QPen(color, 1))
        obsMap = self.obsMap

        for k, v in obsMap.items():
            if v < 0:
                x, y = self.localToGraph(*self.localKeyToXY(k))
                self.qp.drawRect(x, y, 2, 2)

    def drawInstantObs(self, color):

        self.qp.setPen(QPen(color, 1))
        data = self.parser.frontSpotData[self.frameNo]
        points = data.points
        robotPos = data.robotPos
        d45 = degToRad(45)

        for pt in points:
            x, y, z = pt.x, pt.y, pt.z
            if 20 <= z < 80 and -d45 < math.atan2(y, x - self.robotR) < d45:
                x2, y2 = self.slamToGraph(*self.robotToSlam(robotPos, x, y))
                self.qp.drawRect(x2, y2, 2, 2)


    def drawNearObs(self, robotPos, color):

        self.qp.setPen(QPen(color, 1))
        x0, y0 = robotPos.x, robotPos.y
        nearObs = self.nearShadowObs
        for k, v in nearObs.items():
            x = x0 + v.x + self.paintOffsetX
            y = y0 + v.y + self.paintOffsetY
            self.qp.drawRect(x, y, 2, 2)

        for k, v in nearObs.items():
            x = x0 + v.x + self.paintOffsetX
            y = y0 + v.y + self.paintOffsetY
            self.drawCircle(x, y, self.robotRwithGlue, QColor(200, 200, 200), 1)

        nearObs = self.nearObs
        for k, v in nearObs.items():
            x = x0 + v.x + self.paintOffsetX
            y = y0 + v.y + self.paintOffsetY
            self.drawCircle(x, y, self.robotRwithGlue, QColor(200, 200, 200), 1)


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

        data = self.parser.frontSpotData[self.frameNo]
        robotPos = data.robotPos

        # self.drawVisitMap(QColor(255, 255, 0))

        self.timeLabel.setText(str(data.timestamp))

        self.drawObs(QColor(255, 0, 0))

        self.drawShadowObs(QColor(64, 64, 64))

        self.drawInstantObs(QColor(0, 0, 255))

        self.drawNearObs(data.robotPos, QColor(0, 255, 0))

        self.drawOccupyMap(robotPos, QColor(0, 255, 255))

        self.drawRobot(robotPos.x, robotPos.y, robotPos.bearing)

        self.drawTargets(QColor(255, 255, 0))

        # self.qp.setBrush(Qt.NoBrush)
        # self.drawObs(self.frontSpotData, QColor(255, 0, 0), True)
        #
        # self.drawObs(self.centerPts, QColor(0, 0, 255), False)
        #
        # self.drawObs(self.targetPts, QColor(255, 255, 0), False)
        #

        #
        # self.drawRobot(self.robotPosX, self.robotPosY, self.robotBearing)


    def keyPressEvent(self, e):
        # if QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_S:

        if e.key() == Qt.Key_A or e.key() == Qt.Key_Left:
            if self.frameNo > 0:
                self.frameNo -= 1
                self.horzBar.setSliderPosition(self.frameNo)
                self.updateObs(self.parser.frontSpotData[self.frameNo])
                self.update()

        elif e.key() == Qt.Key_D or e.key() == Qt.Key_Right:
            if self.frameNo < len(self.parser.frontSpotData) - 1:
                self.frameNo += 1
                self.horzBar.setSliderPosition(self.frameNo)
                self.updateObs(self.parser.frontSpotData[self.frameNo])
                self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = GotoDwaTestGui()
    sys.exit(app.exec_())

