from file import Vector2


class Player:
    def __init__(self, coords: Vector2, health: int, armor: int):
        self.position = coords
        self.health = health
        self.armor = armor

    def move(self, direction: Vector2):
        self.position += direction

class Interface:
    def __init__(self, player: Player):
        self.player = player
    def __call__(self):
        print(f"HP: {self.player.health} Armor: {self.player.armor}")


#this is for you :3 TODO

class Enemy(Player):
    def __init__(self, coords, health, armor, type):
        super().__init__(coords, health, armor)
        self.type = type
    
    


class Inventory:
    def __init__(self, capacity: int):
        self.capacity = capacity
