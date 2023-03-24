from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QPoint, Qt, QRect
import sys
import math

from src.utils import GridCanvas, Colors


class Notouch2Viewer(GridCanvas):

    def __init__(self):

        super().__init__()

        self.initData()
        self.initUI('Notouch2Viewer')

        self.setMouseTracking(True)

    def inBullet(self, bearing, range, dx):
        return (range * range + dx * dx - 2 * range * dx * math.cos(bearing)) < self.robotRwithGlue * self.robotRwithGlue

    def initData(self):

        self.mousePosEnd = QPoint(0, 0)

        self.robotX = 500
        self.robotY = 500
        self.robotR = 175
        self.robotRwithGlue = 179
        self.deltaX = 19
        self.redzoneR = self.robotRwithGlue + self.deltaX
        self.rightBrushXOffset = 92
        self.rightBrushYOffset = -113
        self.rightBrushR = 73

        oldPts = "206,-38 204,-35 204,-32 203,-26 203,-23 202,-17 201,-14 201,-11 200,-9 200,-6 195,-1 201,2 221,6"
        newPts = "199,-43 197,-40 197,-37 196,-31 196,-28 195,-22 194,-19 195,-16 194,-14 194,-11 189,-5 195,-2 215,1"

        self.oldPts = oldPts.split(" ")
        self.newPts = newPts.split(" ")

        validMinBearing = -60 / 180 * math.pi
        validMaxBearing = 60 / 180 * math.pi

        for i in range(len(self.oldPts)):
            oldX, oldY = map(int, self.oldPts[i].split(","))
            newX, newY = map(int, self.newPts[i].split(","))

            oldBearing = math.atan2(oldY, oldX)
            newBearing = math.atan2(newY, newX)
            estimatedBearing = (oldBearing + newBearing) / 2
            if math.fabs(estimatedBearing - oldBearing) > math.pi / 2:
                if estimatedBearing >= 0:
                    estimatedBearing -= math.pi
                else:
                    estimatedBearing += math.pi

            if estimatedBearing < validMinBearing or estimatedBearing > validMaxBearing:
                continue

            tp, toSegDist = self.getDistToSeg(oldX, oldY, newX, newY)

            if tp == 1:
                continue

            if self.inBullet(estimatedBearing, toSegDist, self.deltaX):
                print("inbullet ", toSegDist,
                      oldX, oldY, oldBearing / math.pi * 180,
                      newX, newY, newBearing / math.pi * 180,
                      estimatedBearing / math.pi * 180
                      )

            elif toSegDist < self.redzoneR:
                print(tp, toSegDist,
                      oldX, oldY, oldBearing / math.pi * 180,
                      newX, newY, newBearing / math.pi * 180,
                      estimatedBearing / math.pi * 180
                     )

            else:
                print("bad ", toSegDist,
                      oldX, oldY, oldBearing / math.pi * 180,
                      newX, newY, newBearing / math.pi * 180,
                      estimatedBearing / math.pi * 180
                      )

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

        # body
        self.qp.setPen(QColor(0, 255, 0))
        self.qp.drawEllipse(QPoint(x, y), self.robotR, self.robotR)

        # glue
        self.qp.setPen(QColor(0, 200, 0))
        self.qp.drawEllipse(QPoint(x, y), self.robotRwithGlue, self.robotRwithGlue)

        # right brush
        self.qp.setPen(QColor(0, 255, 0))
        self.qp.drawEllipse(QPoint(x + self.rightBrushXOffset, y + self.rightBrushYOffset), self.rightBrushR, self.rightBrushR)

        # bearing
        self.drawRay(x, y, deg, 250, QColor(0, 255, 0), 1)


    def drawRedzone(self):

        self.qp.setPen(QColor(0, 100, 0))
        self.qp.drawEllipse(QPoint(self.robotX, self.robotY), self.redzoneR, self.redzoneR)

        self.qp.setPen(QColor(0, 50, 0))
        deltaR = self.redzoneR - self.robotRwithGlue
        rr = self.robotRwithGlue
        self.qp.drawRect(self.robotX, self.robotY - rr, deltaR, 2 * rr)
        self.qp.drawPie(QRect(self.robotX + deltaR - rr, self.robotY - rr, rr * 2, rr * 2),
                        -90 * 16, 180 * 16)


    def drawObs(self, points, color):

        self.qp.setPen(QPen(color, 1))
        for pt in points:
            x, y = map(int, pt.split(","))
            self.qp.drawRect(self.robotX + x, self.robotY + y, 2, 2)

    def paintObjects(self):

        self.drawLabel()

        self.qp.setBrush(Qt.NoBrush)

        self.drawRay(self.robotX, self.robotY, -60, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, -45, 400, QColor(128, 128, 128), 1)
        self.drawRay(self.robotX, self.robotY, 60, 400, QColor(128, 128, 128), 1)

        self.drawRobot(self.robotX, self.robotY, 0)

        self.drawRedzone()

        self.drawObs(self.oldPts, QColor(0, 0, 255))
        self.drawObs(self.newPts, QColor(255, 0, 0))

        ox = 1000
        oy = self.robotY
        self.drawRobot(ox, oy, 0)
        v = 120
        wd = 90
        w = (wd / 180 * math.pi)
        r = v / w
        dur = 0.1
        rad = w * dur
        bearing = -wd * dur / 2.0
        nx = ox + r * math.sin(rad)
        ny = oy - (r - r * math.cos(rad))
        self.drawRobot(nx, ny, bearing)



    def mouseMoveEvent(self, e):
        self.mousePosEnd = QPoint(e.x(), e.y())
        self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Notouch2Viewer()
    sys.exit(app.exec_())
