from enum import IntEnum

from src.geometry import Point2D
from src.modules import TimeAndPoints, Pose2DAndValue

class NavNormalTypes(IntEnum):

    LowObsMapAllNearObs = 0
    LowObsMapNearObs = 1
    LowObsMapNewObs = 2
    LowObsMapNewLooseWireObs = 3
    LowObsMapNewVlineObs = 4
    LowObsMapNewVlineSpace = 5
    LowObsMapNewVlineData = 6
    LowObsMapNewHighObs = 7


class NavNormalParser:

    def __init__(self, filename):

        self.filename = filename
        self.subParsers = dict()
        self.subParsers[NavNormalTypes.LowObsMapAllNearObs] = NavNormalParser.parseLowObsMapAllNearObs
        self.subParsers[NavNormalTypes.LowObsMapNearObs] = NavNormalParser.parseLowObsMapNearObs
        self.subParsers[NavNormalTypes.LowObsMapNewObs] = NavNormalParser.parseLowObsMapNewObs
        self.subParsers[NavNormalTypes.LowObsMapNewLooseWireObs] = NavNormalParser.parseLowObsMapNewLooseWireObs
        self.subParsers[NavNormalTypes.LowObsMapNewVlineObs] = NavNormalParser.parseLowObsMapNewVlineObs
        self.subParsers[NavNormalTypes.LowObsMapNewVlineSpace] = NavNormalParser.parseLowObsMapNewVlineSpace
        self.subParsers[NavNormalTypes.LowObsMapNewVlineData] = NavNormalParser.parseLowObsMapNewVlineData
        self.subParsers[NavNormalTypes.LowObsMapNewHighObs] = NavNormalParser.parseLowObsMapNewHighObs

    def parse(self, dic):

        items = dic.items()
        subParsers = self.subParsers
        with open(self.filename, mode="r") as file:
            for line in file:
                for tp, data in items:
                    subParsers[tp](line, data)

    @staticmethod
    def parseLowObsMapAllNearObs(line, data):

        if "allNearPts" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "allNearPts:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y = map(int, parts[i].split(","))
                    points.append(Point2D(x, y))

                data.append(TimeAndPoints(timestamp, points))

    @staticmethod
    def parseLowObsMapNearObs(line, data):

        if "nearObs" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "nearObs:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y, v = map(int, parts[i].split(","))
                    points.append(Pose2DAndValue(x, y, v))

                data.append(TimeAndPoints(timestamp, points))


    @staticmethod
    def parseLowObsMapNewObs(line, data):

        if "newObs" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "newObs:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y, v = map(int, parts[i].split(","))
                    points.append(Pose2DAndValue(x, y, v))

                data.append(TimeAndPoints(timestamp, points))

    @staticmethod
    def parseLowObsMapNewLooseWireObs(line, data):

        if "newLooseWireObs" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "newLooseWireObs:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y, v = map(int, parts[i].split(","))
                    points.append(Pose2DAndValue(x, y, v))

                data.append(TimeAndPoints(timestamp, points))

    @staticmethod
    def parseLowObsMapNewVlineObs(line, data):

        if "vlineObs" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "vlineObs:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y, v = map(int, parts[i].split(","))
                    points.append(Pose2DAndValue(x, y, v))

                data.append(TimeAndPoints(timestamp, points))

    @staticmethod
    def parseLowObsMapNewVlineSpace(line, data):

        if "vlineSpace" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "vlineSpace:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y, v = map(int, parts[i].split(","))
                    points.append(Pose2DAndValue(x, y, v))

                data.append(TimeAndPoints(timestamp, points))

    @staticmethod
    def parseLowObsMapNewVlineData(line, data):

        if "vlineData" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "vlineData:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y = map(float, parts[i].split(","))
                    points.append(Point2D(x, y))

                data.append(TimeAndPoints(timestamp, points))

    @staticmethod
    def parseLowObsMapNewHighObs(line, data):

        if "highObs" in line and "LowObsMap" in line:
            points = []
            parts = line.split(" ")
            if parts[6] == "highObs:":
                timestamp = int(parts[1])
                for i in range(7, len(parts) - 1):  # tail is space
                    x, y, v = map(int, parts[i].split(","))
                    points.append(Pose2DAndValue(x, y, v))

                data.append(TimeAndPoints(timestamp, points))


    def getCamera2DPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "Camera2DBumper" in line and "Input data" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "data:":
                        timestamp = int(parts[0].split(",")[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    elif parts[7] == "data:":
                        timestamp = int(parts[1])
                        for i in range(8, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoints(timestamp, points))

        return res

    def getGotoObsPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "nearObs" in line and "GotoObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "nearObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoints(timestamp, points))

        return res


    def getGotoObsPointsBeforeMix(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "before mix" in line and "GotoFollowRouting" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[7] == "mix:":
                        timestamp = int(parts[1])
                        for i in range(8, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoints(timestamp, points))

        return res

    def getGotoObsPointsAfterMix(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "after mix" in line and "GotoFollowRouting" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[7] == "mix:":
                        timestamp = int(parts[1])
                        for i in range(8, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoints(timestamp, points))

        return res

    def getLowObsPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "nearObs" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "nearObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y, v = map(int, parts[i].split(","))
                            points.append(Pose2DAndValue(x, y, v))

                    res.append(TimeAndPoints(timestamp, points))

        return res

    def getNewObs(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "newObs" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "newObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y, v = map(int, parts[i].split(","))
                            points.append(Pose2DAndValue(x, y, v))

                        res.append(TimeAndPoints(timestamp, points))

        return res


    def getAllNearObs(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "allNearPts" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "allNearPts:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                        res.append(TimeAndPoints(timestamp, points))

        return res


    def getNewLooseWireObs(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "newLooseWireObs" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "newLooseWireObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y, v = map(int, parts[i].split(","))
                            points.append(Pose2DAndValue(x, y, v))

                        res.append(TimeAndPoints(timestamp, points))

        return res


    def getNewVlineObs(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "vlineObs" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "vlineObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y, v = map(int, parts[i].split(","))
                            points.append(Pose2DAndValue(x, y, v))

                        res.append(TimeAndPoints(timestamp, points))

        return res


    def getNewVlineSpace(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "vlineSpace" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "vlineSpace:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y, v = map(int, parts[i].split(","))
                            points.append(Pose2DAndValue(x, y, v))

                        res.append(TimeAndPoints(timestamp, points))

        return res


    def getHighObs(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "highObs" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "highObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y, v = map(int, parts[i].split(","))
                            points.append(Pose2DAndValue(x, y, v))

                        res.append(TimeAndPoints(timestamp, points))

        return res


    def getVLineData(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "vlineData" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "vlineData:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):  # tail is space
                            x, y = map(float, parts[i].split(","))
                            points.append(Point2D(x, y))

                        res.append(TimeAndPoints(timestamp, points))

        return res

    def getEasyStuckPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "EasyStuckPoint" in line and "StereoVision" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "EasyStuckPoint:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoints(timestamp, points))

        return res

    def getMainBrushData(self, mainBrushSpeed):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "maybeOnCarpet" in line and "CarpetDetectorByCurrent" in line:
                    parts = line.split(" ")
                    offset = 5
                    if parts[5] == "maybeOnCarpet":
                        offset = 5
                    elif parts[6] == "maybeOnCarpet":
                        offset = 6

                    avgCurrent = int(parts[offset + 2])
                    mbSpeed = int(parts[offset + 7])

                    if avgCurrent > 50 and mbSpeed == mainBrushSpeed:

                        x = int(parts[offset + 22])
                        if parts[offset + 23][-1] == ',':
                            parts[offset + 23] = parts[offset + 23][0:-1]
                        y = int(parts[offset + 23])

                        res.append(Pose2DAndValue(x, y, avgCurrent))

        return res


    def getBin5LaserPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                points = []
                parts = line.split(" ")
                if parts[6] != "":
                    timestamp = int(parts[0])
                    for i in range(6, len(parts) - 1):   # tail is space
                        x, y = map(int, parts[i].split(","))
                        points.append(Point2D(x, y))

                res.append(TimeAndPoints(timestamp, points))

        return res





