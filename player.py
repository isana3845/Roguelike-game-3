from file import Vector2


class Player:
    def __init__(self, coords: Vector2, health: int, armor: int):
        self.position = coords
        self.health = health
        self.armor = armor

    def move(self, direction: Vector2):
        self.position += direction



class Enemy(Player):
    def __init__(self, coords, health, armor):
        super().__init__(coords, health, armor)


class Inventory:
    def __init__(self, capacity: int):
        self.capacity = capacity
