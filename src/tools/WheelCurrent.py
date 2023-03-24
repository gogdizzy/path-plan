import time

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QFileDialog, QApplication, QRadioButton
from PyQt5.QtGui import QPainter, QColor
import numpy as np
import sys

from src.utils import GridCanvas


class WheelCurrent(GridCanvas):

    LabelOffset = [100, 30]
    ChartMargin = 50
    OffsetX = 100
    OffsetY = 30

    Threshold = [400, 390, 380, 370,
                 360, 350, 340, 330,
                 320, 310, 300, 0]  # slow

    def __init__(self):

        super().__init__()

        self.initData()
        self.initUI()

    def __del__(self):
        if self.fp:
            print('will close fp')
            self.fp.close()

    def calcPos(self, posStr):
        return round(float(posStr) / 50.0)

    def calcColor(self, current):
        red = np.clip(round((float(current) / 400.0 - 0.5) * 255.0), 0, 255)
        return QColor(red, red, red)

    def initData(self):

        qSettings = QSettings()
        lastPath = qSettings.value("LastFilePath")
        filename, choosed = QFileDialog.getOpenFileName(self, 'Open file', lastPath)

        if not choosed:
            sys.exit(-1)

        qSettings.setValue("LastFilePath", filename)

        self.dataArray = []
        self.dataBox = [2000, 2000, -2000, -2000]
        with open(filename, mode='rt') as fp:
            for line in fp.readlines():
                data = line.split(" ")
                x = self.calcPos(data[0])
                y = self.calcPos(data[1])
                current = int(float(data[2]))
                self.dataArray.append([x, y, current])
                self.dataBox[0] = min(x, self.dataBox[0])
                self.dataBox[1] = min(y, self.dataBox[1])
                self.dataBox[2] = max(x, self.dataBox[2])
                self.dataBox[3] = max(y, self.dataBox[3])

        print(self.dataBox)


    def initUI(self):

        self.raidoButtons = []
        for i in range(10):
            name = "{}~{}".format(i * 100, (i + 1) * 100)
            button = QRadioButton(name, self)
            button.move(i * 100 + 100, 0)
            button.clicked.connect(self.chooseRange)
            self.raidoButtons.append(button)

        super().initUI('WheelCurrent')

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

        # self.Scale = 1.7

        print(self.dataBox)
        print('scale:', self.Scale)
        print(size)

        self.drawCnt = 0
        self.colorGray = QColor(128, 128, 128)
        self.drawnPoint = set()


    def chooseRange(self):

        for i in range(len(self.raidoButtons)):
            if self.raidoButtons[i].isChecked():
                print('choose range: ', i)
                self.Threshold = []
                for t in range((i + 1) * 100, i * 100 - 1, -10):
                    self.Threshold.append(t)
                self.Threshold.append(0)
                print(self.Threshold)

        self.update()


    def closeEvent(self, event):
        event.accept()


    def drawDataInPanel(self, data, i, color=None):

        x = round((data[0] - self.dataBox[0]) * self.Scale + self.Panel[i][0] + self.ChartMargin)
        y = round((data[1] - self.dataBox[1]) * self.Scale + self.Panel[i][1] + self.ChartMargin)

        key = ((x << 16) | y)

        if key in self.drawnPoint:
            return

        self.drawPoint(x, y, color)
        self.drawnPoint.add(key)
        self.drawCnt += 1


    def drawLabel(self):
        self.qp.setPen(self.labelColor)
        for i in range(len(self.Panel)):
            self.qp.drawText(self.Panel[i][0] + self.LabelOffset[0], self.Panel[i][1] + self.LabelOffset[1],
                             "Threshold {0}".format(self.Threshold[i]))


    def paintObjects(self):

        self.drawLabel()

        stTime = time.perf_counter()
        self.drawnPoint.clear()
        self.drawCnt = 0
        for data in self.dataArray:
            current = data[2]
            for i in range(len(self.Panel)):
                # for i in range(1):
                if current >= self.Threshold[i]:
                    self.drawDataInPanel(data, i, self.colorGray)

        edTime = time.perf_counter()
        print("drawCnt: ", self.drawCnt, " dur: ", edTime - stTime)


    def drawPoint(self, x, y, color):

        self.qp.setBrush(color)
        self.qp.drawRect(x, y, 2 * self.Scale, 2 * self.Scale)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = WheelCurrent()
    sys.exit(app.exec_())
