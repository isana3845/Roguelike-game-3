import keyboard
import time
import os
from file import Vector2


map_width = 10
map_height = 10

class Map:
    def __init__(self, height = map_height, width = map_width):
        self.height = height
        self.width = width

    def draw_map(self, player, enemies):
        mapa = []
        for i in range(self.height):
            mapa.append(["." for j in range(self.width)])

        try:
            mapa[player.y()][player.x()] = "@"
        except IndexError:
            pass

        for enemy in enemies:
            mapa[enemy.y()][enemy.x()] = "&"
        
        mapa = "\n".join(list(map(lambda x: " ".join(x), mapa)))

        print(mapa)
    

class Player:
    def __init__(self, coords: Vector2, health: int, strength: int, speed: int):
        self.position = coords
        self.health = health
        self.strength = strength
        self.speed = speed
    
    def move(self, direction: Vector2):
        self.position += direction
        self.position.x = max(0, min(self.x(), map_width-1))
        self.position.y = max(0, min(self.y(), map_height-1))

    def x(self):
        return self.position.x

    def y(self):
        return self.position.y

    def attack(self, enemy):
        if enemy.health > 0:
            enemy.health -= self.strength
    
    def __repr__(self):
        return f"Entity position: {self.position}; Health: {self.health}"
    
    def __contains__(self, coords: Vector2):
        return coords == self.position

class Enemy(Player):
    def __init__(self, coords, health, strength, speed):
        super().__init__(coords, health, strength, speed)
    

m = Map(height=map_height, width=map_width)



ilya = Player(Vector2(1, 5), 10**(-5), 10**9, 9)
kirill = Enemy(Vector2(4, 2), 10**9 + 1, 4, 9)

while True:
    ilya.move(Vector2(keyboard.is_pressed("d") * 1 + keyboard.is_pressed("a")*(-1), keyboard.is_pressed("w") * (-1) + keyboard.is_pressed("s")*1))
    if keyboard.is_pressed("esc"):
        break
    m.draw_map(ilya, [kirill])
    time.sleep(0.5)
    os.system("cls")

