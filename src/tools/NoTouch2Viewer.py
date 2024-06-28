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
        self.deltaX = 25
        self.redzoneR = self.robotRwithGlue + self.deltaX
        self.rightBrushXOffset = 97
        self.rightBrushYOffset = -117
        self.rightBrushR = 73

        newPts = "-324,0 -325,-4 -326,-7 -328,-11 -328,-14 -329,-18 -330,-22 -331,-25 -333,-29 -333,-33 -336,-37 -335,-41 -336,-45 -337,-49 -339,-53 -341,-58 -341,-62 -343,-67 -346,-72 -348,-77 -350,-82 -351,-87 -351,-91 -353,-97 -356,-103 -359,-109 -361,-115 -361,-120 -363,-127 -366,-133 -368,-141 -368,-146 -371,-154 -372,-161 -376,-170 -378,-177 -381,-186 -385,-196 -386,-204 -391,-215 -394,-226 -398,-238 -401,-248 -407,-263 -411,-276 -413,-289 -420,-306 -424,-321 -432,-341 -436,-359 -440,-376 -451,-403 -457,-425 -467,-454 -478,-486 -503,-561 -510,-593 -729,-1006 -707,-1009 -688,-1016 -669,-1022 -649,-1029 -629,-1036 -610,-1042 -591,-1047 -572,-1053 -552,-1058 -534,-1065 -515,-1071 -495,-1077 -476,-1083 -458,-1092 -439,-1097 -420,-1103 -402,-1111 -383,-1117 -363,-1122 -343,-1127 -324,-1135 -306,-1143 -286,-1149 -180,-782 -163,-739 -149,-683 -136,-651 -115,-579 -106,-543 -98,-519 -84,-471 -77,-455 -72,-433 -66,-418 -61,-401 -57,-387 -52,-375 -49,-359 -45,-346 -41,-337 -37,-326 -35,-314 -32,-305 -29,-296 -26,-287 -22,-282 -20,-273 -18,-264 -15,-258 -13,-250 -11,-244 -9,-237 -7,-231 -6,-223 -4,-219 -2,-212 0,-207 2,-203 3,-197 6,-195 12,-196 20,-199 27,-202 36,-206 42,-207 344,-540 348,-525 352,-511 358,-500 361,-486 368,-476 370,-462 375,-449 379,-438 383,-426 387,-415 390,-403 395,-391 401,-382 404,-370 408,-359 411,-348 416,-338 419,-327 424,-317 427,-306 431,-296 435,-285 437,-274 442,-264 444,-253 448,-243 453,-233 458,-223 461,-213 465,-203 469,-193 473,-183 476,-172 479,-162 483,-152 488,-141 492,-131 495,-120 500,-110 505,-100 508,-89 512,-78 516,-67 519,-56 524,-45 528,-34 533,-23 537,-11 539,0 494,22 474,32 441,40 421,48 385,63 368,69 352,76 337,81 318,86 302,91 290,96 280,101 267,105 260,111 248,114 237,118 229,122 218,125 210,129 202,132 194,136 186,138 175,140 168,143 161,146 154,149 148,151 142,154 135,156 129,159 122,161 118,164 113,167 106,168 102,171 96,173 90,174 86,177 80,178 76,181 71,183 66,184 61,186 56,188 51,189 46,190 42,192 38,194 33,196 29,198 25,200 21,202 17,203 13,204 8,205 5,208 -6,199 -9,201 -14,200 -18,202 -22,202 -26,204 -29,206 -33,206 -37,208 -41,210 -44,211 -48,211 -52,213 -56,214 -60,214 -63,216 -67,218 -71,219 -74,220 -78,221 -82,223 -85,225 -89,226 -93,227 -97,228 -101,229 -105,230 -109,231 -113,233 -117,234 -121,236 -125,237 -129,239 -134,241 -138,242 -142,243 -147,245 -151,246 -155,246 -160,247 -165,250 -169,250 -174,253 -179,254 -184,256 -190,259 -195,260 -200,262 -205,262 -212,266 -217,268 -223,268 -230,273 -236,273 -240,272 -245,269 -245,257 -248,251 -249,243 -252,238 -253,230 -255,225 -256,219 -258,213 -260,208 -262,202 -263,197 -264,192 -265,185 -267,181 -268,176 -269,172 -271,168 -272,163 -274,159 -275,155 -276,151 -279,149 -279,144 -281,141 -282,136 -283,132 -285,130 -284,124 -286,122 -288,119 -290,115 -291,112 -292,108 -294,105 -294,101 -296,98 -296,94 -297,92 -299,89 -299,85 -300,81 -300,78 -301,75 -302,71 -303,68 -304,65 -306,62 -307,59 -308,56 -309,53 -310,49 -310,46 -311,43 -313,40 -314,37 -315,34 -317,30 -317,27 -318,24 -319,20 -319,17 -321,14 -323,10 -323,7 -323,3"
        oldPts = "-324,0 -325,-4 -326,-7 -328,-11 -328,-14 -329,-18 -330,-22 -331,-25 -333,-29 -333,-33 -336,-37 -335,-41 -336,-45 -337,-49 -339,-53 -341,-58 -341,-62 -343,-67 -346,-72 -348,-77 -350,-82 -351,-87 -351,-91 -353,-97 -356,-103 -359,-109 -361,-115 -361,-120 -363,-127 -366,-133 -368,-141 -368,-146 -371,-154 -372,-161 -376,-170 -378,-177 -381,-186 -385,-196 -386,-204 -391,-215 -394,-226 -398,-238 -401,-248 -407,-263 -411,-276 -413,-289 -420,-306 -424,-321 -432,-341 -436,-359 -440,-376 -451,-403 -457,-425 -467,-454 -478,-486 -503,-561 -510,-593 -729,-1006 -707,-1009 -688,-1016 -669,-1022 -649,-1029 -629,-1036 -610,-1042 -591,-1047 -572,-1053 -552,-1058 -534,-1065 -515,-1071 -495,-1077 -476,-1083 -458,-1092 -439,-1097 -420,-1103 -402,-1111 -383,-1117 -363,-1122 -343,-1127 -324,-1135 -306,-1143 -286,-1149 -180,-782 -163,-739 -149,-683 -136,-651 -115,-579 -106,-543 -98,-519 -84,-471 -77,-455 -72,-433 -66,-418 -61,-401 -57,-387 -52,-375 -49,-359 -45,-346 -41,-337 -37,-326 -35,-314 -32,-305 -29,-296 -26,-287 -22,-282 -20,-273 -18,-264 -15,-258 -13,-250 -11,-244 -9,-237 -7,-231 -6,-223 -4,-219 -2,-212 0,-207 2,-203 3,-197 6,-195 12,-196 20,-199 27,-202 36,-206 42,-207 344,-540 348,-525 352,-511 358,-500 361,-486 368,-476 370,-462 375,-449 379,-438 383,-426 387,-415 390,-403 395,-391 401,-382 404,-370 408,-359 411,-348 416,-338 419,-327 424,-317 427,-306 431,-296 435,-285 437,-274 442,-264 444,-253 448,-243 453,-233 458,-223 461,-213 465,-203 469,-193 473,-183 476,-172 479,-162 483,-152 488,-141 492,-131 495,-120 500,-110 505,-100 508,-89 512,-78 516,-67 519,-56 524,-45 528,-34 533,-23 537,-11 539,0 494,22 474,32 441,40 421,48 385,63 368,69 352,76 337,81 318,86 302,91 290,96 280,101 267,105 260,111 248,114 237,118 229,122 218,125 210,129 202,132 194,136 186,138 175,140 168,143 161,146 154,149 148,151 142,154 135,156 129,159 122,161 118,164 113,167 106,168 102,171 96,173 90,174 86,177 80,178 76,181 71,183 66,184 61,186 56,188 51,189 46,190 42,192 38,194 33,196 29,198 25,200 21,202 17,203 13,204 8,205 5,208 -6,199 -9,201 -14,200 -18,202 -22,202 -26,204 -29,206 -33,206 -37,208 -41,210 -44,211 -48,211 -52,213 -56,214 -60,214 -63,216 -67,218 -71,219 -74,220 -78,221 -82,223 -85,225 -89,226 -93,227 -97,228 -101,229 -105,230 -109,231 -113,233 -117,234 -121,236 -125,237 -129,239 -134,241 -138,242 -142,243 -147,245 -151,246 -155,246 -160,247 -165,250 -169,250 -174,253 -179,254 -184,256 -190,259 -195,260 -200,262 -205,262 -212,266 -217,268 -223,268 -230,273 -236,273 -240,272 -245,269 -245,257 -248,251 -249,243 -252,238 -253,230 -255,225 -256,219 -258,213 -260,208 -262,202 -263,197 -264,192 -265,185 -267,181 -268,176 -269,172 -271,168 -272,163 -274,159 -275,155 -276,151 -279,149 -279,144 -281,141 -282,136 -283,132 -285,130 -284,124 -286,122 -288,119 -290,115 -291,112 -292,108 -294,105 -294,101 -296,98 -296,94 -297,92 -299,89 -299,85 -300,81 -300,78 -301,75 -302,71 -303,68 -304,65 -306,62 -307,59 -308,56 -309,53 -310,49 -310,46 -311,43 -313,40 -314,37 -315,34 -317,30 -317,27 -318,24 -319,20 -319,17 -321,14 -323,10 -323,7 -323,3"

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
