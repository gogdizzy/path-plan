import os
import struct
from enum import IntEnum


class Bin10Types(IntEnum):

    Bin10Type_Old = 0xF0DC0132
    Bin10Type_OldLeft = 0xF1DC0132
    Bin10Type_WidthBrightness = 0xF2DC0132
    Bin10Type_FlagStatus = 0xF3DC0132
    Bin10Type_PixelXY = 0xF4DC0132
    Bin10Type_ToF = 0xF5DC0132
    Bin10Type_ToFLeft = 0xF6DC0132
    Bin10Type_FlagStatusPixelXY = 0xF7DC0132
    Bin10Type_ToFWithStructure = 0xF8DC0132
    Bin10Type_ToFPerc = 0xF9DC0132
    Bin10Type_ToFWithExpose = 0xFADC0132
    Bin10Type_ToFSplitPerc = 0xFBDC0132
    Bin10Type_TofWithClass = 0xFCDC0132
    Bin10Type_TofWithClusterId = 0xFDDC0132
    Bin10Type_TofLooseWire = 0xFEDC0132
    Bin10Type_TofPercWithClassify = 0xFFDC0132


class Bin10Pos:

    def __init__(self, x = 0, y = 0, bearing = 0):
        self.x = x                 # int32
        self.y = y                 # int32
        self.bearing = bearing     # double

    def readFrom(self, fp):

        self.x, self.y, self.bearing = struct.unpack("iid", fp.read(16))


class Bin10HeaderBase:

    def __init__(self, dType = Bin10Types.Bin10Type_ToF, timestamp = 0, robotPos = None, odoPos = None, yawSpeed = 0):

        self.type = dType              # uint32
        self.timestamp = timestamp     # uint32
        self.robotPos = Bin10Pos() if robotPos is None else robotPos       # Bin10Pos
        self.odoPos = Bin10Pos() if odoPos is None else odoPos             # Bin10Pos
        self.yawSpeed = yawSpeed       # float32

    def readFrom(self, fp):

        self.type, self.timestamp = struct.unpack("II", fp.read(8))
        self.robotPos.readFrom(fp)
        self.odoPos.readFrom(fp)
        # print("robotPos: {} {} {}".format(self.robotPos.x, self.robotPos.y, self.robotPos.bearing))
        self.yawSpeed, = struct.unpack("f", fp.read(4))


class Bin10PointToF:

    def __init__(self, x = 0, y = 0, z = 0, clusterId = 0):

        self.x = x                    # int16
        self.y = y                    # int16
        self.z = z                    # int16

    def readFrom(self, fp):

        self.x, self.y, self.z = struct.unpack("hhh", fp.read(6))


class Bin10HeaderToFLooseWire(Bin10HeaderBase):

    def __init__(self):

        super().__init__()
        self.pointCount = 0           # uint32
        self.points = []

    def readFrom(self, fp):

        super().readFrom(fp)

        self.pointCount, = struct.unpack("I", fp.read(4))

        for i in range(self.pointCount):

            p = Bin10PointToF()
            p.readFrom(fp)
            self.points.append(p)


class Bin10PointToFCompactWithConfidence:

    def __init__(self, x = 0, y = 0, z = 0, amplitude = 0, originalIndex = 0, confidence = 0):
        self.x = x                             # int16
        self.y = y                             # int16
        self.z = z                             # int16
        self.amplitude = amplitude             # uint16
        self.originalIndex = originalIndex     # uint16
        self.confidence = confidence           # float32

    def readFrom(self, fp):

        self.x, self.y, self.z, self.amplitude, self.originalIndex, self.confidence = struct.unpack("<hhhHHf", fp.read(14))


class Bin10HeaderToFWithExpose(Bin10HeaderBase):

    def __init__(self):

        super().__init__()
        self.dataType = 0           # uint32
        self.isLeftToF = False
        self.isPercPoint = False
        self.exposeTime = 0         # uint32
        self.pointCount = 0         # int32
        self.points = []

    def readFrom(self, fp):

        super().readFrom(fp)

        bitfield, self.exposeTime, self.pointCount = struct.unpack("IIi", fp.read(12))
        self.dataType = (bitfield & 0xF)
        self.isLeftToF = ((bitfield >> 4) & 0x1)
        self.isPercPoint = ((bitfield >> 5) & 0x1)

        for i in range(self.pointCount):

            p = Bin10PointToFCompactWithConfidence()
            p.readFrom(fp)
            self.points.append(p)


