from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QPoint, Qt

import sys

from src.utils import GridType, GridCanvas, GridMapPPM, Colors


class MapGen(GridCanvas):

    def __init__(self):

        super().__init__()

        self.initData()
        self.initUI('MapGen')

    def initData(self):

        self.mouseDown = False
        self.mousePosBeg = QPoint(-1, -1)
        self.mousePosEnd = QPoint(-1, -1)

        self.map = GridMapPPM(self.MapWidth, self.MapHeight)


    def paintObjects(self):

        mapData = self.map.mapData

        for x in range(0, self.map.mapWidth):
            for y in range(0, self.map.mapHeight):
                if mapData[x][y] != GridType.Default:
                    self.drawPoint(x, y, self.DefaultObsColor)

        if self.mouseDown:
            self.drawPoints(self.getBresenhamPoints4(self.mousePosBeg, self.mousePosEnd), self.DefaultObsColor)

        self.drawLabel()


    def drawLabel(self):

        self.qp.setPen(Colors.DefaultTextColor)
        self.qp.drawText(50, 50, "pos {} {} -> {} {}".format(self.mousePosBeg.x(), self.mousePosBeg.y(),
                                                             self.mousePosEnd.x(), self.mousePosEnd.y()))


    def mousePressEvent(self, e):
        self.mousePosBeg = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.mouseDown = True


    def mouseMoveEvent(self, e):
        self.mousePosEnd = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.update()


    def mouseReleaseEvent(self, e):
        self.mousePosEnd = QPoint(e.pos().x() // self.TileSize, e.pos().y() // self.TileSize)
        self.mouseDown = False

        mapData = self.map.mapData
        for pt in self.getBresenhamPoints(self.mousePosBeg, self.mousePosEnd):
            mapData[pt.x()][pt.y()] = GridType.Obstacle
        self.update()


    def keyPressEvent(self, e):
        if QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_S:
            self.map.saveData(self.getSaveFileName())

        elif QApplication.keyboardModifiers() == Qt.ControlModifier and e.key() == Qt.Key_O:
            self.map.loadData(self.getOpenFileName())

        elif e.key() == Qt.Key_Backspace:
            self.data.fill(GridType.Default)
            self.update()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MapGen()
    sys.exit(app.exec_())
