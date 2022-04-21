from src.algo import AStar
from src.geometry import Point2D, SimpleRect


startPoint = Point2D(0, 0)
goalPoint = Point2D(10, 10)
box = SimpleRect(0, 0, 255, 255)
# algo = AStar(startPoint, goalPoint, box)
algo = AStar(startPoint, goalPoint, box,
             lambda x0, y0, x1, y1: 1 if abs(x0-x1) + abs(y0-y1) == 1 else 10)
path = algo.search()
print(path)

