from random import choice, shuffle
from file1 import Player, Inventory, Interface, Item
from file import Vector2
import keyboard
import os

l = []
with open("settings.txt", "r") as f:
    for i in f.readlines():
        l += list(map(int, i.split()))


class Map:
    def __init__(self, room_height=9, room_width=20, map_height=3, map_width=3):
        self.room_height = room_height
        self.room_width = room_width
        self.map_height = map_height
        self.map_width = map_width
        self.map = {}
        self.tiles = ['\033[90mΩ\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[94m◦\033[0m']
        self.not_walkable_tiles = ['┌', '─', '┐', '│', '└', '┘']
        

    def generate_room(self):
        room = []
        
        for y in range(self.room_height):
            row = []
            for x in range(self.room_width):
                if y == 0:
                    if x == 0:
                        row.append('┌')
                    elif x == self.room_width - 1:
                        row.append('┐')
                    else:
                        row.append('─')
                elif y == self.room_height - 1:
                    if x == 0:
                        row.append('└')
                    elif x == self.room_width - 1:
                        row.append('┘')
                    else:
                        row.append('─')
                elif x == 0 or x == self.room_width - 1:
                    row.append('│')
                else:
                    row.append(choice(self.tiles))
            room.append(row)

        return room
    
    def generate_map(self):
        k = self.map_width
        area = self.map_height*self.map_width

        for i in range(1, area + 1):
            self.map[i] = set()

        for i in range(1, area + 1):
            if i + k <= area:
                self.map[i].add(i + k)
                self.map[i + k].add(i)

            if i + 1 <= area and i % k:
                self.map[i].add(i + 1)
                self.map[i + 1].add(i)

        edges = []
        for i in self.map:
            for j in self.map[i]:
                if i < j:
                    edges.append((i, j))

        shuffle(edges)

        # Удаляем только те рёбра, которые не создают острова
        # (оставляем хотя бы 2 связи у каждой вершины, кроме угловых)
        for i, j in edges:
            if len(self.map[i]) > 2 and len(self.map[j]) > 2:
                self.map[i].remove(j)
                self.map[j].remove(i)

    def generate_global_map(self):
        rooms = []
        self.generate_map()
        shtuka = self.map

        for y in range(self.map_height):
            row = []
            for x in range(self.map_width):
                room = self.generate_room()
                center_x = self.room_width // 2
                center_y = self.room_height // 2
                room_order = y*self.map_width + x + 1

                for i in shtuka[room_order]:
                    if abs(room_order - i) == 1:
                        if i > room_order:
                            room[center_y][self.room_width - 1] = '■'
                        else:
                            room[center_y][0] = '■'
                    elif abs(room_order - i) == self.map_width:
                        if i > room_order:
                            room[self.room_height - 1][center_x] = '█'
                        else:
                            room[0][center_x] = '█'
                row.append(room)
            rooms.append(row)

        return rooms
    

    def is_walkable(self, position: Vector2, rooms) -> bool:
        room_x = position.x // self.room_width
        room_y = position.y // self.room_height
        local_x = position.x % self.room_width
        local_y = position.y % self.room_height

        if room_x < 0 or room_x >= self.map_width or room_y < 0 or room_y >= self.map_height:
            return False
        
        return rooms[room_y][room_x][local_y][local_x] not in self.not_walkable_tiles
    

    def set_player(self, player: Player, room_x: int, room_y: int):
        player.position.x = room_x * self.room_width + self.room_width // 2
        player.position.y = room_y * self.room_height + self.room_height // 2

    
    def draw_map(self, player: Player, rooms):
        room_x = player.position.x // self.room_width  # Координаты комнаты на карте
        room_y = player.position.y // self.room_height
        local_x = player.position.x % self.room_width  # Координаты игрока в комнате
        local_y = player.position.y % self.room_height

        for room_row in range(self.map_height):
            for y in range(self.room_height):
                line = []

                for room_column in range(self.map_width):
                    room = rooms[room_row][room_column]

                    if (room_row == room_y and room_column == room_x and y == local_y):
                        row = list(room[y])
                        row[local_x] = '\033[93m☺\033[0m'
                        line.append(''.join(row))
                    else:
                        line.append(''.join(room[y]))

                    if room_column < 2:
                        line.append('')
                print(''.join(line))

            

inventory = Inventory()
inventory.add_item(Item("sword", "Weapon", 5), Item("apple", "Healing", 10))

game_map = Map(map_height=l[1], map_width=l[0], room_width = l[2], room_height=l[3])
rooms = game_map.generate_global_map()

player = Player(Vector2(0, 0), 10, 2)
interface = Interface(player)
game_map.set_player(player, 0, 0)

while True:
    os.system("cls")
    game_map.draw_map(player, rooms)
    inventory()
    interface()
    event = keyboard.read_event()
    
    if event.event_type == keyboard.KEY_DOWN:
        match event.name:
            case 'w':
                if game_map.is_walkable(player.position + Vector2(0, -1), rooms):
                    player.move(Vector2(0, -1))
            case 's':
                if game_map.is_walkable(player.position + Vector2(0, 1), rooms):
                    player.move(Vector2(0, 1))
            case 'a':
                if game_map.is_walkable(player.position + Vector2(-1, 0), rooms):
                    player.move(Vector2(-1, 0))
            case 'd':
                if game_map.is_walkable(player.position + Vector2(1, 0), rooms):
                    player.move(Vector2(1, 0))
            
            case 'i':
                while True:
                    os.system("cls")
                    inventory()
                    event = keyboard.read_event()
                    if event.event_type == keyboard.KEY_DOWN:
                        if event.name == "esc":
                            break
                        inventory.action(event.name)

            case 'esc':
                break

