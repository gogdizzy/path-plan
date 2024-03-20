import os.path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QPen, QFont
import sys

from src.modules import NavNormalParser, ColorControl, Pose2DAndValue
from src.utils import GridCanvas


class MainBrushCurrentTool(GridCanvas):


    LabelOffset = [100, 30]
    ChartMargin = 50
    OffsetX = 100
    OffsetY = 30

    Threshold = [400, 390, 380, 370,
                 360, 350, 340, 330,
                 320, 310, 300, 0]


    def __init__(self, data):

        super().__init__()

        self.originData = data

        self.initData()
        self.initUI()

    def calcPos(self, posStr):
        return round(float(posStr) / 50.0)

    def initData(self):

        data = self.originData
        self.dataArray = []
        self.dataBox = [2000, 2000, -2000, -2000]
        for pt in data:
            x, y = self.calcPos(pt.x), self.calcPos(pt.y)
            self.dataArray.append(Pose2DAndValue(x, y, pt.v))
            self.dataBox[0] = min(x, self.dataBox[0])
            self.dataBox[1] = min(y, self.dataBox[1])
            self.dataBox[2] = max(x, self.dataBox[2])
            self.dataBox[3] = max(y, self.dataBox[3])

        self.colorGray = QColor(128, 128, 128)

        self.drawnPoint = set()

        self.threshold = []


    def initUI(self):

        super().initUI('MainBrushCurrentTool')

        self.labelColor = QColor(0, 0, 0)

        size = self.size()
        w = size.width()
        h = size.height()

        h0 = 0
        h1 = h // 3
        h2 = h // 3 * 2
        w0 = 0
        w1 = w // 4
        w2 = w // 2
        w3 = w // 4 * 3

        self.Panel = [[w0, h0], [w1, h0], [w2, h0], [w3, h0],
                      [w0, h1], [w1, h1], [w2, h1], [w3, h1],
                      [w0, h2], [w1, h2], [w2, h2], [w3, h2]]

        self.Scale = min((w1 - self.ChartMargin * 2) / (self.dataBox[2] - self.dataBox[0]),
                         (h1 - self.ChartMargin * 2) / (self.dataBox[3] - self.dataBox[1]))

        # self.Scale = 1

        print(self.dataBox)
        print('scale:', self.Scale)
        print(size)

    def chooseRange(self, idx, dirName):

        self.Threshold = []
        for t in range((idx + 1) * 100, idx * 100 - 1, -10):
            self.Threshold.append(t)
        self.Threshold.append(0)
        self.update()

        img = self.grab()
        img.save(dirName + os.path.sep + str(idx) + ".png", "PNG")


    def closeEvent(self, event):
        event.accept()


    def drawCurrent(self, x, y, c):

        self.qp.setPen(QPen(QColor(255, 0, 0)))
        self.qp.setFont(QFont('Times', 24, QFont.Black))
        self.qp.drawText(x, y, "{0}".format(c))

    def drawCurrentInPanel(self, i, x0, y0, c):

        x = round((x0 - self.dataBox[0]) * self.Scale + self.Panel[i][0] + self.ChartMargin)
        y = round((y0 - self.dataBox[1]) * self.Scale + self.Panel[i][1] + self.ChartMargin)
        self.drawCurrent(x, y, c)


    def drawDataInPanel(self, pt, i, color=None):

        x = round((pt.x - self.dataBox[0]) * self.Scale + self.Panel[i][0] + self.ChartMargin)
        y = round((pt.y - self.dataBox[1]) * self.Scale + self.Panel[i][1] + self.ChartMargin)

        key = ((x << 16) | y)

        if key in self.drawnPoint:
            return

        self.drawPoint(int(x), int(y), color)
        self.drawnPoint.add(key)


    def drawLabel(self):
        self.qp.setPen(self.labelColor)
        for i in range(len(self.Panel)):
            self.qp.drawText(self.Panel[i][0] + self.LabelOffset[0], self.Panel[i][1] + self.LabelOffset[1],
                             "Threshold {0}".format(self.Threshold[i]))


    def paintObjects(self):

        self.drawLabel()

        self.drawnPoint.clear()

        for pt in self.dataArray:
            current = pt.v
            for i in range(len(self.Panel)):
                if current >= self.Threshold[i]:
                    self.drawDataInPanel(pt, i, self.colorGray)

        for th in self.threshold:
            self.drawCurrentInPanel(0, th[0], th[1], th[2])

    def drawPoint(self, x, y, color):

        self.qp.setBrush(color)
        self.qp.drawRect(x, y, round(2 * self.Scale), round(2 * self.Scale))
        # self.qp.drawEllipse(x, y, 2 * self.Scale, 2 * self.Scale)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    fileName = os.path.abspath(sys.argv[1])
    dirName = os.path.dirname(fileName)
    mbSpeed = int(sys.argv[2])
    parser = NavNormalParser(fileName)
    data = parser.getMainBrushData(mbSpeed)

    print(ColorControl.BrFgGreen)
    print("fileName: {}".format(fileName))
    print("record count: {}".format(len(data)))
    print(ColorControl.End)

    ex = MainBrushCurrentTool(data)

    for i in range(10):
        ex.chooseRange(i, dirName)

    # sys.exit(app.exec_())
    sys.exit(0)
