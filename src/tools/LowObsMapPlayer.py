import math
import sys

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtWidgets import QApplication

from src.geometry import *
from src.modules import FileOpener, NavNormalParser, ColorControl, TimeAndPoints, TimeCost, Bin10Parser
from src.modules.DirectoryOpener import DirectoryOpener
from src.modules.NavNormalParser import NavNormalTypes
from src.tools import ObstaclePlayer
from src.utils import Colors

ROBOT_X = 1000
ROBOT_Y = 750

ROBOT_SIDE_X = 2000
ROBOT_SIDE_Y = 800
ROBOT_SIDE_WIDTH = 350
ROBOT_SIDE_HEIGHT = 100

nearObsList = []
newObsList = []
newLowObsList = []
newProbableWireList = []
newLooseWireObsList = []
newVlineObsList = []
newVlineSpaceList = []
highObsList = []
vlineList = []
allNearObsList = []

def drawNearRange(qp, data):

    qp.setPen(QPen(QColor(150, 150, 150), 1))
    radius = 175 + 100
    qp.drawEllipse(QPoint(ROBOT_X, ROBOT_Y), radius, radius)

    radius = 175 + 30
    qp.drawEllipse(QPoint(ROBOT_X, ROBOT_Y), radius, radius)


def drawExtra(qp, data):

    h = dict()

    for pt in data.points:
        deg = clipDegree(round(radToDeg(math.atan2(pt.y, pt.x))))
        idx = deg + 180
        h.setdefault(idx, []).append(pt)

    qp.setPen(QPen(QColor(0, 0, 200), 1))

    cnt = 0
    for deg, pts in h.items():
        pts = sorted(pts, key=lambda pt: math.hypot(pt.x, pt.y))
        if len(pts) <= 3:
            for pt in pts:
                qp.drawRect(ROBOT_X + pt.x, ROBOT_Y + pt.y, 2, 2)
                cnt += 1
        else:
            for i in range(3):
                pt = pts[i]
                qp.drawRect(ROBOT_X + pt.x, ROBOT_Y + pt.y, 2, 2)
                cnt += 1

    if cnt > 300:
        print("pts: {}, filter: {}".format(len(data.points), cnt))


def printInfo(qp, data):

    cnt = dict()

    for pt in data.points:

        deg = clipDegree(round(radToDeg(math.atan2(pt.y, pt.x))))
        idx = deg + 180
        cnt.setdefault(idx, 0)
        cnt[idx] += 1

    stay = 0
    for deg, c in cnt.items():
        print(deg, c)
        stay += min(3, c)

    print("pts: {}, filter: {}".format(len(data.points), stay))

def drawOccupy(qp, data):

    radius = 200
    qp.setPen(QPen(QColor(200, 200, 200), 1))
    for pt in data.points:
        qp.drawEllipse(QPoint(ROBOT_X + pt.x, ROBOT_Y + pt.y), radius, radius)


def drawVLineData(qp, data):

    global vlineList

    if len(vlineList) <= 0:
        return

    for i in range(len(vlineList) - 1, -1, -1):
        if data.timestamp - 200 < vlineList[i].timestamp <= data.timestamp:
            line = [-1] * 50
            lowH = [100] * 50
            highH = [0] * 50
            qp.setPen(QPen(QColor(255, 0, 0), 1))
            validCnt = 0
            for pt in vlineList[i].points:
                if pt.x == 0 and pt.y == 0:
                    continue

                validCnt += 1

                if pt.y <= 2:
                    qp.setPen(QPen(QColor(0, 0, 0), 1))
                elif pt.y <= 5:
                    qp.setPen(QPen(QColor(128, 0, 0), 1))
                else:
                    qp.setPen(QPen(QColor(255, 0, 0), 1))

                x = int(pt.x / 3)
                if pt.y < 4:
                    line[x] = max(line[x], 0)
                elif 4 <= pt.y <= 5:
                    line[x] = max(line[x], 1)
                elif 5 < pt.y <= 10:
                    line[x] = max(line[x], 2)
                elif 10 < pt.y <= 15:
                    line[x] = max(line[x], 3)
                else:
                    line[x] = max(line[x], 4)

                if pt.y >= 3:
                    lowH[x] = min(lowH[x], pt.y)
                    highH[x] = max(highH[x], pt.y)


                qp.drawRect(round(ROBOT_SIDE_X + ROBOT_SIDE_WIDTH + pt.x),
                            round(ROBOT_SIDE_Y + pt.y),
                            2, 2)
            print("vlineTime: {} vlineSize: {}".format(vlineList[i].timestamp, len(vlineList[i].points)))
            print(vlineList[i].points)

            if validCnt <= 10:
                break

            print(line)
            foundWire = False
            w0 = 0
            w1 = 0
            w2 = 0
            w4 = 0
            for k in range(len(line)):
                h = line[k]
                if h <= 0:
                    if w1 > 0:
                        w2 += 1
                    else:
                        w0 += 1
                elif h >= 4:
                    break
                    # w4 += 1
                    # if w4 >= 3:
                    #     break
                    #
                    # print("diff {}".format(highH[k] - lowH[k]))
                    # if 0 <= highH[k] - lowH[k] < 10:
                    #     if w2 > 0:
                    #         w2 = 0
                    #     w1 += 1
                    # else:
                    #     break
                else:
                    if w2 > 0:
                        w2 = 0
                    w1 += 1

                if h < 4:
                    w4 = 0

                if 1 <= w1 <= 4 and w2 >= 3:
                    foundWire = True

            if foundWire:
                qp.setPen(QPen(Colors.DefaultTextColor, 2))
                font = QFont()
                font.setPointSize(20)
                qp.setFont(font)
                qp.drawText(ROBOT_SIDE_X + ROBOT_SIDE_WIDTH - 50,
                            ROBOT_SIDE_Y + 130,
                            "M!h6")
            break

