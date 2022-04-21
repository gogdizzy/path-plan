
class SimpleRect:

    def __init__(self, left=0, bottom=0, right=0, top=0):

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def __str__(self):

        return f'({self.left},{self.bottom},{self.right},{self.top})'

    def __repr__(self):

        return f'({self.left},{self.bottom},{self.right},{self.top})'

    def width(self):

        return self.right - self.left + 1

    def widthWithX(self, x):

        return max(self.right, x) - min(self.left, x) + 1

    def height(self):

        return self.top - self.bottom + 1

    def heightWithY(self, y):

        return max(self.top, y) - min(self.bottom, y) + 1

    def expand(self, x, y):

        if x < self.left:
            self.left = x
        if x > self.right:
            self.right = x
        if y < self.bottom:
            self.bottom = y
        if y > self.top:
            self.top = y

    def contains(self, x, y):

        return self.left <= x <= self.right and self.bottom <= y <= self.top

