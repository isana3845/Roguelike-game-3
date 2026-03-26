from random import choice
from player import Player
from file import Vector2
import keyboard
import os


class Map:
    def __init__(self, room_height=9, room_width=20):
        self.room_height = room_height
        self.room_width = room_width
        self.tiles = ['\033[90m#\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[92m.\033[0m', '\033[94m~\033[0m']
        self.not_walkable_tiles = ['\033[90m#\033[0m', '┌', '─', '┐', '│', '└', '┘']
        

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

        self.original_map = [row.copy() for row in room]

        return room
    

    def generate_global_map(self):
        rooms = []

        for y in range(3):
            row = []
            for x in range(3):
                room = self.generate_room()
                center_x = self.room_width // 2
                center_y = self.room_height // 2

                if y < 2:
                    room[self.room_height - 1][center_x] = ' '
                if y > 0:
                    room[0][center_x] = ' '
                if x < 2:
                    room[center_y][self.room_width - 1] = ' '
                if x > 0:
                    room[center_y][0] = ' '

                row.append(room)
            rooms.append(row)

        return rooms
    

    def is_walkable(self, position: Vector2, rooms) -> bool:
        room_x = position.x // self.room_width
        room_y = position.y // self.room_height
        local_x = position.x % self.room_width
        local_y = position.y % self.room_height

        if room_x < 0 or room_x >= 3 or room_y < 0 or room_y >= 3:
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

        for room_row in range(3):
            for y in range(self.room_height):
                line = []

                for room_column in range(3):
                    room = rooms[room_row][room_column]

                    if (room_row == room_y and room_column == room_x and y == local_y):
                        row = list(room[y])
                        row[local_x] = '\033[93m@\033[0m'
                        line.append(''.join(row))
                    else:
                        line.append(''.join(room[y]))

                    if room_column < 2:
                        line.append('  ')

                print(''.join(line))

            if room_row < 2:
                separator = []
                for room_col in range(3):
                    separator.append(' ' * self.room_width)
                    if room_col < 2:
                        separator.append('   ')
                print(''.join(separator))


game_map = Map()
rooms = game_map.generate_global_map()

player = Player(Vector2(0, 0), 10, 2)
game_map.set_player(player, 0, 0)

while True:
    os.system("cls")
    game_map.draw_map(player, rooms)
    event = keyboard.read_event()
    
    if event.event_type == keyboard.KEY_DOWN:
        match event.name:
            case 'w':
                new_x = player.position.x
                new_y = player.position.y - 1
                if game_map.is_walkable(player.position + Vector2(0, -1), rooms):
                    player.move(Vector2(0, -1))
            case 's':
                new_x = player.position.x
                new_y = player.position.y + 1
                if game_map.is_walkable(player.position + Vector2(0, 1), rooms):
                    player.move(Vector2(0, 1))
            case 'a':
                new_x = player.position.x - 1
                new_y = player.position.y
                if game_map.is_walkable(player.position + Vector2(-1, 0), rooms):
                    player.move(Vector2(-1, 0))
            case 'd':
                new_x = player.position.x + 1
                new_y = player.position.y
                if game_map.is_walkable(player.position + Vector2(1, 0), rooms):
                    player.move(Vector2(1, 0))
            case 'esc':
                break