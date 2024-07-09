import struct
import numpy as np

from src.utils import GridType


class GridMapPPM:

    def __init__(self, w=0, h=0):

        self.mapWidth = w
        self.mapHeight = h
        self.mapData = np.zeros((self.mapWidth, self.mapHeight), dtype=int)

    def loadData(self, filename, trim=True):

        if not filename:
            return

        with open(filename, mode="rb") as file:
            file.readline(128)
            self.mapWidth, self.mapHeight, _ = map(int, file.readline(128).split())
            self.mapData = np.zeros((self.mapWidth, self.mapHeight), dtype=int)
            for y in range(0, self.mapHeight):
                for x in range(0, self.mapWidth):
                    r, g, b = struct.unpack('BBB', file.read(3))
                    if r == 0 and g == 0 and b == 0:
                        # print('{} {} {} {} {}'.format(x, y, r, g, b))
                        self.mapData[x][y] = GridType.Obstacle

            if trim:
                self.trimData()


    def saveData(self, filename):

        if not filename:
            return

        with open(filename, mode="wb") as file:
            file.write(b'P6\n')
            file.write('{} {} 255\n'.format(self.mapWidth, self.mapHeight).encode())
            for y in range(0, self.mapHeight):
                for x in range(0, self.mapWidth):
                    if self.mapData[x][y] == GridType.Obstacle:
                        file.write(struct.pack('BBB', 0, 0, 0))
                    elif self.mapData[x][y] == GridType.Space:
                        file.write(struct.pack('BBB', 255, 255, 255))
                    else:
                        file.write(struct.pack('BBB', 128, 128, 128))

    def trimData(self):

        startX = 0
        endX = self.mapWidth - 1
        startY = 0
        endY = self.mapHeight - 1

        all(all(self.mapData[x][y] == GridType.Default for y in range(0, self.mapHeight)) and (startX := x,) for x in range(0, self.mapWidth))
        all(all(self.mapData[x][y] == GridType.Default for y in range(0, self.mapHeight)) and (endX := x,) for x in range(self.mapWidth - 1, 0, -1))
        all(all(self.mapData[x][y] == GridType.Default for x in range(0, self.mapWidth)) and (startY := y,) for y in range(0, self.mapHeight))
        all(all(self.mapData[x][y] == GridType.Default for x in range(0, self.mapWidth)) and (endY := y,) for y in range(self.mapHeight - 1, 0, -1))

        if startX != 0 or endX != self.mapWidth - 1 or startY != 0 or endY != self.mapHeight - 1:
            oldMapData = self.mapData
            newMapData = np.zeros((endX - startX + 1, endY - startY + 1), dtype=int)
            for x in range(0, newMapData.shape[0]):
                for y in range(0, newMapData.shape[1]):
                    newMapData[x][y] = oldMapData[startX + x][startY + y]
            self.mapWidth = endX - startX + 1
            self.mapHeight = endY - startY + 1
            self.mapData = newMapData
