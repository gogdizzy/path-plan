import sys

from PyQt5.QtWidgets import QApplication

from src.modules import FileOpener, NavNormalParser, ColorControl
from src.tools import ObstaclePlayer

if __name__ == '__main__':

    app = QApplication(sys.argv)

    fileOpener = FileOpener(None, "EasyStuckPointPlayer")
    fileName = fileOpener.getPath()
    parser = NavNormalParser(fileName)
    data = parser.getEasyStuckPoints()

    print(ColorControl.BrFgGreen)
    print("fileName: {}".format(fileName))
    print("record count: {}".format(len(data)))
    print(ColorControl.End)

    ex = ObstaclePlayer(data)

    sys.exit(app.exec_())
