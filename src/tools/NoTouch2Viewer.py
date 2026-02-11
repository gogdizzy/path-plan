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
        self.robotRwithGlue = 178.5
        self.deltaX = 20
        self.redzoneR = self.robotRwithGlue + self.deltaX
        self.rightBrushXOffset = 97
        self.rightBrushYOffset = -117
        self.rightBrushR = 73

        oldPts = "-325,-185 -318,-183 -313,-184 -307,-182 -301,-181 -293,-182 -288,-181 -284,-182 -280,-182 -275,-181 -271,-181 -263,-182 -259,-182 -255,-181 -252,-181 -249,-183 -245,-182 -241,-182 -234,-182 -230,-181 -227,-181 -224,-181 -220,-181 -217,-182 -214,-182 -211,-182 -204,-183 -201,-182 -198,-183 -195,-182 -191,-181 -188,-182 -185,-183 -182,-182 -179,-182 -176,-182 -173,-181 -167,-181 -163,-182 -160,-182 -157,-182 -154,-182 -151,-182 -148,-183 -144,-182 -141,-182 -138,-182 -135,-182 -131,-182 -128,-181 -125,-181 -121,-182 -118,-181 -115,-181 -111,-182 -107,-182 -104,-182 -101,-181 -97,-182 -93,-182 -90,-181 -86,-181 -81,-182 -78,-181 -74,-181 -69,-182 -65,-182 -61,-181 -57,-181 -52,-182 -47,-182 -42,-182 -36,-183 -31,-183 -25,-185 -21,-184 -15,-184 -10,-183 -4,-183 2,-184 7,-183 12,-181 19,-181 27,-182 33,-181 41,-182 48,-181 56,-181 56,-176 64,-177 73,-181 80,-179 92,-180 103,-181 108,-173 113,-180 124,-179 124,-173 125,-166 124,-159 125,-153 128,-150 125,-142 122,-134 124,-129 130,-126 140,-125 150,-123 168,-124 184,-124 198,-122 217,-122 238,-122 259,-121 288,-121"
        newPts = "-340,-183 -333,-181 -328,-182 -322,-181 -317,-180 -308,-180 -303,-180 -299,-180 -295,-181 -290,-180 -286,-180 -278,-181 -274,-181 -270,-180 -267,-180 -264,-182 -260,-181 -256,-181 -249,-181 -245,-180 -242,-180 -239,-180 -235,-180 -232,-181 -229,-181 -226,-182 -219,-182 -216,-181 -213,-182 -210,-181 -206,-181 -203,-181 -200,-182 -197,-182 -194,-182 -191,-182 -188,-181 -182,-181 -178,-182 -175,-181 -172,-181 -169,-182 -166,-182 -163,-182 -159,-182 -156,-181 -153,-182 -150,-182 -146,-181 -143,-180 -140,-181 -136,-182 -133,-181 -130,-181 -126,-181 -122,-182 -119,-182 -116,-181 -112,-182 -108,-182 -105,-181 -101,-181 -96,-182 -93,-181 -89,-181 -84,-182 -80,-182 -76,-181 -72,-181 -67,-182 -62,-182 -57,-182 -51,-184 -46,-183 -40,-185 -36,-184 -30,-184 -25,-183 -19,-183 -12,-184 -7,-183 -2,-182 4,-182 11,-183 18,-182 26,-182 33,-182 41,-181 41,-177 49,-177 58,-181 65,-180 77,-181 88,-182 93,-173 98,-181 109,-180 109,-174 110,-167 109,-160 111,-154 113,-151 111,-143 107,-135 110,-130 115,-127 125,-126 135,-124 153,-125 169,-125 184,-124 203,-124 223,-123 244,-123 273,-123"

        self.oldPts = oldPts.split(" ")
        self.newPts = newPts.split(" ")

        validMinBearing = -45 / 180 * math.pi
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
            elif tp == 2:
                bearing = estimatedBearing
            else: # tp == 3
                bearing = newBearing

            if self.inBullet(bearing, toSegDist, self.deltaX):
                print("inbullet ", tp, toSegDist,
                      oldX, oldY, oldBearing / math.pi * 180,
                      newX, newY, newBearing / math.pi * 180,
                      bearing / math.pi * 180
                      )

            elif toSegDist < self.redzoneR:
                print(tp, toSegDist,
                      oldX, oldY, oldBearing / math.pi * 180,
                      newX, newY, newBearing / math.pi * 180,
                      bearing / math.pi * 180
                     )

            else:
                print("bad ", toSegDist,
                      oldX, oldY, oldBearing / math.pi * 180,
                      newX, newY, newBearing / math.pi * 180,
                      bearing / math.pi * 180
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
        self.qp.drawLine(x, y, int(x + length * math.cos(rad)), int(y + length * math.sin(rad)))

    def drawRobot(self, x0, y0, deg):

        x, y = int(x0), int(y0)

        # body
        self.qp.setPen(QColor(0, 255, 0))
        self.qp.drawEllipse(QPoint(x, y), self.robotR, self.robotR)

        # glue
        self.qp.setPen(QColor(0, 200, 0))
        self.qp.drawEllipse(QPoint(x, y), self.robotRwithGlue, self.robotRwithGlue)

        # glue
        self.qp.setPen(QColor(0, 200, 0))
        self.qp.drawEllipse(QPoint(x, y), self.robotR + 45, self.robotR + 45)

        # right brush
        self.qp.setPen(QColor(0, 255, 0))
        self.qp.drawEllipse(QPoint(x + self.rightBrushXOffset, y + self.rightBrushYOffset), self.rightBrushR, self.rightBrushR)
        self.qp.drawEllipse(QPoint(x + self.rightBrushXOffset, y + self.rightBrushYOffset), self.rightBrushR + 45, self.rightBrushR + 45)

        # bearing
        self.drawRay(x, y, deg, 250, QColor(0, 255, 0), 1)

        # valid_y
        self.drawRay(x - 200, y - 200, 0, 400, QColor(64, 64, 64), 1)


    def drawRedzone(self):

        self.qp.setPen(QColor(0, 100, 0))
        self.qp.drawEllipse(QPoint(self.robotX, self.robotY), self.redzoneR, self.redzoneR)

        self.qp.setPen(QColor(0, 50, 0))
        deltaR = self.redzoneR - self.robotRwithGlue
        rr = self.robotRwithGlue
        self.qp.drawRect(self.robotX, int(self.robotY - rr), int(deltaR), int(2 * rr))
        self.qp.drawPie(QRect(int(self.robotX + deltaR - rr), int(self.robotY - rr), int(rr * 2), int(rr * 2)),
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
        self.drawRay(self.robotX, self.robotY, -70, 400, QColor(128, 128, 128), 1)

        self.drawRobot(self.robotX, self.robotY, 0)

        self.drawRedzone()

        self.drawObs(self.oldPts, QColor(0, 0, 255))
        self.drawObs(self.newPts, QColor(255, 0, 0))

        ox = 2000
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
