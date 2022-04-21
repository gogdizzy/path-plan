import queue
import math
import numpy as np

from src.geometry import Point2D, SimpleRect


class AStar:

    POP_VALUE = -2
    UNKNOWN_VALUE = np.inf

    OFFSETS = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    @staticmethod
    def defaultDistance(startX, startY, endX, endY):

        return math.hypot(endX - startX, endY - startY)

    def __init__(self, startPoint, endPoint, boundingBox,
                 distanceFunc=None, heuristicFunc=None):

        self.startX = startPoint.x
        self.startY = startPoint.y
        self.endX = endPoint.x
        self.endY = endPoint.y
        self.box = boundingBox
        self.distFunc = distanceFunc if distanceFunc else self.defaultDistance
        self.heuristicFunc = heuristicFunc if heuristicFunc else self.defaultDistance

        self.dist = np.empty([boundingBox.width(), boundingBox.height()])
        self.dist.fill(self.UNKNOWN_VALUE)
        self.dist[self.startX][self.startY] = 0
        self.source = np.empty([boundingBox.width(), boundingBox.height()], dtype=tuple)
        self.queue = queue.PriorityQueue()
        self.queue.put((0 + self.heuristicFunc(self.startX, self.startY, self.endX, self.endY), 0, self.startX, self.startY))
        self.found = False
        self.path = []

    def tryExpand(self, x, y, dist):

        if (not self.box.contains(x, y)) or self.dist[x][y] < 0 or dist >= self.dist[x][y]:
            return False

        self.dist[x][y] = dist
        self.queue.put((dist + self.heuristicFunc(x, y, self.endX, self.endY), dist, x, y))
        return True

    def search(self):

        while not self.queue.empty():

            curPoint = self.queue.get()
            f, g, x, y = curPoint

            if x == self.endX and y == self.endY:
                self.found = True
                break

            if g == self.dist[x][y]:
                self.dist[x][y] = self.POP_VALUE
                for offset in self.OFFSETS:
                    nx, ny = x + offset[0], y + offset[1]
                    nd = self.dist[x][y] + self.distFunc(x, y, nx, ny)
                    if self.tryExpand(nx, ny, nd):
                        self.source[nx][ny] = x, y

        if self.found:
            x, y = self.endX, self.endY
            while True:
                self.path.append(Point2D(x, y))
                if x == self.startX and y == self.startY:
                    break
                x, y = self.source[x][y]
            self.path.reverse()

        return self.path


    def searchGenerator(self, onNewPoint):

        while not self.queue.empty():

            curPoint = self.queue.get()
            f, g, x, y = curPoint

            if x == self.endX and y == self.endY:
                self.found = True
                break

            if g == self.dist[x][y]:
                self.dist[x][y] = self.POP_VALUE
                if onNewPoint(x, y, self.dist[x][y]):
                    yield
                for offset in self.OFFSETS:
                    nx, ny = x + offset[0], y + offset[1]
                    nd = g + self.distFunc(x, y, nx, ny)
                    if self.tryExpand(nx, ny, nd):
                        self.source[nx][ny] = x, y
                        if onNewPoint(nx, ny, self.dist[nx][ny]):
                            yield

        if self.found:
            x, y = self.endX, self.endY
            while True:
                self.path.append(Point2D(x, y))
                if x == self.startX and y == self.startY:
                    break
                x, y = self.source[x][y]
            self.path.reverse()

        return self.path




