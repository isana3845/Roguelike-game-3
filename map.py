from random import choice, shuffle, randint
from file1 import Player, Inventory, Interface, Item
from file import Vector2
import keyboard
import os


class Map:
    def __init__(self, room_height=9, room_width=20, map_height=3, map_width=3):
        self.room_height = room_height
        self.room_width = room_width
        self.map_height = map_height
        self.map_width = map_width
        self.map = {}
        self.visited_rooms = {}
        self.tiles = ['\033[90mΩ\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[94m◦\033[0m']
        self.not_walkable_tiles = ['┌', '─', '┐', '│', '└', '┘']
        self.exit_tile = '\033[35m🁫\033[0m'
        

    def generate_room(self, is_exit=False):
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

        if is_exit:
            exit_x = randint(1, self.room_width - 2)
            exit_y = randint(1, self.room_height - 2)
            room[exit_y][exit_x] = self.exit_tile

        return room
    

    def generate_map(self):
        area = self.map_height * self.map_width
        self.map = {i: set() for i in range(1, area + 1)}
        edges = []

        for i in range(1, area + 1):
            if i % self.map_width != 0:
                edges.append((i, i + 1))

            if i + self.map_width <= area:
                edges.append((i, i + self.map_width))

        shuffle(edges)
        parent = list(range(area + 1))

        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])

            return parent[x]
        

        for a, b in edges:
            if find(a) != find(b):
                parent[find(a)] = find(b)
                self.map[a].add(b)
                self.map[b].add(a)


    def generate_global_map(self, exit_x=None, exit_y=None):
        rooms = []
        self.generate_map()
        shtuka = self.map

        for y in range(self.map_height):
            row = []
            for x in range(self.map_width):
                has_exit = (x == exit_x and y == exit_y) if exit_x is not None else False
                room = self.generate_room(is_exit=has_exit)
                center_x = self.room_width // 2
                center_y = self.room_height // 2
                room_order = y * self.map_width + x + 1

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
    

    def is_exit(self, position: Vector2, rooms) -> bool:
        room_x = position.x // self.room_width
        room_y = position.y // self.room_height
        local_x = position.x % self.room_width
        local_y = position.y % self.room_height

        
        return rooms[room_y][room_x][local_y][local_x] == self.exit_tile
    

    def set_player(self, player: Player, room_x: int, room_y: int):
        player.position.x = room_x * self.room_width + self.room_width // 2
        player.position.y = room_y * self.room_height + self.room_height // 2

    
    def draw_map(self, player: Player, rooms, interface: Interface):
        room_x = player.position.x // self.room_width  # Координаты комнаты на карте
        room_y = player.position.y // self.room_height
        local_x = player.position.x % self.room_width  # Координаты игрока в комнате
        local_y = player.position.y % self.room_height

        if (room_x, room_y) not in self.visited_rooms:
            room_copy = [row[:] for row in rooms[room_y][room_x]]
            self.visited_rooms[(room_x, room_y)] = room_copy

        side_lines = interface.get_lines()
        map_lines = []

        for room_row in range(self.map_height):
            for y in range(self.room_height):
                line = []

                for room_column in range(self.map_width):
                    if (room_column, room_row) in self.visited_rooms:
                        room = rooms[room_row][room_column]

                        if (room_row == room_y and room_column == room_x and y == local_y):
                            row = list(room[y])
                            row[local_x] = '\033[93m☺\033[0m'
                            line.append(''.join(row))
                        else:
                            line.append(''.join(room[y]))
                    else:
                        line.append('\033[30m' + '█' * self.room_width + '\033[0m')

                    if room_column < 2:
                        line.append('')
                # print(" " * int(self.room_width*0.5), end = "")
                map_lines.append(''.join(line))

        max_lines = max(len(map_lines), len(side_lines))
    
        for i in range(max_lines):
            map_part = map_lines[i] if i < len(map_lines) else ' ' * self.room_width * self.map_width
            side_part = side_lines[i] if i < len(side_lines) else ''
            
            print(f"{map_part}{' ' * self.room_width}{side_part}")



game_map = Map(map_height=randint(2, 5), map_width=randint(2, 4))

start_x = randint(0, game_map.map_width - 1)
start_y = randint(0, game_map.map_height - 1)
exit_x = randint(0, game_map.map_width - 1)
exit_y = randint(0, game_map.map_height - 1)

while exit_x == start_x and exit_y == start_y:
    exit_x = randint(0, game_map.map_width - 1)
    exit_y = randint(0, game_map.map_height - 1)

rooms = game_map.generate_global_map(exit_x, exit_y)
player = Player(Vector2(0, 0), 20, 20, 2, 10)
interface = Interface(player)
game_map.set_player(player, start_x, start_y)
inventory = Inventory()
inventory.add_item(Item("Sword", "Weapon", 5), Item("Apple", "Healing", 10))

while True:
    os.system("cls")
    game_map.draw_map(player, rooms, interface)
    inventory()

    if game_map.is_exit(player.position, rooms):
        os.system("cls")
        interface.add_event("Вы перешли на следующий уровень!")
        interface.level += 1
        game_map = Map(map_height=randint(2, 5), map_width=randint(2, 4))

        start_x = randint(0, game_map.map_width - 1)
        start_y = randint(0, game_map.map_height - 1)
        exit_x = randint(0, game_map.map_width - 1)
        exit_y = randint(0, game_map.map_height - 1)

        while exit_x == start_x and exit_y == start_y:
            exit_x = randint(0, game_map.map_width - 1)
            exit_y = randint(0, game_map.map_height - 1)

        rooms = game_map.generate_global_map(exit_x, exit_y)
        game_map.visited_rooms.clear()
        game_map.set_player(player, start_x, start_y)

        continue
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

