import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog


class FileOpener:

    def __init__(self, widget, cacheKeyName):

        qSettings = QSettings()
        lastPath = qSettings.value(cacheKeyName)
        filename, choosed = QFileDialog.getOpenFileName(widget, 'Open file', lastPath)

        if not choosed:
            sys.exit(-1)

        qSettings.setValue(cacheKeyName, filename)
        self.path = filename

    def getPath(self):

        return self.path