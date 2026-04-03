import sqlite3
import os #👀
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
    

class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        return cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        self.conn.close()
        print("Соединение закрыто")