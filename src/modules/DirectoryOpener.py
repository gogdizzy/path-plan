import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog


class DirectoryOpener:

    def __init__(self, widget, cacheKeyName):

        qSettings = QSettings()
        lastPath = qSettings.value(cacheKeyName)
        dirname = QFileDialog.getExistingDirectory(widget, 'Open dir', lastPath, options=QFileDialog.ShowDirsOnly)

        if not dirname:
            sys.exit(-1)

        qSettings.setValue(cacheKeyName, dirname)
        self.path = dirname

    def getPath(self):

        return self.path