from random import choice, randint, shuffle
from vector_database import Vector2
from important_classes import Player, Interface, Enemy, Item


class Map:
    def __init__(self, room_height=9, room_width=20, map_height=3, map_width=3):
        self.room_height = room_height
        self.room_width = room_width
        self.map_height = map_height
        self.map_width = map_width
        self.map = {}
        self.visited_rooms = {}
        self.rooms = []
        self.tiles = ['\033[90mΩ\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[94m◦\033[0m']
        self.not_walkable_tiles = ['┌', '─', '┐', '│', '└', '┘', '\033[91mE\033[0m', '\033[94m☺\033[0m', '\033[93m☺\033[0m']
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


    def generate_global_map_from_connections(self, connections, exit_x=None, exit_y=None):
        area = self.map_height * self.map_width
        self.map = {i: set() for i in range(1, area + 1)}

        for room_from, room_to in connections:
            self.map[room_from].add(room_to)
            self.map[room_to].add(room_from)

        return self.build_rooms(exit_x, exit_y)


    def generate_global_map(self, exit_x=None, exit_y=None):
        self.generate_map()
        return self.build_rooms(exit_x, exit_y)


    def build_rooms(self, exit_x=None, exit_y=None):
        self.rooms = []
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
            self.rooms.append(row)

        return self.rooms
    

    def is_walkable(self, position: Vector2, rooms) -> bool:
        room_x = position.x // self.room_width
        room_y = position.y // self.room_height
        local_x = position.x % self.room_width
        local_y = position.y % self.room_height

        if room_x < 0 or room_x >= self.map_width or room_y < 0 or room_y >= self.map_height:
            return False

        if local_x < 0 or local_x >= self.room_width or local_y < 0 or local_y >= self.room_height:
            return False

        tile = rooms[room_y][room_x][local_y][local_x]
        # Двери ('■' и '█') считаем проходимыми
        if tile in self.not_walkable_tiles and tile not in ['■', '█']:
            return False

        return True
    

    def is_exit(self, position: Vector2, rooms) -> bool:
        room_x = position.x // self.room_width
        room_y = position.y // self.room_height
        local_x = position.x % self.room_width
        local_y = position.y % self.room_height

        
        return rooms[room_y][room_x][local_y][local_x] == self.exit_tile
    

    def set_entity(self, entity: Player, room_x: int, room_y: int, x_offset = 0, y_offset = 0):
        entity.position.x = room_x * self.room_width + self.room_width // 2 + x_offset % self.room_width
        entity.position.y = room_y * self.room_height + self.room_height // 2 - y_offset % self.room_height

    
    def draw_map(self, player: Player, entities: list, items: list[Item], rooms, interface: Interface):
        room_x = player.position.x // self.room_width
        room_y = player.position.y // self.room_height
        local_x = player.position.x % self.room_width
        local_y = player.position.y % self.room_height
    
        if (room_x, room_y) not in self.visited_rooms:
            room_copy = [row[:] for row in rooms[room_y][room_x]]
            self.visited_rooms[(room_x, room_y)] = room_copy
    
        # Создаем словарь для позиций врагов
        enemy_map = {}
        for entity in entities:
            if isinstance(entity, Enemy):
                enemy_room_x = entity.position.x // self.room_width
                enemy_room_y = entity.position.y // self.room_height
                enemy_local_x = entity.position.x % self.room_width
                enemy_local_y = entity.position.y % self.room_height
                enemy_map[(enemy_room_x, enemy_room_y, enemy_local_x, enemy_local_y)] = entity
        
        # Создаем словарь для позиций предметов
        item_map = {}
        for item in items:
            if isinstance(item, Item):
                item_room_x = item.position.x // self.room_width
                item_room_y = item.position.y // self.room_height
                item_local_x = item.position.x % self.room_width
                item_local_y = item.position.y % self.room_height
                item_map[(item_room_x, item_room_y, item_local_x, item_local_y)] = item
    
        side_lines = interface.get_lines()
        map_lines = []
    
        for room_row in range(self.map_height):
            for y in range(self.room_height):
                line = []
    
                for room_column in range(self.map_width):
                    if (room_column, room_row) in self.visited_rooms:
                        room = rooms[room_row][room_column]
                        row = list(room[y])
    
                        # Отрисовываем каждый символ в строке
                        for x in range(self.room_width):
                            is_player = (room_row == room_y and room_column == room_x and 
                                       y == local_y and x == local_x)
                            is_enemy = (room_column, room_row, x, y) in enemy_map
                            is_item = (room_column, room_row, x, y) in item_map
                            
                            if is_player:
                                # Отображаем игрока
                                row[x] = '\033[93m☺\033[0m' if not player.invisibility else '\033[94m☺\033[0m'
                            elif is_enemy:
                                # Отображаем врага
                                row[x] = '\033[91mE\033[0m'
                            elif is_item:
                                # Отображаем предмет
                                row[x] = '\033[91mП\033[0m'
    
                        line.append(''.join(row))
                    else:
                        line.append('\033[30m' + '█' * self.room_width + '\033[0m')
    
                    if room_column < 2:
                        line.append('')
    
                map_lines.append(''.join(line))
    
        max_lines = max(len(map_lines), len(side_lines))
    
        for i in range(max_lines):
            map_part = map_lines[i] if i < len(map_lines) else ' ' * self.room_width * self.map_width
            side_part = side_lines[i] if i < len(side_lines) else ''
    
            print(f"{map_part}{' ' * self.room_width}{side_part}")