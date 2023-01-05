import sys

from PyQt5.QtWidgets import QApplication
from src.utils import GridCanvas, States, Colors
from src.algo import Dijkstra
from src.geometry import Point2D, SimpleRect


class DijkstraTestGui(GridCanvas):

    def __init__(self):

        super().__init__()

        self.initUI('Dijkstra.Test')
        self.initData()

    def initData(self):

        self.startPoint = Point2D(128, 64)
        self.goalPoint = Point2D(140, 70)
        self.box = SimpleRect(0, 0, 255, 255)
        self.algo = Dijkstra(self.startPoint, self.goalPoint, self.box,
                             lambda x0, y0, x1, y1: 1 if abs(x0-x1) + abs(y0-y1) == 1 else 10)
        self.updatePoints = []
        self.state = 1
        self.routine = None

    def onNewPoint(self, x, y, dist):

        self.updatePoints.append((x, y, dist))
        if len(self.updatePoints) % 20 == 0 or self.algo.found:
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
            super(DijkstraTestGui, self).timerEvent(event)


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

        if self.algo.found:
            self.drawPath()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = DijkstraTestGui()
    sys.exit(app.exec_())

