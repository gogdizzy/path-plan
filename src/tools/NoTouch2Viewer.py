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
        self.deltaX = 20
        self.redzoneR = self.robotRwithGlue + self.deltaX
        self.rightBrushXOffset = 92
        self.rightBrushYOffset = -113
        self.rightBrushR = 73

        oldPts = "-310,-204 -300,-204 -289,-204 -279,-204 -269,-204 -259,-203 -233,-188 -229,-192 -231,-200 -222,-199 -213,-197 -209,-201 -191,-189 -192,-197 -184,-195 -171,-191 -165,-191 -159,-190 -154,-190 -148,-189 -143,-190 -138,-189 -133,-189 -128,-191 -125,-193 -119,-190 -113,-188 -108,-188 -104,-188 -99,-188 -95,-188 -91,-188 -86,-187 -82,-187 -78,-187 -74,-187 -70,-187 -66,-186 -62,-187 -58,-186 -54,-186 -51,-186 -47,-185 -43,-183 -39,-181 -35,-179 -31,-180 -28,-180 -25,-180 -22,-190 -19,-190 -16,-190 -12,-190 -9,-190 -6,-190 -2,-190 0,-190 3,-189 7,-189 10,-189 13,-189 19,-187 22,-187 25,-187 28,-186 31,-186 35,-186 38,-186 41,-185 44,-185 48,-185 51,-185 54,-184 58,-185 61,-185 64,-184 68,-184 71,-183 75,-183 78,-183 82,-183 85,-183 89,-182 96,-182 100,-182 104,-181 108,-181 112,-181 116,-180 121,-180 125,-180 129,-179 134,-179 138,-179 142,-178 147,-177 157,-177 162,-177 167,-176 172,-176 178,-175 184,-175 190,-175 196,-174 202,-174 208,-173 214,-167 214,-161 213,-155 213,-150 212,-144 212,-139 211,-134 211,-129 210,-124 203,-113 201,-107 203,-103 201,-98 202,-94 200,-89 202,-85 200,-80 201,-76 202,-72 200,-68 201,-64 200,-60 201,-56 202,-52 207,-49 206,-45 205,-42 205,-38 205,-35 205,-31 205,-28 205,-21 204,-18 204,-15 204,-12 204,-8 204,-5 204,1 204,4 202,7 203,10 203,14 203,17 202,20 202,27 202,30 202,34 201,37 202,41 201,44 201,47 197,51 196,55 197,59 196,63 197,67 196,71 195,74 196,79 195,83 196,87 195,91 193,95 195,100 193,103 198,114 198,119 197,123 198,128 197,133 197,139 197,144 197,149 196,154 196,160 196,166 196,172 195,179 195,185 195,192 195,199 195,207 195,215 201,231 200,239 200,249 199,258 198,267 198,277 197,288 196,299 196,311 195,323"
        newPts = "-316,-206 -306,-206 -295,-206 -285,-206 -275,-206 -265,-205 -239,-190 -235,-194 -237,-202 -227,-200 -219,-199 -215,-202 -197,-190 -198,-198 -190,-196 -177,-192 -171,-192 -165,-192 -160,-191 -154,-191 -149,-191 -144,-190 -139,-190 -134,-192 -131,-194 -125,-191 -119,-189 -114,-189 -110,-189 -105,-189 -101,-188 -96,-189 -92,-188 -88,-188 -84,-188 -80,-188 -76,-187 -72,-187 -68,-188 -64,-187 -60,-186 -57,-187 -53,-185 -49,-183 -45,-182 -41,-180 -37,-180 -34,-180 -31,-181 -28,-190 -25,-190 -22,-190 -18,-190 -15,-190 -12,-190 -8,-190 -5,-190 -2,-190 1,-189 4,-189 7,-189 13,-187 16,-187 19,-187 22,-187 26,-186 29,-186 32,-186 35,-185 38,-185 42,-185 45,-185 48,-184 52,-185 55,-185 59,-184 62,-184 65,-183 69,-183 72,-183 76,-183 79,-182 83,-182 90,-181 94,-182 98,-181 102,-181 106,-180 110,-180 115,-180 119,-180 123,-179 128,-179 132,-178 137,-178 141,-177 151,-177 156,-176 161,-176 166,-175 172,-175 178,-174 184,-174 190,-174 196,-173 202,-172 208,-166 208,-160 207,-154 207,-149 206,-143 206,-138 205,-133 204,-128 204,-123 197,-112 195,-106 196,-102 194,-97 196,-93 194,-88 195,-84 193,-79 194,-75 196,-72 194,-67 195,-63 193,-59 194,-55 195,-51 200,-48 199,-44 199,-41 198,-37 198,-34 198,-31 198,-27 198,-21 197,-17 197,-14 197,-11 197,-7 197,-4 197,1 197,5 195,8 196,11 196,14 196,18 195,21 195,28 195,31 195,35 194,38 194,41 194,45 194,48 190,52 189,56 190,60 188,64 190,68 188,72 187,75 189,80 187,83 189,88 187,92 185,95 187,101 185,104 191,115 190,120 190,124 190,129 190,134 190,139 189,145 189,150 188,155 188,161 188,167 188,173 187,179 187,186 187,193 187,200 187,208 187,216 192,232 192,240 191,249 191,258 190,268 189,278 189,289 188,300 187,312 186,324"

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
                print("inbullet ", toSegDist,
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
        self.qp.drawLine(x, y, x + length * math.cos(rad), y + length * math.sin(rad))

    def drawRobot(self, x, y, deg):

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
        self.drawRay(self.robotX, self.robotY, -35, 400, QColor(128, 128, 128), 1)

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
