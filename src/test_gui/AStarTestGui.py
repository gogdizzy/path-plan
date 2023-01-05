import math
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication

from src.utils import GridCanvas, GridType, Colors, States
from src.algo import AStar
from src.geometry import Point2D, SimpleRect


class AStarTestGui(GridCanvas):

    def __init__(self):

        super().__init__()

        self.initUI('Dijkstra.Test')
        self.initData()

    def distanceFunc(self, x0, y0, x1, y1):

        cost = math.hypot(x1 - x0, y1 - y0)
        penalty = 1000000 if self.map[x1][y1] == GridType.Obstacle else 0
        return cost + penalty

    def initData(self):

        self.map = np.zeros([256, 256])
        for y in range(5, 75):
            self.map[33][y] = GridType.Obstacle
        for x in range(5, 34):
            self.map[x][75] = GridType.Obstacle

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

        if self.state == States.Init:
            self.state = States.Searching
            self.run()

        if event.timerId() == self.timer.timerId():
            self.update()
            if self.state == States.Searching:
                try:
                    self.routine.send(self.onNewPoint)
                except StopIteration:
                    self.state = States.Over
        else:
            super(AStarTestGui, self).timerEvent(event)


    def drawPath(self):

        path = self.algo.path
        for i in range(len(path) - 1):
            self.drawConn(path[i].x, path[i].y, path[i+1].x, path[i+1].y, Colors.DefaultConnColor)

    def paintObjects(self):

        for pt in self.updatePoints:
            x, y, dist = pt
            self.drawPoint(x, y, Colors.DefaultPopColor if dist == self.algo.POP_VALUE else Colors.DefaultVisitColor)

        self.drawPoint(self.startPoint.x, self.startPoint.y, Colors.DefaultStartColor)
        self.drawPoint(self.goalPoint.x, self.goalPoint.y, Colors.DefaultGoalColor)

        for x in range(self.box.left, self.box.right + 1):
            for y in range(self.box.bottom, self.box.top):
                if self.map[x][y] == GridType.Obstacle:
                    self.drawPoint(x, y, Colors.DefaultObsColor)

        if self.algo.found:
            self.drawPath()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = AStarTestGui()
    sys.exit(app.exec_())


