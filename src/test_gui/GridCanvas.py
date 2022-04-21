
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import QBasicTimer, QSettings


class GridCanvas(QWidget):

    TileSize = 10
    FrameSpeed = 30
    MapWidth = 512
    MapHeight = 256

    DefaultTextColor = QColor(0, 0, 0)
    DefaultBgColor = QColor(224, 224, 216)
    DefaultGridColor = QColor(168, 168, 158)
    DefaultStartColor = QColor(255, 128, 128)
    DefaultGoalColor = QColor(128, 128, 255)
    DefaultConnColor = QColor(0, 250, 34)
    DefaultObsColor = QColor(0, 0, 0)
    DefaultNearObsColor = QColor(150, 150, 150)
    DefaultCornerColor = QColor(255, 0, 0)
    DefaultNearCornerColor = QColor(100, 100, 100)
    DefaultVisitColor = QColor(102, 250, 196)
    DefaultPopColor = QColor(202, 250, 196)
    DefaultNarrowColor = QColor(255, 0, 0)

    def __init__(self):

        super().__init__()


    def initUI(self, title):

        self.qp = QPainter()

        self.setWindowTitle(title)
        self.showMaximized()

        self.timer = QBasicTimer()
        self.timer.start(self.FrameSpeed, self)


    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def closeEvent(self, event):

        event.accept()


    def paintObjects(self):

        pass


    def paintEvent(self, e):

        self.qp.begin(self)
        self.drawBackground()
        self.drawGridLine()

        self.paintObjects()

        self.qp.end()


    def drawBackground(self, color=DefaultBgColor):

        self.qp.setPen(color)
        self.qp.setBrush(color)
        self.qp.drawRect(0, 0, self.TileSize * self.MapWidth, self.TileSize * self.MapHeight)


    def drawGridLine(self, color=DefaultGridColor):

        size = self.size()

        self.qp.setPen(color)
        for col in range(0, size.width(), self.TileSize):
            self.qp.drawLine(col, 0, col, size.height())
        for row in range(0, size.height(), self.TileSize):
            self.qp.drawLine(0, row, size.width(), row)


    def drawPoint(self, pt, color):

        self.drawPoint(pt.x(), pt.y(), color)


    def drawPoint(self, x, y, color):

        self.qp.setBrush(color)
        self.qp.drawRect(x * self.TileSize, y * self.TileSize, self.TileSize, self.TileSize)


    def drawPoints(self, points, color):

        self.qp.setBrush(color)
        for pt in points:
            self.qp.drawRect(pt.x() * self.TileSize, pt.y() * self.TileSize, self.TileSize, self.TileSize)


    def drawConn(self, pt0, pt1, color):

        self.drawConn(pt0.x(), pt0.y(), pt1.x(), pt1.y(), color)


    def drawConn(self, x0, y0, x1, y1, color):
        pen = QPen(color, 2)
        self.qp.setPen(pen)
        self.qp.drawLine(x0 * self.TileSize + self.TileSize / 2,
                         y0 * self.TileSize + self.TileSize / 2,
                         x1 * self.TileSize + self.TileSize / 2,
                         y1 * self.TileSize + self.TileSize / 2)


    def getOpenFileName(self):
        qSettings = QSettings()
        lastPath = qSettings.value("LastFilePath")
        filename, choosed = QFileDialog.getOpenFileName(self, 'Open file', lastPath)

        if not choosed:
            return None

        qSettings.setValue("LastFilePath", filename)
        return filename


    def getSaveFileName(self):
        qSettings = QSettings()
        lastPath = qSettings.value("LastFilePath")
        filename, choosed = QFileDialog.getSaveFileName(self, 'Save file', lastPath)

        if not choosed:
            return None

        qSettings.setValue("LastFilePath", filename)
        return filename

