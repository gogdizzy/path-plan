import sys

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from src.geometry import Point2D
from src.modules import FileOpener, NavNormalParser, ColorControl, RobotModel
from src.tools import ObstaclePlayer

robotX = 1000
robotY = 750
robotModel = RobotModel.getModel_2()

def drawRedzone(qp, data):

    qp.setPen(QColor(0, 200, 200))
    qp.drawEllipse(QPoint(robotX, robotY), robotModel.robotR + 45, robotModel.robotR + 45)
    qp.drawEllipse(QPoint(robotX + robotModel.rightBrushXOffset, robotY + robotModel.rightBrushYOffset),
                   robotModel.rightBrushR + 45, robotModel.rightBrushR + 45)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    fileOpener = FileOpener(None, "Camera2DPointPlayer")
    fileName = fileOpener.getPath()
    parser = NavNormalParser(fileName)
    data = parser.getCamera2DPoints()

    print(ColorControl.BrFgGreen)
    print("fileName: {}".format(fileName))
    print("record count: {}".format(len(data)))
    print(ColorControl.End)

    ex = ObstaclePlayer(data, Point2D(robotX, robotY))
    ex.addCustomFunction(drawRedzone, 1)

    sys.exit(app.exec_())
