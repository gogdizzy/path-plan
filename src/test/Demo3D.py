import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl


class MyWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.glWidget = gl.GLViewWidget()
        self.setCentralWidget(self.glWidget)
        self.scene = gl.GLGridItem()
        self.glWidget.addItem(self.scene)
        self.cube = gl.GLAxisItem()
        self.glWidget.addItem(self.cube)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())