class Bin10PointToFWithClusterId:

    def __init__(self, x = 0, y = 0, z = 0, clusterId = 0):

        self.x = x                    # int16
        self.y = y                    # int16
        self.z = z                    # int16
        self.clusterId = clusterId    # uint16

    def readFrom(self, fp):

        self.x, self.y, self.z, self.clusterId = struct.unpack("hhhH", fp.read(8))

class Bin10PointToFWithCorrectZAndClusterId:

    def __init__(self, x = 0, y = 0, z = 0, correctZ = 0, clusterId = 0):

        self.x = x                    # int16
        self.y = y                    # int16
        self.z = z                    # int16
        self.correctZ = correctZ      # int16
        self.clusterId = clusterId    # uint16

    def readFrom(self, fp):

        self.x, self.y, self.z, self.correctZ, self.clusterId = struct.unpack("hhhhH", fp.read(10))

class Bin10HeaderToFWithClusterId(Bin10HeaderBase):

    def __init__(self):

        super().__init__()
        self.classifyCount = [0, 0, 0, 0]
        self.reserverd = [0, 0, 0, 0, 0, 0]
        self.pointCount = 0
        self.points = []

    def readFrom(self, fp):

        super().readFrom(fp)
        self.classifyCount[0], self.classifyCount[1], self.classifyCount[2], self.classifyCount[3] = struct.unpack("HHHH", fp.read(8))
        fp.read(24)      # reserved
        self.pointCount, = struct.unpack("i", fp.read(4))

        for i in range(self.pointCount):
            p = Bin10PointToFWithClusterId()
            p.readFrom(fp)
            self.points.append(p)


class Bin10HeaderToFWithCorrectZAndClusterId(Bin10HeaderBase):

    def __init__(self):

        super().__init__()
        self.classifyCount = [0, 0, 0, 0, 0, 0]
        self.reserverd = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.subVersion = 0
        self.sizeofPoint = 0
        self.pointCount = 0
        self.points = []

    def readFrom(self, fp):

        super().readFrom(fp)
        for i in range(6):
            self.classifyCount[i], = struct.unpack("H", fp.read(2))
        fp.read(18)      # reserved
        self.subVersion, self.sizeofPoint, self.pointCount = struct.unpack("<BBi", fp.read(6))

        for i in range(self.pointCount):
            p = Bin10PointToFWithCorrectZAndClusterId()
            p.readFrom(fp)
            self.points.append(p)

class Bin10Parser:

    def __init__(self, filename, startTimestamp = 0):

        self.leftSpotData = []
        self.frontSpotData = []
        self.frontFloodData = []

        with open(filename, mode="rb") as fp:

            fp.seek(0, 2)
            filesize = fp.tell()
            fp.seek(0, 0)

            while fp.tell() < filesize:

                magic, = struct.unpack("I", fp.read(4))

                # print("magic: {:X} {}".format(magic, magic))
                if magic != Bin10Types.Bin10Type_TofWithClusterId and \
                   magic != Bin10Types.Bin10Type_ToFWithExpose and \
                   magic != Bin10Types.Bin10Type_TofPercWithClassify and \
                   magic != Bin10Types.Bin10Type_TofLooseWire:

                    os.abort()

                fp.seek(-4, 1)

                if magic == Bin10Types.Bin10Type_ToFWithExpose:

                    data = Bin10HeaderToFWithExpose()
                    data.readFrom(fp)

                    if data.timestamp < startTimestamp:
                        continue

                    if data.isLeftToF:
                        self.leftSpotData.append(data)

                    else:
                        self.frontSpotData.append(data)

                    # print("Spot {}".format("Left" if data.isLeftToF else "Front"))

                elif magic == Bin10Types.Bin10Type_TofWithClusterId:

                    data = Bin10HeaderToFWithClusterId()
                    data.readFrom(fp)

                    if data.timestamp < startTimestamp:
                        continue

                    self.frontFloodData.append(data)

                elif magic == Bin10Types.Bin10Type_TofPercWithClassify:

                    data = Bin10HeaderToFWithCorrectZAndClusterId()
                    data.readFrom(fp)

                    if data.timestamp < startTimestamp:
                        continue

                    self.frontFloodData.append(data)

                    # print("Flood Front")

                elif magic == Bin10Types.Bin10Type_TofLooseWire:

                    data = Bin10HeaderToFLooseWire()
                    data.readFrom(fp)



            print("Left Spot: {}".format(len(self.leftSpotData)))
            print("Front Spot: {}".format(len(self.frontSpotData)))
            print("Front Flood: {}".format(len(self.frontFloodData)))

