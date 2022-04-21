import math
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication

from src.test_gui import GridCanvas
from src.algo import AStar
from src.geometry import Point2D, SimpleRect


class AStarTestGui(GridCanvas):

    OBS_VALUE = 1

    STATE_INIT = 1
    STATE_SEARCH = 2
    STATE_OVER = 3

    def __init__(self):

        super().__init__()

        self.initUI('Dijkstra.Test')
        self.initData()

    def distanceFunc(self, x0, y0, x1, y1):

        cost = math.hypot(x1 - x0, y1 - y0)
        penalty = 1000000 if self.map[x1][y1] == self.OBS_VALUE else 0
        return cost + penalty

    def initData(self):

        self.map = np.zeros([256, 256])
        for y in range(5, 75):
            self.map[33][y] = self.OBS_VALUE
        for x in range(5, 34):
            self.map[x][75] = self.OBS_VALUE

        self.startPoint = Point2D(28, 64)
        self.goalPoint = Point2D(40, 70)
        self.box = SimpleRect(0, 0, 255, 255)
        self.algo = AStar(self.startPoint, self.goalPoint, self.box, self.distanceFunc)
        self.updatePoints = []
        self.state = 1
        self.routine = None

    def onNewPoint(self, x, y, dist):

        self.updatePoints.append((x, y, dist))
        if len(self.updatePoints) % 100 == 0 or self.algo.found:
            return True
        return False

    def run(self):

        self.routine = self.algo.searchGenerator(self.onNewPoint)
        self.routine.send(None)

    def timerEvent(self, event):
        '''handles timer event'''

        if self.state == self.STATE_INIT:
            self.state = self.STATE_SEARCH
            self.run()

        if event.timerId() == self.timer.timerId():
            self.update()
            if self.state == self.STATE_SEARCH:
                try:
                    self.routine.send(self.onNewPoint)
                except StopIteration:
                    self.state = self.STATE_OVER
        else:
            super(AStarTestGui, self).timerEvent(event)


    def drawPath(self):

        path = self.algo.path
        for i in range(len(path) - 1):
            self.drawConn(path[i].x, path[i].y, path[i+1].x, path[i+1].y, self.DefaultConnColor)

    def paintObjects(self):

        for pt in self.updatePoints:
            x, y, dist = pt
            self.drawPoint(x, y, self.DefaultPopColor if dist == self.algo.POP_VALUE else self.DefaultVisitColor)

        self.drawPoint(self.startPoint.x, self.startPoint.y, self.DefaultStartColor)
        self.drawPoint(self.goalPoint.x, self.goalPoint.y, self.DefaultGoalColor)

        for x in range(self.box.left, self.box.right + 1):
            for y in range(self.box.bottom, self.box.top):
                if self.map[x][y] == self.OBS_VALUE:
                    self.drawPoint(x, y, self.DefaultObsColor)

        if self.algo.found:
            self.drawPath()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = AStarTestGui()
    sys.exit(app.exec_())