def drawVLineData2(qp, data):

    global vlineList

    if len(vlineList) <= 0:
        return

    for i in range(len(vlineList) - 1, -1, -1):
        if data.timestamp - 200 < vlineList[i].timestamp <= data.timestamp:
            line = [-1] * 50
            lowH = [100] * 50
            highH = [0] * 50
            qp.setPen(QPen(QColor(255, 0, 0), 1))
            validCnt = 0
            points = vlineList[i].points

            for k in range(len(points)):
                pt = points[k]
                if pt.x == 0 and pt.y == 0:
                    continue

                validCnt += 1
                x = int(pt.x / 3)
                if pt.y >= 3:
                    lowH[x] = min(lowH[x], pt.y)
                    highH[x] = max(highH[x], pt.y)

                if pt.y <= 2:
                    qp.setPen(QPen(QColor(0, 0, 0), 1))
                elif pt.y <= 5:
                    qp.setPen(QPen(QColor(128, 0, 0), 1))
                else:
                    qp.setPen(QPen(QColor(255, 0, 0), 1))

                qp.drawRect(round(ROBOT_SIDE_X + ROBOT_SIDE_WIDTH + pt.x),
                            round(ROBOT_SIDE_Y + pt.y),
                            2, 2)

            startIdx = -1
            for k in range(len(points)):
                pt = points[k]
                if pt.x == 0 and pt.y == 0:
                    continue

                x = int(pt.x / 3)
                if pt.y <= 2:
                    startIdx = k
                elif highH[x] > 20:
                    break
                elif 4 <= pt.y <= 15 and highH[x] < 20 and startIdx >= 0:
                    line[x] = max(line[x], 1)
                elif 5 < pt.y <= 10:
                    line[x] = max(line[x], 2)
                elif 10 < pt.y <= 15:
                    line[x] = max(line[x], 3)
                else:
                    line[x] = max(line[x], 4)

            print("vlineTime: {} vlineSize: {}".format(vlineList[i].timestamp, len(vlineList[i].points)))
            print(vlineList[i].points)

            if validCnt <= 10:
                break

            print(line)
            foundWire = False
            w0 = 0
            w1 = 0
            w2 = 0
            w4 = 0
            for k in range(len(line)):
                h = line[k]
                if h <= 0:
                    if w1 > 0:
                        w2 += 1
                    else:
                        w0 += 1
                elif h >= 4:
                    break
                    # w4 += 1
                    # if w4 >= 3:
                    #     break
                    #
                    # print("diff {}".format(highH[k] - lowH[k]))
                    # if 0 <= highH[k] - lowH[k] < 10:
                    #     if w2 > 0:
                    #         w2 = 0
                    #     w1 += 1
                    # else:
                    #     break
                else:
                    if w2 > 0:
                        w2 = 0
                    w1 += 1

                if h < 4:
                    w4 = 0

                if 1 <= w1 <= 6 and w2 >= 3:
                    print("k = {}".format(k))
                    foundWire = True

            if foundWire:
                qp.setPen(QPen(Colors.DefaultTextColor, 2))
                font = QFont()
                font.setPointSize(20)
                qp.setFont(font)
                qp.drawText(ROBOT_SIDE_X + ROBOT_SIDE_WIDTH - 50,
                            ROBOT_SIDE_Y + 130,
                            "M!h6")
            break


