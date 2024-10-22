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
        self.deltaX = 45
        self.redzoneR = self.robotRwithGlue + self.deltaX
        self.rightBrushXOffset = 97
        self.rightBrushYOffset = -117
        self.rightBrushR = 73

        newPts = "-253,-174 -242,-173 -234,-173 -231,-177 -222,-176 -214,-175 -211,-179 -202,-177 -193,-175 -187,-175 -188,-182 -180,-180 -177,-183 -164,-174 -161,-177 -161,-184 -153,-181 -150,-184 -143,-181 -141,-184 -138,-186 -131,-184 -128,-186 -121,-182 -118,-184 -112,-181 -109,-184 -104,-181 -101,-182 -98,-185 -92,-182 -90,-184 -85,-181 -81,-182 -78,-184 -74,-181 -71,-182 -68,-184 -64,-182 -60,-183 -57,-184 -53,-181 -50,-182 -47,-183 -43,-182 -40,-182 -37,-183 -33,-180 -30,-181 -27,-181 -24,-181 -21,-181 -18,-181 -14,-181 -11,-181 -8,-181 -5,-181 -2,-181 0,-181 4,-180 5,-163 8,-163 11,-163 14,-162 17,-165 20,-165 23,-164 26,-163 30,-171 33,-170 37,-173 40,-172 43,-171 48,-173 51,-172 53,-168 57,-171 60,-170 63,-169 66,-168 71,-171 72,-166 77,-168 82,-171 85,-169 91,-172 93,-169 100,-173 103,-171 111,-176 117,-178 115,-169 118,-167 122,-166 127,-167 130,-164 142,-172"
        oldPts = "-274,-173 -263,-171 -255,-171 -252,-175 -243,-174 -235,-174 -232,-177 -222,-175 -214,-173 -208,-174 -209,-181 -200,-178 -197,-181 -184,-173 -181,-176 -182,-183 -174,-179 -171,-182 -164,-179 -161,-183 -158,-185 -152,-182 -149,-185 -142,-181 -139,-183 -133,-180 -130,-183 -124,-179 -121,-181 -119,-184 -113,-181 -110,-183 -105,-180 -102,-181 -99,-183 -94,-180 -91,-181 -88,-183 -84,-181 -81,-181 -78,-183 -74,-180 -71,-181 -68,-182 -64,-181 -61,-181 -58,-182 -54,-179 -51,-180 -48,-180 -45,-180 -41,-180 -38,-180 -35,-180 -32,-180 -29,-180 -26,-180 -22,-180 -19,-180 -16,-180 -15,-163 -12,-162 -9,-162 -6,-162 -3,-164 0,-164 2,-163 5,-163 10,-170 13,-169 17,-172 20,-171 23,-170 27,-173 30,-172 32,-168 36,-170 39,-169 43,-169 46,-167 51,-171 52,-166 56,-167 62,-170 65,-169 71,-172 73,-168 80,-173 83,-171 90,-176 96,-177 95,-169 97,-166 102,-166 107,-166 110,-164 122,-171"

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
