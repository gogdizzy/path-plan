
class RobotModel:

    def __init__(self, robotR, robotRWithGlue, rightBrushXOffset, rightBrushYOffset, rightBrushR):

        self.robotR = robotR
        self.robotRwithGlue = robotRWithGlue
        self.rightBrushXOffset = rightBrushXOffset
        self.rightBrushYOffset = rightBrushYOffset
        self.rightBrushR = rightBrushR

    @staticmethod
    def getModel_1():

        return RobotModel(175, 178.5, 92, -113, 73)

    @staticmethod
    def getModel_2():

        return RobotModel(175, 178.5, 97, -117, 73)
