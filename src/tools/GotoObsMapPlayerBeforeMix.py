import math
import sys

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QApplication

from src.geometry import *
from src.modules import FileOpener, NavNormalParser, ColorControl
from src.tools import ObstaclePlayer

ROBOT_X = 1000
ROBOT_Y = 750

def drawNear(qp, data):

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

    # if cnt > 300:
    #     print("pts: {}, filter: {}".format(len(data.points), cnt))

    print("pts: {}".format(len(data.points)))

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

if __name__ == '__main__':

    app = QApplication(sys.argv)

    fileOpener = FileOpener(None, "GotoObsMapPlayer")
    fileName = fileOpener.getPath()
    parser = NavNormalParser(fileName)
    data = parser.getGotoObsPointsBeforeMix()

    print(ColorControl.BrFgGreen)
    print("fileName: {}".format(fileName))
    print("record count: {}".format(len(data)))
    print(ColorControl.End)

    ex = ObstaclePlayer(data, Point2D(ROBOT_X, ROBOT_Y))
    # ex.addCustomFunction(printInfo, 1)
    ex.addCustomFunction(drawNear, -1)
    ex.addCustomFunction(drawExtra, 2)

    sys.exit(app.exec_())
