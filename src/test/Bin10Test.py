import sys

from PyQt5.QtWidgets import QApplication

from src.modules import Bin10Parser, TimeCost
from src.modules.DirectoryOpener import DirectoryOpener

if __name__ == '__main__':
    app = QApplication(sys.argv)

    dirOpener = DirectoryOpener(None, "LowObsMapPlayer")
    dirName = dirOpener.getPath()

    tc = TimeCost()

    bin10File = dirName + "/NAV_binId10.log"
    print(f"Bin10File: {bin10File}")
    bin10Parser = Bin10Parser(bin10File)

    for data in bin10Parser.frontFloodData:

        print(data.timestamp)

    print("  open time cost: {}".format(tc.countDown()))

    sys.exit(app.exec_())