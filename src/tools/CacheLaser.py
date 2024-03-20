from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QPoint, Qt, QRect, QSettings
import sys
import math

from src.utils import GridCanvas, Colors


class CacheLaser(GridCanvas):

    def __init__(self):

        super().__init__()

        self.initData()
        self.initUI('CacheLaser')

        self.setMouseTracking(True)

    def inBullet(self, bearing, range, dx):
        return (range * range + dx * dx - 2 * range * dx * math.cos(bearing)) < self.robotRwithGlue * self.robotRwithGlue

    def initData(self):

        self.mousePosEnd = QPoint(0, 0)

        self.robotX = 500
        self.robotY = 500
        self.robotR = 175
        self.robotRwithGlue = 178.5
        self.deltaX = 50
        self.redzoneR = self.robotRwithGlue + self.deltaX
        self.rightBrushXOffset = 92
        self.rightBrushYOffset = -113
        self.rightBrushR = 73
        self.lastX = 0
        self.lastY = 0
        self.lastRad = 0
        self.lastDeg = 0

        self.offsetX = -1000
        self.offsetY = 7400

        qSettings = QSettings()
        lastPath = qSettings.value("LastCacheLaserFilePath")
        filename, choosed = QFileDialog.getOpenFileName(self, 'Open file', lastPath)

        if not choosed:
            sys.exit(-1)

        qSettings.setValue("LastCacheLaserFilePath", filename)

        self.shadowPts = []
        self.rawPts = []
        with open(filename, mode='rt') as fp:
            for line in fp.readlines():
                data = line.split(" ")
                if data[1] == "slamPose":
                    pos_ts = int(data[0])
                    pos_x = float(data[2])
                    pos_y = float(data[3])
                    pos_theta = float(data[4])
                    self.lastX = pos_x
                    self.lastY = pos_y
                    self.lastRad = pos_theta
                    self.lastDeg = pos_theta * 180 / math.pi
                    # self.robotX = int(pos_x * 1000) - 800
                    # self.robotY = int(pos_y * 1000) + 6400
                elif data[1] == "rawLaser":
                    laser_ts = int(data[0])
                    count = int(data[4])
                    for i in range(count):
                        angle = float(data[i*3+5])
                        dist = float(data[i*3+6])
                        intensity = float(data[i*3+7])
                        if intensity > 0xFFF:
                            continue
                        dx = dist * math.cos(angle + pos_theta)
                        dy = dist * math.sin(angle + pos_theta)
                        px = pos_x + dx
                        py = pos_y + dy
                        self.rawPts.append([px, py])
                elif data[1] == "shadowLaser":
                    laser_ts = int(data[0])
                    count = int(data[4])
                    pts = []
                    for i in range(count):
                        angle = float(data[i * 3 + 5])
                        dist = float(data[i * 3 + 6])
                        intensity = float(data[i * 3 + 7])
                        if intensity > 0xFFF:
                            continue
                        dx = dist * math.cos(angle + pos_theta)
                        dy = dist * math.sin(angle + pos_theta)
                        px = pos_x + dx
                        py = pos_y + dy
                        self.shadowPts.append([px, py])


        self.robotX = int(self.lastX * 1000) + self.offsetX
        self.robotY = int(self.lastY * 1000) + self.offsetY

        print("shadow: ", self.shadowPts)
        print("raw: ", self.rawPts)

        # self.oldPts = oldPts.split(" ")
        # self.newPts = newPts.split(" ")
        #
        # validMinBearing = -60 / 180 * math.pi
        # validMaxBearing = 60 / 180 * math.pi
        #
        # for i in range(len(self.oldPts)):
        #     oldX, oldY = map(int, self.oldPts[i].split(","))
        #     newX, newY = map(int, self.newPts[i].split(","))
        #
        #     oldBearing = math.atan2(oldY, oldX)
        #     newBearing = math.atan2(newY, newX)
        #     estimatedBearing = (oldBearing + newBearing) / 2
        #     if math.fabs(estimatedBearing - oldBearing) > math.pi / 2:
        #         if estimatedBearing >= 0:
        #             estimatedBearing -= math.pi
        #         else:
        #             estimatedBearing += math.pi
        #
        #     if estimatedBearing < validMinBearing or estimatedBearing > validMaxBearing:
        #         continue
        #
        #     tp, toSegDist = self.getDistToSeg(oldX, oldY, newX, newY)
        #
        #     if tp == 1:
        #         continue
        #     elif tp == 2:
        #         bearing = estimatedBearing
        #     else: # tp == 3
        #         bearing = newBearing
        #
        #     if self.inBullet(bearing, toSegDist, self.deltaX):
        #         print("inbullet ", tp, toSegDist,
        #               oldX, oldY, oldBearing / math.pi * 180,
        #               newX, newY, newBearing / math.pi * 180,
        #               bearing / math.pi * 180
        #               )
        #
        #     elif toSegDist < self.redzoneR:
        #         print(tp, toSegDist,
        #               oldX, oldY, oldBearing / math.pi * 180,
        #               newX, newY, newBearing / math.pi * 180,
        #               bearing / math.pi * 180
        #              )
        #
        #     else:
        #         print("bad ", toSegDist,
        #               oldX, oldY, oldBearing / math.pi * 180,
        #               newX, newY, newBearing / math.pi * 180,
        #               bearing / math.pi * 180
        #               )

    def getDistToSeg(self, oldX, oldY, newX, newY):

        if (newX - oldX) * (0.0 - oldX) + (newY - oldY) * (0.0 - oldY) <= 0:
            return 1, math.hypot(oldX, oldY)

        if (oldX - newX) * (0.0 - newX) + (oldY - newY) * (0.0 - newY) <= 0:
            return 3, math.hypot(newX, newY)

        return 2, math.fabs((oldX - 0) * (newY - 0) - (newX - 0) * (oldY - 0) / ((newX - oldX) * (newX - oldX) + (newY - oldY) * (newY - oldY)))


    def drawLabel(self):

        self.qp.setPen(Colors.DefaultTextColor)
        dx = self.mousePosEnd.x() - self.robotX
        dy = self.mousePosEnd.y() - self.robotY
        range = math.hypot(dx, dy)
        bearing = math.atan2(dy, dx)
        self.qp.drawText(50, 50, "x: {} y: {}   range: {:.2f} bearing: {:.2f} | {:.2f}".format(dx, dy, range, bearing / math.pi * 180, bearing))

    def drawRay(self, x, y, deg, length, penColor, penWidth):

        self.qp.setPen(QPen(penColor, penWidth))
        rad = math.pi / 180 * deg
        self.qp.drawLine(x, y, x + length * math.cos(rad), y + length * math.sin(rad))

    def drawRobot(self, x, y, deg):

        rad = deg / 180 * math.pi
        c = math.cos(rad)
        s = math.sin(rad)
        # body
        self.qp.setPen(QColor(0, 255, 0))
        self.qp.drawEllipse(QPoint(x, y), self.robotR, self.robotR)

        # glue
        self.qp.setPen(QColor(0, 200, 0))
        self.qp.drawEllipse(QPoint(x, y), self.robotRwithGlue, self.robotRwithGlue)

        # glue
        self.qp.setPen(QColor(0, 200, 0))
        self.qp.drawEllipse(QPoint(x, y), 230, 230)

        # right brush
        self.qp.setPen(QColor(0, 255, 0))
        dx = self.rightBrushXOffset * c + self.rightBrushYOffset * s
        dy = self.rightBrushXOffset * (-s) + self.rightBrushYOffset * c
        self.qp.drawEllipse(QPoint(x + dx, y + dy), self.rightBrushR, self.rightBrushR)

        # bearing
        self.drawRay(x, y, deg, 250, QColor(0, 255, 0), 1)


    def drawRedzone(self):

        self.qp.setPen(QColor(0, 100, 0))
        self.qp.drawEllipse(QPoint(self.robotX, self.robotY), self.redzoneR, self.redzoneR)

        self.qp.setPen(QColor(0, 50, 0))
        deltaR = self.redzoneR - self.robotRwithGlue
        rr = self.robotRwithGlue
        self.qp.drawRect(self.robotX - deltaR, self.robotY - rr, deltaR, 2 * rr)
        self.qp.drawPie(QRect(self.robotX - deltaR - rr, self.robotY - rr, rr * 2, rr * 2),
                        -270 * 16, 180 * 16)


    def drawObs(self, points, color):

        self.qp.setPen(QPen(color, 1))
        for pt in points:
            x = int(pt[0] * 1000) + self.offsetX
            y = int(pt[1] * 1000) + self.offsetY
            self.qp.drawRect(x, y, 2, 2)

    def paintObjects(self):

        self.drawLabel()

        self.qp.setBrush(Qt.NoBrush)

        self.drawRay(self.robotX, self.robotY, -60 + self.lastDeg, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, -45 + self.lastDeg, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, 60 + self.lastDeg, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, -35 + self.lastDeg, 400, QColor(128, 128, 128), 1)


        self.drawRobot(self.robotX, self.robotY, self.lastDeg)

        self.drawRedzone()

        self.drawObs(self.rawPts, QColor(0, 0, 255))
        self.drawObs(self.shadowPts, QColor(255, 0, 0))
        # self.drawRobot(self.robotX + int(self.lastX * 1000) - 800,
        #                self.robotY + int(self.lastY * 1000) + 6400,
        #                0)
        # print(self.lastX, self.lastY)
        # print(self.robotX + int(self.lastX * 1000) - 800,
        #                self.robotY + int(self.lastY * 1000) + 6400)

        # ox = 1000
        # oy = self.robotY
        # self.drawRobot(ox, oy, 0)
        # v = 120
        # wd = 90
        # w = (wd / 180 * math.pi)
        # r = v / w
        # dur = 0.1
        # rad = w * dur
        # bearing = -wd * dur / 2.0
        # nx = ox + r * math.sin(rad)
        # ny = oy - (r - r * math.cos(rad))
        # self.drawRobot(nx, ny, bearing)



    def mouseMoveEvent(self, e):
        self.mousePosEnd = QPoint(e.x(), e.y())
        self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = CacheLaser()
    sys.exit(app.exec_())
