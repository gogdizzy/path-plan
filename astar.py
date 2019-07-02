from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMessageBox, QInputDialog, QApplication
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QBasicTimer, QPoint
import numpy as np
import sys, math
import queue

class AStar(QWidget):

    TileSize = 10
    FrameSpeed = 30
    MapWidth = 512
    MapHeight = 256


    def __init__(self):

        super().__init__()

        self.initData()
        self.initUI()

    def initData(self):

        self.startPoint = QPoint(28, 64)
        self.goalPoint = QPoint(40, 70)
        self.data = np.zeros((self.MapWidth, self.MapHeight))
        self.data.fill(np.inf)
        for y in range(5, 75):
            self.data[33][y] = -1
        for x in range(5, 34):
            self.data[x][75] = -1
        self.par = np.empty((self.MapWidth, self.MapHeight), dtype=tuple)
        self.par.fill((-1,-1))

        dic = {"Distance 0": lambda x, y: 0,
               "Euclidean Distance": lambda x, y: np.hypot(x - self.goalPoint.x(), y - self.goalPoint.y()),
               "Manhattan Distance": lambda x, y: np.abs(x - self.goalPoint.x()) + np.abs(y - self.goalPoint.y()),
               "Diagonal Distance": self.diagonal}

        htype, choosed = QInputDialog.getItem(self, "Choose Heuristic", "Choose Heuristic:", dic.keys(), 0, False)
        if not choosed:
            exit(-1)
        self.h = dic[htype]

        self.queue = queue.PriorityQueue()
        self.data[self.startPoint.x()][self.startPoint.y()] = 0
        self.queue.put((self.f(0, self.startPoint.x(), self.startPoint.y()), 0, self.startPoint.x(), self.startPoint.y()))
        self.found = False

    def initUI(self):

        self.qp = QPainter()

        self.bgColor = QColor(224, 224, 216)
        self.gridColor = QColor(168, 168, 158)
        self.startColor = QColor(255, 128, 128)
        self.goalColor = QColor(128, 128, 255)
        self.connColor = QColor(155, 100, 34)
        self.obsColor = QColor(0, 0, 0)
        self.visitColor = QColor(102, 250, 196)

        self.setWindowTitle('Test')
        self.showMaximized()

        self.timer = QBasicTimer()
        self.timer.start(self.FrameSpeed, self)

    def diagonal(self, x, y):
        dx = np.abs(x - self.goalPoint.x())
        dy = np.abs(y - self.goalPoint.y())
        return np.minimum(dx, dy) * math.sqrt(2) + np.abs(dx - dy)

    def f(self, g, x, y):

        return g + self.h(x, y)

    def dataExpand(self, x, y, dist):

        if x < 0 or x >= self.MapWidth or y < 0 or y >= self.MapHeight\
                or self.data[x][y] < 0 or dist >= self.data[x][y]:
            return False
        self.data[x][y] = dist
        self.queue.put((self.f(dist, x, y), dist, x, y))
        return True

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def timerEvent(self, event):
        '''handles timer event'''

        if self.found:
            return

        offsets = [(-1, -1, math.sqrt(2)), (-1, 0, 1), (-1, 1, math.sqrt(2)),
                   (0, -1, 1), (0, 1, 1),
                   (1, -1, math.sqrt(2)), (1, 0, 1), (1, 1, math.sqrt(2))]

        if event.timerId() == self.timer.timerId():
            # self.drawRandomPoint()
            cnt = 0
            while not self.queue.empty():

                tp = self.queue.get()
                dist = tp[1]
                x = tp[2]
                y = tp[3]
                if x == self.goalPoint.x() and y == self.goalPoint.y():
                    self.timer.stop()
                    self.found = True
                    QMessageBox.question(self, 'Message',
                                         "found goal, totalsearch = {}, dist = {}".format(self.totalSearch(), dist), QMessageBox.Ok)

                if dist == self.data[x][y]:
                    for offset in offsets:
                        if self.dataExpand(x + offset[0], y + offset[1], dist + offset[2]):
                            self.par[x + offset[0]][y + offset[1]] = (x, y)
                    cnt += 1
                    if cnt > 40:
                        break

            self.update()

        else:
            super(AStar, self).timerEvent(event)

    def closeEvent(self, event):
        event.accept()

    def paintEvent(self, e):

        self.qp.begin(self)
        self.drawBackground()
        self.drawGridLine()
        for x in range(0, self.MapWidth):
            for y in range(0, self.MapHeight):
                if self.data[x][y] != np.inf:
                    if self.data[x][y] == -1:
                        self.drawPoint(x, y, self.obsColor)
                    else:
                        self.drawPoint(x, y, self.visitColor)
        self.drawPoint(self.startPoint.x(), self.startPoint.y(), self.startColor)
        self.drawPoint(self.goalPoint.x(), self.goalPoint.y(), self.goalColor)

        if self.found:
            self.drawPath()

        self.qp.end()

    def drawBackground(self):

        fillc = self.bgColor

        self.qp.setPen(fillc)
        self.qp.setBrush(fillc)
        self.qp.drawRect(0, 0, self.TileSize * self.MapWidth, self.TileSize * self.MapHeight)


    def drawGridLine(self):

        size = self.size()
        linec = self.gridColor

        self.qp.setPen(linec)
        for col in range(0, size.width(), self.TileSize):
            self.qp.drawLine(col, 0, col, size.height())
        for row in range(0, size.height(), self.TileSize):
            self.qp.drawLine(0, row, size.width(), row)


    def drawPoint(self, x, y, color):

        self.qp.setBrush(color)
        self.qp.drawRect(x * self.TileSize, y * self.TileSize, self.TileSize, self.TileSize)

    def drawConn(self, x0, y0, x1, y1, color):

        self.qp.setPen(color)
        self.qp.drawLine(x0 * self.TileSize + self.TileSize / 2,
                         y0 * self.TileSize + self.TileSize / 2,
                         x1 * self.TileSize + self.TileSize / 2,
                         y1 * self.TileSize + self.TileSize / 2)

    def drawPath(self):

        x = self.goalPoint.x()
        y = self.goalPoint.y()
        sx = self.startPoint.x()
        sy = self.startPoint.y()

        while x != sx or y != sy:
            px, py = self.par[x][y]
            self.drawConn(px, py, x, y, self.connColor)
            x, y = px, py

    def totalSearch(self):
        # return sum([map(lambda x: 1 if 0 <= x < np.inf else 0, sum(self.data, []))])
        return sum([1 if 0 <= x < np.inf else 0 for x in self.data.flat])

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = AStar()
    sys.exit(app.exec_())