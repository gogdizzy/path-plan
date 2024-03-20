import time

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QFileDialog, QApplication, QRadioButton, QPushButton, QTextEdit, \
    QLineEdit
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
import numpy as np
import sys

from src.utils import GridCanvas


class MainBrushCurrent(GridCanvas):


    LabelOffset = [100, 30]
    ChartMargin = 50
    OffsetX = 100
    OffsetY = 30

    Threshold = [400, 390, 380, 370,
                 360, 350, 340, 330,
                 320, 310, 300, 0]


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
        red = round((float(current) / 400.0 - 0.5) * 255.0)
        if red < 0:
            red = 0
        elif red > 255:
            red = 255
        # red = np.clip(round((float(current) / 400.0 - 0.5) * 255.0), 0, 255)
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
                current = int(data[2])
                # print("xyc:", x, y, current)
                self.dataArray.append([x, y, current])
                self.dataBox[0] = min(x, self.dataBox[0])
                self.dataBox[1] = min(y, self.dataBox[1])
                self.dataBox[2] = max(x, self.dataBox[2])
                self.dataBox[3] = max(y, self.dataBox[3])

        print(self.dataBox)
        self.drawCnt = 0

        self.colorGray = QColor(128, 128, 128)
        self.colorTable = []
        for current in range(5000):
            self.colorTable.append(self.calcColor(current))

        self.drawnPoint = set()
        self.BackgroundValue = 200

        self.pointFather = {}
        self.threshold = []


    def initUI(self):

        self.raidoButtons = []
        for i in range(10):
            name = "{}~{}".format(i*100, (i+1)*100)
            button = QRadioButton(name, self)
            button.move(i*100+100, 0)
            button.clicked.connect(self.chooseRange)
            self.raidoButtons.append(button)

        self.backgroundValueText = QLineEdit(self)
        self.backgroundValueText.move(1150, 0)

        self.calcButton = QPushButton('Calc', self)
        self.calcButton.move(1300, 0)
        self.calcButton.clicked.connect(self.calcThreshold)

        super().initUI('MainBrushCurrent')

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


    def getFather(self, x):

        f = self.pointFather.get(x, x)
        if f == x:
            return f

        self.pointFather[x] = self.getFather(f)
        return self.pointFather[x]

    def mergeFather(self, x, y):

        xf = self.getFather(x)
        yf = self.getFather(y)
        if xf != yf:
            self.pointFather[yf] = xf


    def calcThreshold(self):

        # self.mergeFather(1, 2)
        # self.mergeFather(3, 4)
        # self.mergeFather(2, 4)
        #
        # for i in range(5):
        #     print("test: {} {}".format(i, self.getFather(i)))

        self.pointFather.clear()
        self.BackgroundValue = int(self.backgroundValueText.text())
        print("BackgroundValue: {}".format(self.BackgroundValue))

        map2 = {}
        tot = 0
        for i, data in enumerate(self.dataArray):
            x, y, c = data
            if c <= self.BackgroundValue:
                continue
            # print(x, y, c)
            key = ((x & 0xFFFF) << 16) + (y & 0xFFFF)
            for nx in range(x - 3, x + 4):
                for ny in range(y - 3, y + 4):
                    nkey = ((nx & 0xFFFF) << 16) + (ny & 0xFFFF)
                    nval = map2.get(nkey)
                    if nval is not None:
                        self.mergeFather(nval, i)
                        # print("merge {} {}".format(nval, i))
            map2[key] = i
            tot += 1

        fathers = set()
        for i in map2.values():
            fathers.add(self.getFather(i))

        print("tot: {} -> {}".format(tot, len(fathers)))

        self.threshold.clear()
        for f in fathers:

            rg = dict()
            datas = []
            for i, data in enumerate(self.dataArray):
                if f == self.getFather(i):
                    datas.append(i)
                    c = self.dataArray[i][2]
                    c = c - c % 10
                    rg[c] = rg.get(c, 0) + 1

            if len(datas) < 50:
                continue

            vis = set()
            for i in datas:
                x, y, c = self.dataArray[i]
                # print(x, y, c)
                key = ((x & 0xFFFF) << 16) + (y & 0xFFFF)
                vis.add(key)

            pointCnt = len(datas)
            totArea = len(vis)
            vis.clear()
            print("pointCnt: {}  totArea: {}".format(pointCnt, totArea))

            datas.sort(key=lambda z: self.dataArray[z][2], reverse=True)
            print(list(map(lambda z: self.dataArray[z][2], datas)))
            tot = 0
            idx = 0

            found = False
            for c in range(1200, 100, -10):
                cnt = rg.get(c, 0)
                tot += cnt
                while idx < pointCnt:
                    x, y, c2 = self.dataArray[datas[idx]]
                    if c2 >= c:
                        key = ((x & 0xFFFF) << 16) + (y & 0xFFFF)
                        vis.add(key)
                        idx += 1
                    else:
                        break

                print("{} {} {:.3f} {:.3f} {:.3f}".format(c, cnt, cnt / pointCnt, tot / pointCnt, len(vis) / totArea))

                if not found:
                    if len(vis) >= totArea * 0.75 or (len(vis) >= totArea * 0.70 and cnt / pointCnt < 0.015):
                        print("group {} {} {} {} {}".format(f, len(datas), x, y, c + 10))
                        self.threshold.append([x, y, c + 10])
                        found = True



            # vis.clear()
            # for i in datas:
            #     x, y, c = self.dataArray[i]
            #     key = ((x & 0xFFFF) << 16) + (y & 0xFFFF)
            #     vis.add(key)
            #     if len(vis) >= totArea * 0.75:
            #         print("group {} {} {} {} {}".format(f, len(datas), x, y, c))
            #         self.threshold.append([x, y, c])
            #         # self.drawCurrentInPanel(0, x, y, c)
            #         break

        print('finish')
        self.update()


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

        img = self.grab()

        img.save("/Users/guanxin/11.png", "PNG")


    def closeEvent(self, event):
        event.accept()


    def drawCurrent(self, x, y, c):

        self.qp.setPen(QPen(QColor(255, 0, 0)))
        self.qp.setFont(QFont('Times', 24, QFont.Black))
        self.qp.drawText(x, y, "{0}".format(c))

    def drawCurrentInPanel(self, i, x0, y0, c):

        x = round((x0 - self.dataBox[0]) * self.Scale + self.Panel[i][0] + self.ChartMargin)
        y = round((y0 - self.dataBox[1]) * self.Scale + self.Panel[i][1] + self.ChartMargin)

        # print("will draw at {} {}".format(x, y))

        self.drawCurrent(x, y, c)


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
        # print("drawCnt: ", self.drawCnt, " dur: ", edTime - stTime)

        for th in self.threshold:
            self.drawCurrentInPanel(0, th[0], th[1], th[2])

        # for data in [[6,144,10], [7,144,10],[8,144,10],[9,144,10],[26, 144, 10]]:
        #     self.drawDataInPanel(data, 11, QColor(255, 0, 0))
        # self.drawPoint(6, 144, QColor(255, 0, 0))
        # self.drawPoint(26, 144, QColor(255, 0, 0))


    def drawPoint(self, x, y, color):

        self.qp.setBrush(color)
        self.qp.drawRect(x, y, 2 * self.Scale, 2 * self.Scale)
        # self.qp.drawEllipse(x, y, 2 * self.Scale, 2 * self.Scale)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainBrushCurrent()
    sys.exit(app.exec_())