nearLowObsColor = QColor(255, 0, 0)
nearWire5Color = QColor(255, 153, 0)
nearWireColor = QColor(255, 255, 0)
nearVlineColor = QColor(0, 0, 255)
nearVlineWireColor = QColor(0, 0, 0)

def drawNearObs(qp, data):

    hasVlineWire = False
    for pt in data.points:

        if pt.v & 32 != 0:
            qp.setPen(QPen(nearVlineWireColor, 1))   # vline wire
            hasVlineWire = True
        elif pt.v & 16 != 0:
            qp.setPen(QPen(nearVlineColor, 1))  # vline
        elif pt.v & 8 != 0:
            qp.setPen(QPen(nearWireColor, 1))  # wire
        elif pt.v & 4 != 0:
            qp.setPen(QPen(nearWire5Color, 1))    # wire 5mm
        elif pt.v & 2 != 0:
            qp.setPen(QPen(nearLowObsColor, 1))   # 13mm

        qp.drawRect(ROBOT_X + pt.x, ROBOT_Y + pt.y, 2, 2)

    if hasVlineWire:
        print("hasVlineWire")


def drawObs(qp, data, obsList, color, name):

    for i in range(len(obsList) - 1, -1, -1):
        if data.timestamp - 200 < obsList[i].timestamp <= data.timestamp:
            qp.setPen(QPen(color, 1))
            for pt in obsList[i].points:
                qp.drawRect(ROBOT_X + pt.x, ROBOT_Y + pt.y, 2, 2)
            print("{} Time: {} ptsSize: {}".format(name, obsList[i].timestamp, len(obsList[i].points)))
            break


newLowObsColor = QColor(204, 51, 51)
newWire5Color = QColor(204, 143, 51)
newWireColor = QColor(204, 204, 51)
newVlineColor = QColor(68, 68, 187)
newVlineSpaceColor = QColor(255, 255, 255)
highObsColor = QColor(0, 255, 0)
allNearObsColor = QColor(200, 200, 200)

def drawNewLowObs(qp, data):

    global newLowObsList

    drawObs(qp, data, newLowObsList, newLowObsColor, "newLowObs")   # 13mm


def drawNewProbableWireObs(qp, data):

    global newProbableWireList

    drawObs(qp, data, newProbableWireList, newWire5Color, "newWire5mm")   # wire 5mm


def drawNewLooseWireObs(qp, data):

    global newLooseWireObsList

    drawObs(qp, data, newLooseWireObsList, newWireColor, "newWire")   # wire


def drawNewVlineObs(qp, data):

    global newVlineObsList

    drawObs(qp, data, newVlineObsList, newVlineColor, "newVlineObs")   # vline obs


def drawNewVlineSpace(qp, data):

    global newVlineSpaceList

    drawObs(qp, data, newVlineSpaceList, newVlineSpaceColor, "newVlineSpace")   # vline space


def drawHighObs(qp, data):

    global highObsList

    drawObs(qp, data, highObsList, highObsColor, "newHighObs")
    

def drawAllNearObs(qp, data):

    global allNearObsList

    drawObs(qp, data, allNearObsList, allNearObsColor, "allNearObs")



def drawRobotSide(qp, data):

    qp.setPen(QPen(QColor(0, 255, 0), 2))
    qp.drawRect(ROBOT_SIDE_X, ROBOT_SIDE_Y, ROBOT_SIDE_WIDTH, ROBOT_SIDE_HEIGHT)



def splitObs():

    global newObsList
    global newLowObsList
    global newProbableWireList

    newLowObsList = []
    newProbableWireList = []
    for i in range(len(newObsList)):
        ts = newObsList[i].timestamp
        points = newObsList[i].points
        lowObsPoints = []
        probableWirePoints = []
        for pt in points:
            if pt.v == 1:
                lowObsPoints.append(pt)
            elif pt.v == 2:
                probableWirePoints.append(pt)

        newLowObsList.append(TimeAndPoints(ts, lowObsPoints))
        newProbableWireList.append(TimeAndPoints(ts, probableWirePoints))
        if len(probableWirePoints) > 0:
            print(ts)


