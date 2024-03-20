import math

class ShapeToOffsets:

    @staticmethod
    def getCircle(radius):

        offsets = []
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                if math.hypot(x, y) <= radius:
                    offsets.append((x, y))

        return offsets