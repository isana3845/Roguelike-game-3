from random import choice
from player import Player
from file import Vector2
import keyboard
import os


class Map:
    def __init__(self, height=13, width=40):
        self.height = height
        self.width = width
        self.tiles = ['\033[90m#\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[94m~\033[0m']
        self.not_walkable_tiles = ['\033[90m#\033[0m', '#']
        self.original_map = None

    def generate_map(self):
        game_map = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    row.append('#')
                else:
                    row.append(choice(self.tiles))
            game_map.append(row)

        self.original_map = [row.copy() for row in game_map]

        return game_map
    

    def set_player(self, game_map, player: Player):
        for y in range(self.height):
            for x in range(self.width):
                if game_map[y][x] == '\033[93m@\033[0m':
                    game_map[y][x] = self.original_map[y][x]

        game_map[player.position.y][player.position.x] = '\033[93m@\033[0m'

        return game_map
    

    def is_walkable(self, game_map, position: Vector2) -> bool:
        return game_map[position.y][position.x] not in self.not_walkable_tiles

    
    def draw_map(self, game_map):
        for row in game_map:
            print("".join(row))


player = Player(Vector2(1, 1), 10, 2)
game_map = Map()
mapa = game_map.generate_map()
game_map.set_player(mapa, player)
game_map.draw_map(mapa)

while True:
    event = keyboard.read_event()

    if event.event_type == keyboard.KEY_UP:
        match event.name:
            case 'w':
                if game_map.is_walkable(mapa, player.position + Vector2(0, -1)):
                    player.move(Vector2(0, -1))
            case 'a':
                if game_map.is_walkable(mapa, player.position + Vector2(-1, 0)):
                    player.move(Vector2(-1, 0))
            case 's':
                if game_map.is_walkable(mapa, player.position + Vector2(0, 1)):
                    player.move(Vector2(0, 1))
            case 'd':
                if game_map.is_walkable(mapa, player.position + Vector2(1, 0)):
                    player.move(Vector2(1, 0))
            case 'esc':
                break
    else:
        continue
    
    
    os.system("cls")
    game_map.set_player(mapa, player)
    game_map.draw_map(mapa)