def drawColor(qp, pos1x, pos1y, name, pos2x, pos2y, color):

    qp.setPen(QPen(Colors.DefaultTextColor, 1))
    qp.drawText(pos1x, pos1y, name)
    # qp.setPen(QPen(color, 1))
    qp.fillRect(pos2x, pos2y, 300, 10, color)


def drawColorTable(qp, data):

    drawColor(qp, 2000, 100, "nearObs-lowObs", 2150, 90, nearLowObsColor)
    drawColor(qp, 2000, 120, "newObs-lowObs", 2150, 110, newLowObsColor)
    drawColor(qp, 2000, 140, "nearObs-wire", 2150, 130, nearWireColor)
    drawColor(qp, 2000, 160, "newObs-wire", 2150, 150, newWireColor)
    drawColor(qp, 2000, 180, "nearObs-wire5mm", 2150, 170, nearWire5Color)
    drawColor(qp, 2000, 200, "newObs-wire5mm", 2150, 190, newWire5Color)
    drawColor(qp, 2000, 220, "nearObs-vline", 2150, 210, nearVlineColor)
    drawColor(qp, 2000, 240, "nearObs-vline-wire", 2150, 230, nearVlineWireColor)
    drawColor(qp, 2000, 260, "newObs-vline", 2150, 250, newVlineColor)
    drawColor(qp, 2000, 280, "newObs-vlinespace", 2150, 270, newVlineSpaceColor)
    drawColor(qp, 2000, 300, "newObs-highObs", 2150, 290, highObsColor)



if __name__ == '__main__':

    app = QApplication(sys.argv)

    dirOpener = DirectoryOpener(None, "LowObsMapPlayer")
    dirName = dirOpener.getPath()

    print(ColorControl.BrFgGreen)
    print(f"DirPath: {dirName}")

    navNormalFile = dirName + "/NAV_normal_m.log"
    print(f"NavNormalFile: {navNormalFile}")

    tc = TimeCost()
    parser = NavNormalParser(navNormalFile)

    parser.parse({NavNormalTypes.LowObsMapNearObs : nearObsList,
                  NavNormalTypes.LowObsMapNewObs : newObsList,
                  NavNormalTypes.LowObsMapNewLooseWireObs : newLooseWireObsList,
                  NavNormalTypes.LowObsMapNewVlineObs : newVlineObsList,
                  NavNormalTypes.LowObsMapNewVlineSpace : newVlineSpaceList,
                  NavNormalTypes.LowObsMapNewVlineData : vlineList,
                  NavNormalTypes.LowObsMapNewHighObs : highObsList})

    # data = parser.getLowObsPoints()
    # newObsList = parser.getNewObs()
    splitObs()
    # newLooseWireObsList = parser.getNewLooseWireObs()
    # newVlineObsList = parser.getNewVlineObs()
    # newVlineSpaceList = parser.getNewVlineSpace()
    # highObsList = parser.getHighObs()
    # vlineList = parser.getVLineData()
    # allNearObsList = parser.getAllNearObs()

    print("  open time cost: {}".format(tc.countDown()))

    # bin10File = dirName + "/NAV_binId10.log"
    # print(f"Bin10File: {bin10File}")
    # bin10Parser = Bin10Parser(bin10File)
    #
    # print("  open time cost: {}".format(tc.countDown()))

    print("haha {}".format(len(newObsList)))
    print("haha2 {}".format(len(newLooseWireObsList)))
    print("haha3 {}".format(len(highObsList)))

    print("record count: {}".format(len(nearObsList)))
    print(ColorControl.End)

    ex = ObstaclePlayer(nearObsList, Point2D(ROBOT_X, ROBOT_Y))
    # ex.addCustomFunction(printInfo, 1)
    ex.addCustomFunction(drawColorTable, -100)
    ex.addCustomFunction(drawNearRange, -1)
    # ex.addCustomFunction(drawExtra, 2)
    ex.addCustomFunction(drawOccupy, 1)
    ex.addCustomFunction(drawAllNearObs, 2)

    ex.addCustomFunction(drawNewLowObs, 4)
    ex.addCustomFunction(drawHighObs, 5)
    ex.addCustomFunction(drawNewLooseWireObs, 6)
    ex.addCustomFunction(drawNewProbableWireObs, 7)


    ex.addCustomFunction(drawNewVlineSpace, 8)
    ex.addCustomFunction(drawNewVlineObs, 9)

    ex.addCustomFunction(drawNearObs, 10)



    ex.addCustomFunction(drawRobotSide, 20)
    ex.addCustomFunction(drawVLineData, 21)

    sys.exit(app.exec_())
