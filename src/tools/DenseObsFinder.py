import queue

import cv2
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMessageBox, QInputDialog, QApplication, QFileDialog, QCheckBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QBasicTimer, QPoint, Qt, QSettings, QRect
import numpy as np
import sys, math
from datetime import datetime
import time

from src.utils import GridCanvas, GridType, GridMapPPM
from src.geometry import SimpleRect
from src.algo import GraphicAlgo




class DenseObsFinder(GridCanvas, GridType, GraphicAlgo):

    NarrowCost = 100
    # NarrowCost = 0
    BUBBLE_R = 5
    POP_VALUE = -2
    # NearObsCost = [10000000, 1000000, 100000, 10000, 100, 1, 0]
    NearObsCost = [1000000000000, 1000000000000, 10000, 10, 1, 0, 0]
    # NearObsCost = [100000000000000, 100000000000000, 1000000, 1000, 100, 0, 0]
    NearCornerCost = [12800, 6400, 3200, 1600, 800, 400, 300, 200, 100, 50, 0]
    SimilarMask = {0x01: 0x83, 0x02: 0x07, 0x04: 0x0E, 0x08: 0x1C,
                    0x10: 0x38, 0x20: 0x70, 0x40: 0xE0, 0x80: 0xC1}
    # OppositeMask = {0x01: 0x38, 0x02: 0x70, 0x04: 0xE0, 0x08: 0xC1,
    #                 0x10: 0x83, 0x20: 0x07, 0x40: 0x0E, 0x80: 0x1C}
    OppositeMask = {0x01: 0x380, 0x02: 0x700, 0x04: 0xE00, 0x08: 0x1C00,
                    0x10: 0x3800, 0x20: 0x7000, 0x40: 0xE000, 0x80: 0xC001,
                    0x100: 0x8003, 0x200: 0x07, 0x400: 0x0E, 0x800: 0x1C,
                    0x1000: 0x38, 0x2000: 0x70, 0x4000: 0xE0, 0x8000: 0x1C0}
    HasOppositeMask = []

    def __init__(self):

        super(DenseObsFinder, self).__init__()

        self.initData()

        self.checkBox = QCheckBox('UseNarrowCost', self)
        self.checkBox.move(30, 80)
        self.checkBox.stateChanged.connect(self.shouldUseNarrowCost)

        self.checkBox2 = QCheckBox('ShowConvexHull', self)
        self.checkBox2.move(30, 100)
        self.checkBox2.stateChanged.connect(self.shouldShowConvex)



        self.checkBox3 = QCheckBox('ShowAuxPoint', self)
        self.checkBox3.move(30, 120)
        self.checkBox3.stateChanged.connect(self.shouldShowAux)

        self.checkBox4 = QCheckBox('ShowContours', self)
        self.checkBox4.move(30, 140)
        self.checkBox4.stateChanged.connect(self.shouldShowContours)

        self.checkBox5 = QCheckBox('ShowDense', self)
        self.checkBox5.move(30, 160)
        self.checkBox5.stateChanged.connect(self.shouldShowDense)

        self.initUI('DenseObsFinder')



    def shouldUseNarrowCost(self):

        self.useNarrowCost = self.checkBox.isChecked()
        print('useNarrowCost {}'.format(self.useNarrowCost))

    def shouldShowConvex(self):

        self.showConvexHull = self.checkBox2.isChecked()
        self.update()

    def shouldShowAux(self):

        self.showAuxPoint = self.checkBox3.isChecked()
        self.update()

    def shouldShowContours(self):

        self.showContours = self.checkBox4.isChecked()
        self.update()

    def shouldShowDense(self):

        self.showDense = self.checkBox5.isChecked()
        self.update()


    def initData(self):

        if len(self.HasOppositeMask) == 0:
            self.HasOppositeMask.append(False)
            for i in range(1, 65536):
                v = False
                for mask, opposite in self.OppositeMask.items():
                    if (i & mask) != 0 and (i & opposite) != 0:
                        v = True
                        break
                self.HasOppositeMask.append(v)

        self.map = GridMapPPM()

        self.useNarrowCost = False
        self.showConvexHull = False
        self.showAuxPoint = False
        self.showContours = False
        self.showDense = False

        self.nearObsMap = None
        self.nearObsVec = None
        self.nearCornerMap = None

        self.mouseDown = False
        self.mousePosBeg = QPoint(-1, -1)
        self.mousePosEnd = QPoint(-1, -1)

        self.data = None
        self.par = None
        self.found = False
        self.fastFound = False
        self.planning = False
        self.fastPath = None
        self.simplePath = None

        self.chairConvex = None
        self.chairContours = None
        self.obsCenter = set()
        self.tmpMap = None

        self.smallObsPts = []




    def paintObjects(self):

        mapData = self.map.mapData

        for x in range(0, self.map.mapWidth):
            for y in range(0, self.map.mapHeight):
                if self.smallObsPts[x][y] == 1:
                    self.drawPoint(x, y, QColor(255, 255, 0))
                if self.showDense and self.tmpMap[x][y] == 1:
                    self.drawPoint(x, y, self.DefaultObsCenterColor)
                elif self.showAuxPoint and (x, y) in self.obsCenter:
                    self.drawPoint(x, y, self.DefaultObsCenterColor)
                elif mapData[x][y] != self.DEFAULT_VALUE:
                    if mapData[x][y] == self.OBS_VALUE:
                        self.drawPoint(x, y, self.DefaultObsColor)
                    elif self.showAuxPoint and mapData[x][y] == self.NARROW_VALUE:
                        self.drawPoint(x, y, self.DefaultNarrowColor)
                    elif self.showAuxPoint:
                        self.drawPoint(x, y, self.DefaultVisitColor)
                else:
                    if self.showAuxPoint and self.HasOppositeMask[self.nearObsVec[x][y]]:
                        self.drawPoint(x, y, self.DefaultNearCornerColor)
                    # if self.nearCornerMap[x][y] >= 0:
                    #     self.drawPoint(x, y, self.DefaultNearCornerColor)
                    # elif self.nearObsMap[x][y] >= 0:
                    #     self.drawPoint(x, y, self.DefaultNearObsColor)

                # if self.data is not None:
                #     if self.data[x][y] == -1:
                #         self.drawPoint(x, y, self.DefaultObsColor)
                #     elif self.data[x][y] == -2:
                #         self.drawPoint(x, y, self.DefaultPopColor)

        self.drawLabel()
        if self.mouseDown:
            self.drawPoints(self.getBresenhamPoints8(self.mousePosBeg, self.mousePosEnd), self.DefaultVisitColor)
        self.drawPoint(self.mousePosBeg.x(), self.mousePosBeg.y(), self.DefaultStartColor)
        self.drawPoint(self.mousePosEnd.x(), self.mousePosEnd.y(), self.DefaultGoalColor)

        if self.showConvexHull:
            self.drawChairConvex()

        if self.showContours:
            self.drawChairContours()

        if self.found:
            self.drawPath()
            # self.drawSplinePath()


    def drawChairConvex(self):

        if self.chairConvex and len(self.chairConvex) > 0:
            for hull in self.chairConvex:
                pointCnt = len(hull)
                for i in range(pointCnt):
                    j = 0 if i == pointCnt - 1 else i + 1
                    self.drawConn(hull[i][0][0], hull[i][0][1], hull[j][0][0], hull[j][0][1], self.DefaultHullColor)

    def drawChairContours(self):

        if self.chairContours and len(self.chairContours) > 0:
            for contour in self.chairContours:
                pointCnt = len(contour)
                for i in range(pointCnt):
                    j = 0 if i == pointCnt - 1 else i + 1
                    self.drawConn(contour[i][0][1], contour[i][0][0], contour[j][0][1], contour[j][0][0], self.DefaultContourColor)

    def drawLabel(self):
        self.qp.setPen(self.DefaultTextColor)
        self.qp.drawText(50, 50, "pos {} {} -> {} {}".format(self.mousePosBeg.x(), self.mousePosBeg.y(),
                                                             self.mousePosEnd.x(), self.mousePosEnd.y()))


    def drawPath(self):

        path = self.fastPath if self.fastPath is not None else self.simplePath

        for i in range(1, len(path)):
            self.drawConn(path[i-1].x(), path[i-1].y(),
                          path[i].x(), path[i].y(),
                          self.DefaultConnColor)


    def drawSplinePath(self):

        x = self.mousePosEnd.x()
        y = self.mousePosEnd.y()
        sx = self.mousePosBeg.x()
        sy = self.mousePosBeg.y()

        pts = [(x, y)]

        while x != sx or y != sy:
            px, py = self.par[x][y]
            x, y = px, py
            pts.append((x, y))

        opts = DenseObsFinder.bspline(pts, 200)
        for i in range(1, len(opts)):
            self.drawConn(opts[i-1][0], opts[i-1][1], opts[i][0], opts[i][1], self.DefaultConnColor)


    def mousePressEvent(self, e):
        self.mousePosBeg = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.mouseDown = True
        pass
        # QMessageBox.question(self, 'Message',
        #                     "mouse pos x = {}, y = {}".format(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize), QMessageBox.Ok)


    def mouseMoveEvent(self, e):
        self.mousePosEnd = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.update()
        # QMessageBox.question(self, 'Message',
        #                      "mouse pos x = {}, y = {}".format(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize), QMessageBox.Ok)


    def mouseReleaseEvent(self, e):
        self.mousePosEnd = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.mouseDown = False
        # for pt in self.getBresenhamPoints8(self.mousePosBeg, self.mousePosEnd):
        #     self.mapData[pt.x()][pt.y()] = -1
        self.update()
        self.search()
        print("nearObs {} {} {} {}".format(self.mousePosEnd.x(), self.mousePosEnd.y(),
                                           self.map.mapData[self.mousePosEnd.x()][self.mousePosEnd.y()],
                                        self.nearObsMap[self.mousePosEnd.x()][self.mousePosEnd.y()]))
        # QMessageBox.question(self, 'Message',
        #                      "mouse pos x = {}, y = {}".format(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize), QMessageBox.Ok)


    def keyPressEvent(self, e):
        if QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_S:
            self.map.saveData(self.getSaveFileName())

        elif QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_O:
            self.map.loadData(self.getOpenFileName())
            # self.updateNearObs()
            self.updateNearObs3()
            self.updateCorners()
            self.updateChairConvex()

        elif e.key() == Qt.Key_Backspace:
            self.clearSearch()
            self.update()


    def roundingPoint(self, x, y, r, handle):
        mapWidth = self.map.mapWidth
        mapHeight = self.map.mapHeight
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                nx = x + dx
                ny = y + dy
                if not (0 <= nx < mapWidth and 0 <= ny < mapHeight):
                    continue
                dr = math.sqrt(dx * dx + dy * dy)
                if dr <= r:
                    handle(x, y, nx, ny, dr)



    def updateNearObs(self):

        mapData = self.map.mapData
        mapWidth = self.map.mapWidth
        mapHeight = self.map.mapHeight

        self.nearObsMap = np.zeros((mapWidth, mapHeight), dtype=int)
        self.nearObsMap.fill(-1)
        self.nearObsVec = np.zeros((mapWidth, mapHeight), dtype=int)

        def getVec(xobs, yobs, x, y):
            if xobs == x and yobs == y:
                return 0
            idx = round(math.atan2(yobs - y, xobs - x) / (math.pi / 4))
            if idx < 0:
                idx = idx + 8
            return 0x1 << idx


        def handleNearObs(xobs, yobs, x, y, r):
            rr = round(r)
            if self.nearObsMap[x][y] == -1 or self.nearObsMap[x][y] > rr:
                self.nearObsMap[x][y] = rr
            self.nearObsVec[x][y] = (self.nearObsVec[x][y] | getVec(xobs, yobs, x, y))

        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if mapData[x][y] == self.OBS_VALUE:
                    self.roundingPoint(x, y, self.BUBBLE_R, handleNearObs)


    def updateNearObs2(self):

        mapData = self.map.mapData
        mapWidth = self.map.mapWidth
        mapHeight = self.map.mapHeight

        nearObsMap = np.zeros((mapWidth, mapHeight), dtype=float)
        nearObsMap.fill(1000)

        self.nearObsVec = np.zeros((mapWidth, mapHeight), dtype=int)

        def getVec(xobs, yobs, x, y):
            if xobs == x and yobs == y:
                return 0
            idx = round(math.atan2(yobs - y, xobs - x) / (math.pi / 4))
            if idx < 0:
                idx = idx + 8
            return 0x1 << idx

        def handleNearObs(xobs, yobs, x, y, v):
            if x < 0 or x >= mapWidth or y < 0 or y >= mapHeight:
                return

            if nearObsMap[x][y] > v:
                nearObsMap[x][y] = v

            relVec = getVec(xobs, yobs, x, y)
            if nearObsMap[xobs][yobs] == 0 or (self.nearObsVec[xobs][yobs] & self.SimilarMask[relVec]) != 0:
                self.nearObsVec[x][y] = (self.nearObsVec[x][y] | relVec)
            # print('{} {} {} {:#X} {} {} {} {:#X}'.format(
            #     xobs, yobs, nearObsMap[xobs][yobs], self.nearObsVec[xobs][yobs],
            #     x, y, nearObsMap[x][y], self.nearObsVec[x][y]))

        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if mapData[x][y] == self.OBS_VALUE:
                    nearObsMap[x][y] = 0

        sqrt2 = math.sqrt(2)

        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if 0 <= nearObsMap[x][y] < self.BUBBLE_R:
                    handleNearObs(x, y, x + 1, y, nearObsMap[x][y] + 1)
                    handleNearObs(x, y, x - 1, y + 1, nearObsMap[x][y] + sqrt2)
                    handleNearObs(x, y, x, y + 1, nearObsMap[x][y] + 1)
                    handleNearObs(x, y, x + 1, y + 1, nearObsMap[x][y] + sqrt2)

        # print('=======================')

        for x in range(mapWidth - 1, -1, -1):
            for y in range(mapHeight - 1, -1, -1):
                if 0 <= nearObsMap[x][y] < self.BUBBLE_R:
                    handleNearObs(x, y, x - 1, y, nearObsMap[x][y] + 1)
                    handleNearObs(x, y, x + 1, y - 1, nearObsMap[x][y] + sqrt2)
                    handleNearObs(x, y, x, y - 1, nearObsMap[x][y] + 1)
                    handleNearObs(x, y, x - 1, y - 1, nearObsMap[x][y] + sqrt2)

        self.nearObsMap = np.zeros((mapWidth, mapHeight), dtype=int)
        self.nearObsMap.fill(-1)
        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if nearObsMap[x][y] < 1000:
                    self.nearObsMap[x][y] = round(nearObsMap[x][y])


    def updateNearObs3(self):

        t1 = time.time()

        mapData = self.map.mapData
        mapWidth = self.map.mapWidth
        mapHeight = self.map.mapHeight

        nearObsMap = np.zeros((mapWidth, mapHeight), dtype=float)
        nearObsMap.fill(1000)
        nearObsMap1 = np.zeros((mapWidth, mapHeight), dtype=float)
        nearObsMap1.fill(1000)
        nearObsMap2 = np.zeros((mapWidth, mapHeight), dtype=float)
        nearObsMap2.fill(1000)

        parentX1 = np.zeros((mapWidth, mapHeight), dtype=int)
        parentY1 = np.zeros((mapWidth, mapHeight), dtype=int)
        parentX2 = np.zeros((mapWidth, mapHeight), dtype=int)
        parentY2 = np.zeros((mapWidth, mapHeight), dtype=int)

        self.nearObsVec = np.zeros((mapWidth, mapHeight), dtype=int)

        t2 = time.time()

        # 圆周周分为 16 块，返回某块对应的 mask
        def getVec(xobs, yobs, x, y):
            if xobs == x and yobs == y:
                return 0
            tmp = math.atan2(yobs - y, xobs - x) / (math.pi / 8)
            if tmp < 0:
                tmp = tmp + 16
            idx = int(tmp)
            return 0x1 << idx

        # 用 (xobs,yobs) 来更新 (x,y) 的 bubble 值
        # nearObsMap 存的是全部方向过来的 bubble 值
        # nearObsMap1 存的是右上方向过来的 bubble 值
        # nearObsMap2 存的是左下方向过来的 bubble 值
        # 确保找到的是源头的 obs，所以用了 parentX1 和 parentY1 来存储
        # 记录所有最小值的来源的方向（小表示离 obs 近）
        def handleNearObs(xobs, yobs, x, y, d, rightTop):
            if x < 0 or x >= mapWidth or y < 0 or y >= mapHeight:
                return

            v = nearObsMap[xobs][yobs] + d
            if nearObsMap[x][y] > v and v < self.BUBBLE_R:
                nearObsMap[x][y] = v

            relVec = 0
            if rightTop:
                v = nearObsMap1[xobs][yobs] + d
                if nearObsMap1[x][y] >= v:
                    nearObsMap1[x][y] = v
                    parentX1[x][y] = parentX1[xobs][yobs]
                    parentY1[x][y] = parentY1[xobs][yobs]
                    if nearObsMap1[parentX1[x][y]][parentY1[x][y]] != 0:
                        print('error rightTop {} {} {} {}'.format(xobs, yobs, x, y))
                        return
                    relVec = getVec(parentX1[x][y], parentY1[x][y], x, y)
            else:
                v = nearObsMap2[xobs][yobs] + d
                if nearObsMap2[x][y] >= v:
                    nearObsMap2[x][y] = v
                    parentX2[x][y] = parentX2[xobs][yobs]
                    parentY2[x][y] = parentY2[xobs][yobs]
                    if nearObsMap2[parentX2[x][y]][parentY2[x][y]] != 0:
                        print('error leftbottom {} {} {} {}'.format(xobs, yobs, x, y))
                        return
                    relVec = getVec(parentX2[x][y], parentY2[x][y], x, y)

            # relVec = getVec(xobs, yobs, x, y)
            # if nearObsMap[xobs][yobs] == 0 or (self.nearObsVec[xobs][yobs] & self.SimilarMask[relVec]) != 0:
            # if x == 35 and y == 95:
            #     if rightTop:
            #         print("part 35,95 from {},{}, {:#X}".format(parentX1[x][y], parentY1[x][y], relVec))
            #     else:
            #         print("part 35,95 from {},{}, {:#X}".format(parentX2[x][y], parentY2[x][y], relVec))

            self.nearObsVec[x][y] = (self.nearObsVec[x][y] | relVec)
            # print('{} {} {} {:#X} {} {} {} {:#X}'.format(
            #     xobs, yobs, nearObsMap1[xobs][yobs] if rightTop else nearObsMap2[xobs][yobs], self.nearObsVec[xobs][yobs],
            #     x, y, nearObsMap1[x][y] if rightTop else nearObsMap2[x][y], self.nearObsVec[x][y]))

        # 对 obs 进行 BFS 搜索，最大范围是 5x5，聚为一类
        clusterIndex = 0
        clusterGroup = np.zeros((mapWidth, mapHeight), dtype=int)
        clusterCenter = [[0, 0]]
        clusterSize = [0]
        visit = np.zeros((mapWidth, mapHeight), dtype=int)
        sumX = 0
        sumY = 0
        cnt = 0
        def bfsObs(x, y, visit, box):
            nonlocal sumX
            nonlocal sumY
            nonlocal cnt
            nonlocal clusterIndex
            nonlocal clusterGroup
            nonlocal mapData
            nonlocal mapWidth
            nonlocal mapHeight

            if x < 0 or x >= mapWidth or y < 0 or y >= mapHeight:
                # print("err {} {} {} {}".format(x, y, mapWidth, mapHeight))
                return

            if mapData[x][y] == self.OBS_VALUE and visit[x][y] == 0\
                    and box.widthWithX(x) <= 5 and box.heightWithY(y) <= 5:
                cnt += 1
                sumX += x
                sumY += y
                visit[x][y] = 1
                box.expand(x, y)
                clusterGroup[x][y] = clusterIndex
                for nx in range(x - 1, x + 2):
                    for ny in range(y - 1, y + 2):
                        if nx == x and ny == y:
                            continue
                        bfsObs(nx, ny, visit, box)

        self.obsCenter = set()
        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                parentX1[x][y] = x
                parentY1[x][y] = y
                parentX2[x][y] = x
                parentY2[x][y] = y
                if mapData[x][y] == self.OBS_VALUE:
                    nearObsMap[x][y] = 0
                    nearObsMap1[x][y] = 0
                    nearObsMap2[x][y] = 0
                    if visit[x][y] == 0:
                        sumX = sumY = cnt = 0
                        clusterIndex += 1
                        box = SimpleRect(x, y, x, y)
                        bfsObs(x, y, visit, box)
                        cx, cy = round(sumX / cnt), round(sumY / cnt)
                        clusterCenter.append([cx, cy])
                        self.obsCenter.add((cx, cy))
                        clusterSize.append(cnt)

        t3 = time.time()

        sqrt2 = math.sqrt(2)

        # 两次全遍历，更新两个主方向的值

        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if 0 <= nearObsMap1[x][y] < self.BUBBLE_R:
                    handleNearObs(x, y, x + 1, y - 1, sqrt2, True)
                    handleNearObs(x, y, x + 1, y, 1, True)
                    handleNearObs(x, y, x, y + 1, 1, True)
                    handleNearObs(x, y, x + 1, y + 1, sqrt2, True)

        for y in range(0, mapHeight):
            for x in range(0, mapWidth):
                if 0 <= nearObsMap1[x][y] < self.BUBBLE_R:
                    handleNearObs(x, y, x - 1, y + 1, sqrt2, True)

        # print('=======================')

        for x in range(mapWidth - 1, -1, -1):
            for y in range(mapHeight - 1, -1, -1):
                if 0 <= nearObsMap2[x][y] < self.BUBBLE_R:
                    handleNearObs(x, y, x, y - 1, 1, False)
                    handleNearObs(x, y, x - 1, y + 1, sqrt2, False)
                    handleNearObs(x, y, x - 1, y, 1, False)
                    handleNearObs(x, y, x - 1, y - 1, sqrt2, False)

        for y in range(mapHeight - 1, -1, -1):
            for x in range(mapWidth - 1, -1, -1):
                if 0 <= nearObsMap2[x][y] < self.BUBBLE_R:
                    handleNearObs(x, y, x + 1, y - 1, sqrt2, False)

        t4 = time.time()

        self.nearObsMap = np.zeros((mapWidth, mapHeight), dtype=int)
        self.nearObsMap.fill(-1)
        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                # if (abs(x - 35) < 10 and abs(y - 95) < 10):
                #     print("obsVec {},{} {:#X} {},{} {},{}".format(x, y, self.nearObsVec[x][y], parentX1[x][y], parentY1[x][y], parentX2[x][y], parentY2[x][y]))

                if self.HasOppositeMask[self.nearObsVec[x][y]]:
                    px1, py1 = parentX1[x][y], parentY1[x][y]
                    px2, py2 = parentX2[x][y], parentY2[x][y]
                    parentDist = math.hypot(px2 - px1, py2 - py1)

                    if mapData[px1][py1] == self.OBS_VALUE and mapData[px2][py2] == self.OBS_VALUE:
                        cx1, cy1 = clusterCenter[clusterGroup[px1][py1]]
                        cx2, cy2 = clusterCenter[clusterGroup[px2][py2]]

                        narrowCnt = 0
                        for pt in GraphicAlgo.getBresenhamPoints8(QPoint(cx1, cy1),
                                                           QPoint(cx2, cy2)):
                            if mapData[pt.x()][pt.y()] != self.OBS_VALUE:
                                narrowCnt += 1

                        if parentDist <= 9 and narrowCnt <= 9:
                            for pt in GraphicAlgo.getBresenhamPoints4(QPoint(cx1, cy1),
                                                               QPoint(cx2, cy2)):
                                if mapData[pt.x()][pt.y()] != self.OBS_VALUE:
                                    mapData[pt.x()][pt.y()] = self.NARROW_VALUE
                                    # print("narrow {},{} from {},{} -> {},{}".format(pt.x(), pt.y(), cx1, cy1, cx2, cy2))

                if nearObsMap[x][y] < 1000:
                    self.nearObsMap[x][y] = round(nearObsMap[x][y])

        t5 = time.time()

        print("width: {} height: {}".format(mapWidth, mapHeight))
        print("init: {}".format(t2 - t1))
        print("groupObs: {}".format(t3 - t2))
        print("2 bubble: {}".format(t4 - t3))
        print("draw narrow: {}".format(t5 - t4))




    def updateChairConvex(self):

        t1 = time.time()

        mapData = self.map.mapData
        mapWidth = self.map.mapWidth
        mapHeight = self.map.mapHeight

        self.smallObsPts = np.zeros((mapWidth, mapHeight), dtype=np.int8)
        visit = np.zeros((mapWidth, mapHeight), dtype=np.int8)

        clusterIndex = 0
        clusterGroup = np.zeros((mapWidth, mapHeight), dtype=int)
        clusterSize = [0]
        clusterSmallBox = [False]
        cnt = 0

        t2 = time.time()

        def bfsObs(x, y, box):
            nonlocal visit
            nonlocal cnt
            nonlocal clusterIndex
            nonlocal clusterGroup
            nonlocal mapData
            nonlocal mapWidth
            nonlocal mapHeight

            if x < 0 or x >= mapWidth or y < 0 or y >= mapHeight:
                return

            if mapData[x][y] == self.OBS_VALUE and visit[x][y] == 0:
                box.expand(x, y)
                cnt += 1
                visit[x][y] = 1
                clusterGroup[x][y] = clusterIndex
                for nx in range(x - 1, x + 2):
                    for ny in range(y - 1, y + 2):
                        if nx == x and ny == y:
                            continue
                        bfsObs(nx, ny, box)

        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if mapData[x][y] == self.OBS_VALUE:
                    if visit[x][y] == 0:
                        cnt = 0
                        clusterIndex += 1
                        box = SimpleRect(x, y, x, y)
                        bfsObs(x, y, box)
                        clusterSize.append(cnt)
                        clusterSmallBox.append(box.height() <= 4 and box.width() <= 4)

        t3 = time.time()

        def smallObs(x, y):
            rv = mapData[x][y] == self.OBS_VALUE and clusterSize[clusterGroup[x][y]] <= 10 and clusterSmallBox[clusterGroup[x][y]]
            if rv:
                self.smallObsPts[x][y] = 1
            return rv
            # return mapData[x][y] == self.OBS_VALUE

        def bfsChairs(x, y, pts):
            nonlocal visit
            nonlocal mapData
            nonlocal mapWidth
            nonlocal mapHeight

            if x < 0 or x >= mapWidth or y < 0 or y >= mapHeight:
                return

            if visit[x][y] == 0:
                if mapData[x][y] == self.NARROW_VALUE or smallObs(x, y):
                    visit[x][y] = 1
                    pts.append([float(x), float(y)])
                    for nx in range(x - 5, x + 6):
                        for ny in range(y - 5, y + 6):
                            if nx == x and ny == y:
                                continue
                            bfsChairs(nx, ny, pts)

        self.tmpMap = np.zeros((mapWidth, mapHeight), dtype=np.uint8)
        self.chairConvex = []
        self.chairContours = []
        visit.fill(0)
        image = np.zeros((mapWidth, mapHeight), dtype=np.uint8)
        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if visit[x][y] == 0 and smallObs(x, y):
                    pts = []
                    bfsChairs(x, y, pts)
                    # print("start: {} {}, size: {}".format(x, y, len(pts)))
                    convexPoints = cv2.convexHull(np.asarray(pts, dtype=int))
                    area = cv2.contourArea(convexPoints)
                    # print(area)
                    if area > 20:
                        self.chairConvex.append(convexPoints)
                    # print("end: {} {}, area: {} size: {}".format(x, y, area, len(convexPoints)))

                    image.fill(0)
                    for pt in pts:
                        for x1 in range(int(pt[0]) - 2, int(pt[0]) + 3):
                            for y1 in range(int(pt[1]) - 2, int(pt[1]) + 3):
                                if x1 < 0 or x1 >= mapWidth or y1 < 0 or y1 >= mapHeight:
                                    continue
                                image[x1][y1] = 1
                                self.tmpMap[x1][y1] = 1
                    contours, _ = cv2.findContours(image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
                    cv2.fillPoly(self.tmpMap, contours, color=1)
                    # print("contour: {}".format(contours[0]))
                    area = cv2.contourArea(contours[0])
                    if area >= 30:
                        self.chairContours.append(contours[0])

        t4 = time.time()

        print("convex init: {}".format(t2 - t1))
        print("groupObs: {}".format(t3 - t2))
        print("dense: {}".format(t4 - t3))


    def updateCorners(self):

        mapData = self.map.mapData.astype(np.float32)
        mapWidth = self.map.mapWidth
        mapHeight = self.map.mapHeight

        self.nearCornerMap = np.zeros((mapWidth, mapHeight), dtype=int)
        self.nearCornerMap.fill(-1)

        corners = []
        def findCorner(xobs, yobs, x, y, r):
            if self.map.mapData[x][y] == self.OBS_VALUE:
                corners.append((x, y))

        def handleCorner(xobs, yobs, x, y, r):
            # rr = round(1000 - r * 100)
            # if self.nearCornerMap[x][y] < rr:
            #     self.nearCornerMap[x][y] = rr
            rr = round(r)
            if self.nearCornerMap[x][y] == -1 or self.nearCornerMap[x][y] > rr:
                self.nearCornerMap[x][y] = rr

        result = GraphicAlgo.cornerHarris(mapData, 2, 3, 0.04)
        pos = cv2.goodFeaturesToTrack(result, 0, 0.01, 10)
        for i in range(len(pos)):
            y = round(pos[i][0][0])
            x = round(pos[i][0][1])
            self.roundingPoint(x, y, 3, findCorner)

        # for x, y in corners:
        #     self.map.mapData[x][y] = self.CORNER_VALUE
        #     self.roundingPoint(x, y, 9, handleCorner)



    def f(self, g, x, y):

        return g + self.h(x, y)


    def h(self, x, y):

        dx = abs(x - self.mousePosEnd.x())
        dy = abs(y - self.mousePosEnd.y())

        return math.sqrt(dx * dx + dy * dy)


    def dataExpand(self, x, y, dist):

        if x < 0 or x >= self.MapWidth or y < 0 or y >= self.MapHeight\
                or self.data[x][y] < 0 or dist >= self.data[x][y]:
            return False
        self.data[x][y] = dist
        self.queue.put((self.f(dist, x, y), dist, x, y))
        return True


    def timerEvent(self, event):
        '''handles timer event'''

        if not self.planning:
            return

        offsets = [(-1, -1, math.sqrt(2)), (-1, 0, 1), (-1, 1, math.sqrt(2)),
                   (0, -1, 1), (0, 1, 1),
                   (1, -1, math.sqrt(2)), (1, 0, 1), (1, 1, math.sqrt(2))]

        mapWidth = self.map.mapWidth
        mapHeight = self.map.mapHeight

        if event.timerId() == self.timer.timerId():
            # self.drawRandomPoint()
            cnt = 0
            while not self.queue.empty():

                tp = self.queue.get()
                dist = tp[1]
                x = tp[2]
                y = tp[3]
                if x == self.mousePosEnd.x() and y == self.mousePosEnd.y():
                    self.found = True
                    self.planning = False
                    self.collectSimplePath()
                    QMessageBox.question(self, 'Message',
                                         "found goal, totalsearch = {}, dist = {}".format(self.totalSearch(), dist), QMessageBox.Ok)
                    break
                if dist == self.data[x][y]:
                    self.data[x][y] = self.POP_VALUE
                    for offset in offsets:
                        nx = x + offset[0]
                        ny = y + offset[1]
                        if nx < 0 or nx >= mapWidth or ny < 0 or ny >= mapHeight:
                            continue
                        # ndist = dist + offset[2] + self.NearObsCost[self.nearObsMap[nx][ny]] + self.NearCornerCost[self.nearCornerMap[nx][ny]]
                        ndist = dist + offset[2] + self.NearObsCost[self.nearObsMap[nx][ny]]
                        # if self.useNarrowCost and self.HasOppositeMask[self.nearObsVec[nx][ny]]:
                        if self.useNarrowCost and self.map.mapData[nx][ny] == self.NARROW_VALUE:
                            ndist = ndist + self.NarrowCost
                        # ndist = dist + offset[2] + self.NearObsCost[self.nearObsMap[nx][ny]] + self.nearCornerMap[nx][ny]
                        if self.dataExpand(nx, ny, ndist):
                            self.par[nx][ny] = (x, y)
                    cnt += 1
                    if cnt > 400:
                        break

            if self.queue.empty():
                self.planning = False
            self.update()

        else:
            super(DenseObsFinder, self).timerEvent(event)


    def fastSearch(self):

        nearObs = False
        def checkObs(xobs, yobs, x, y, r):
            nonlocal nearObs
            if self.nearObsMap[x][y] == 0:
                nearObs = True

        pts = self.getBresenhamPoints8(self.mousePosBeg, self.mousePosEnd)
        for pt in pts:
            self.roundingPoint(pt.x(), pt.y(), 3, checkObs)
            if nearObs:
                break

        if not nearObs:
            self.fastPath = pts
        return not nearObs


    def search(self):

        # if self.fastSearch():
        #     print('fast search ok')
        #     self.found = True
        #     self.update()
        #     return

        self.data = np.zeros((self.MapWidth, self.MapHeight))
        self.data.fill(np.inf)

        self.par = np.empty((self.map.mapWidth, self.map.mapHeight), dtype=tuple)
        self.par.fill((-1, -1))
        self.queue = queue.PriorityQueue()

        st = self.mousePosBeg
        stx = st.x()
        sty = st.y()

        self.data[stx][sty] = 0
        self.queue.put((self.f(0, stx, sty), 0, stx, sty))
        self.found = False
        self.planning = True


    def collectSimplePath(self):

        x = self.mousePosEnd.x()
        y = self.mousePosEnd.y()
        sx = self.mousePosBeg.x()
        sy = self.mousePosBeg.y()

        path = []
        path.append(QPoint(x, y))

        while x != sx or y != sy:
            px, py = self.par[x][y]
            x, y = px, py
            path.append(QPoint(x, y))

        path.reverse()

        #print(len(path))
        #self.simplePath = path
        self.simplePath = []
        lenp = len(path)
        i = 0
        next = 0
        while True:
            self.simplePath.append(path[i])

            #print(i)

            if i >= lenp - 1:
                break
            for j in range(i + 1, lenp):
                for pt in self.getBresenhamPoints8(path[i], path[j]):
                    if self.nearObsMap[pt.x()][pt.y()] >= 0 or self.nearCornerMap[pt.x()][pt.y()] >= 0:
                        next = j
                        break
                if next > i:
                    i = next if next == i + 1 else (next - 1)
                    break
                if j == lenp - 1:
                    i = j
                    break



    def totalSearch(self):
        return sum([1 if 0 <= x < np.inf else 0 for x in self.data.flat])


    def clearSearch(self):

        self.data = None
        self.par = None
        self.found = False
        self.fastFound = False
        self.planning = False
        self.fastPath = None
        self.simplePath = None


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = DenseObsFinder()
    sys.exit(app.exec_())
