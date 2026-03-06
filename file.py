import keyboard
import time


class Vector2:
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def normalize(self):
        absolute = abs(self)
        self.x /= absolute
        self.y /= absolute
        self.z /= absolute
        return Vector2(self.x / absolute, self.y / absolute)

    def __contains__(self, item):
        return item in [self.x, self.y]

    def __repr__(self):
        return f"X: {self.x} Y: {self.y}"
    
    @staticmethod
    def up(direction = -1):
        return Vector2(0, -1*direction)

    @staticmethod
    def right(direction = 1):
        return Vector2(1*direction, 0)

    def __eq__(self, value):
        return self.x == value.x and self.y == value.y

    def __bool__(self):
        return Vector2(0, 0) != self
        
    def __add__(self, vec):
        return Vector2(self.x + vec.x, self.y + vec.y)
    
    def __sub__(self, vec):
        return Vector2(self.x - vec.x, self.y - vec.y)

    def __abs__(self):
        return (self.x**2 + self.y**2)**0.5