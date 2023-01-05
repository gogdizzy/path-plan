import struct
import numpy as np


class GridMap:

    def __init__(self, w=0, h=0):

        self.mapWidth = w
        self.mapHeight = h
        self.mapData = np.zeros((self.mapWidth, self.mapHeight), dtype=int)

    def loadData(self, filename):

        if not filename:
            return

        with open(filename, mode="rb") as file:
            self.mapWidth, self.mapHeight = struct.unpack('ii', file.read(8))
            self.mapData = np.zeros((self.mapWidth, self.mapHeight), dtype=int)
            for y in range(0, self.mapHeight):
                for x in range(0, self.mapWidth):
                    self.mapData[x][y] = struct.unpack('i', file.read(4))[0]

    def saveData(self, filename):

        if not filename:
            return

        with open(filename, mode="wb") as file:
            file.write(struct.pack('ii', self.mapWidth, self.mapHeight))
            for y in range(0, self.mapHeight):
                for x in range(0, self.mapWidth):
                    file.write(struct.pack('i', self.mapData[x][y]))
