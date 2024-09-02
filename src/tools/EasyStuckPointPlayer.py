import math
import sys
from collections import deque

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QApplication

from src.algo import HullType, GraphicAlgo, MergeFindSet
from src.geometry import Point2D, distanceSquare
from src.modules import FileOpener, NavNormalParser, ColorControl
from src.tools import ObstaclePlayer

ROBOT_X = 1000
ROBOT_Y = 750

def ClusterPoints(points, dist):

    distSqr = dist * dist
    mfs = MergeFindSet()

    for i in range(0, len(points)):
        for j in range(i + 1, len(points)):
            if distanceSquare(points[i], points[j]) <= distSqr:
                mfs.merge(i, j)

    res = dict()
    for i in range(0, len(points)):
        group = mfs.find(i)
        res.setdefault(group, []).append(points[i])

    return res.values()

def drawBox(qp, data):

    print("all: {}".format(data.points))

    for points in ClusterPoints(data.points, 50):
        print(points)
        if (len(points) < 3):
            continue

        for width, color, box in [(4, QColor(0, 230, 200), GraphicAlgo.getHull(points, HullType.ConcaveHull_KNN, 3)),
                           (3, QColor(0, 0, 230), GraphicAlgo.getHull(points, HullType.ConcaveHull_KNN, 30)),
                           (2, QColor(230, 0, 230), GraphicAlgo.getHull(points, HullType.ConcaveHull_KNN, 50)),
                           (1, QColor(230, 0, 0), GraphicAlgo.getHull(points, HullType.ConvexHull_GrahamScan))]:

            print("boxSize: ", len(box))

            qp.setPen(QPen(color, width))
            for i in range(-1, len(box) - 1):
                qp.drawLine(ROBOT_X + box[i].x, ROBOT_Y + box[i].y,
                            ROBOT_X + box[i+1].x, ROBOT_Y + box[i+1].y)


def drawOccupy(qp, data):

    radius = 190
    qp.setPen(QPen(QColor(200, 200, 200), 1))
    for pt in data.points:
        qp.drawEllipse(QPoint(ROBOT_X + pt.x, ROBOT_Y + pt.y), radius, radius)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    fileOpener = FileOpener(None, "EasyStuckPointPlayer")
    fileName = fileOpener.getPath()
    parser = NavNormalParser(fileName)
    data = parser.getEasyStuckPoints()

    print(ColorControl.BrFgGreen)
    print("fileName: {}".format(fileName))
    print("record count: {}".format(len(data)))
    print(ColorControl.End)

    ex = ObstaclePlayer(data, Point2D(ROBOT_X, ROBOT_Y))
    # ex.addCustomFunction(drawOccupy, -1)
    # ex.addCustomFunction(drawBox, 1)

    sys.exit(app.exec_())
