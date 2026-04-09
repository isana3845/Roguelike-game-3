from random import choice, shuffle, randint
import time
import copy
from important_classes import Player, Inventory, Interface, Item, Enemy
from world import Map
from vector_database import Vector2
import keyboard
import os


map_height = randint(2, 5)
map_width = randint(2, 4)

items_to_choose = [Item("Golden sword", "weapon", 10), Item("Apple", "healing", 5), Item("Potion", "invisibility_potion", 20), Item("Iron chest", "armor", 5)]
items = []

for i in range(map_height*map_width - 2):
    items.append(choice(items_to_choose))

game_map = Map(map_height=map_height, map_width=map_height)

start_x = randint(0, game_map.map_width - 1)
start_y = randint(0, game_map.map_height - 1)
exit_x = randint(0, game_map.map_width - 1)
exit_y = randint(0, game_map.map_height - 1)

while exit_x == start_x and exit_y == start_y:
    exit_x = randint(0, game_map.map_width - 1)
    exit_y = randint(0, game_map.map_height - 1)

rooms = game_map.generate_global_map(exit_x, exit_y)
inventory = Inventory()
player = Player(Vector2(0, 0), 16, 20, 2, 10, inventory)

entities = [Enemy(Vector2(0, 0), 20, 20, 2, 20) for i in range(map_height*map_width - 1)]

ent = entities
# Важно: создаем новый список предметов с правильными позициями
placed_items = []  # Список для размещенных предметов
item_list = copy.deepcopy(items)


# Размещаем врагов и предметы
for y in range(game_map.map_height):
    for x in range(game_map.map_width):
        if [x, y] == [start_x, start_y]:
            continue
        
        # Размещаем врага
        if ent:
            game_map.set_entity(ent[0], x, y)
            ent = ent[1:]
        
        # Размещаем предмет, если есть
        if item_list:
            item = item_list.pop(0)  # Берем первый предмет
            # Используем случайные смещения
            x_offset = randint(-game_map.room_width//4, game_map.room_width//4)
            y_offset = randint(-game_map.room_height//4, game_map.room_height//4)
            game_map.set_entity(item, x, y, 1, 1)
            placed_items.append(item)  # Добавляем в список размещенных предметов

# Теперь items должен содержать размещенные предметы
items = placed_items


inventory.add_item(Item("Sword", "weapon", 5), Item("Apple", "healing", 5), Item("Shlyapka", "armor", 5), Item("Potion", "invisibility_potion", 10))
interface = Interface(player)
game_map.set_entity(player, start_x, start_y)

nearest = None

player_has_moved = False  # Флаг, что игрок сделал ход

print(items)

while True and player.health > 0:
    os.system("cls")
    game_map.draw_map(player, entities, items, rooms, interface)
    event = keyboard.read_event()

    if game_map.is_exit(player.position, rooms):
        os.system("cls")
        interface.add_event("Вы перешли на следующий уровень!")
        interface.level += 1
        map_height = randint(2, 5)
        map_width = randint(2, 4)
        game_map = Map(map_height=map_height, map_width=map_width)

        entities = [Enemy(Vector2(0, 0), 20, 20, 2, 20) for i in range(map_height*map_width - 4)]
        ent = entities.copy()

        start_x = randint(0, game_map.map_width - 1)
        start_y = randint(0, game_map.map_height - 1)
        exit_x = randint(0, game_map.map_width - 1)
        exit_y = randint(0, game_map.map_height - 1)

        # Создаем новые предметы для нового уровня
        new_items_data = [choice(items_to_choose) for i in range(map_height*map_width)]
        new_items = []

        # Размещаем врагов и предметы
        for y in range(game_map.map_height):
            for x in range(game_map.map_width):
                if [x, y] == [start_x, start_y]:
                    continue
                
                if ent:
                    game_map.set_entity(ent[0], x, y, randint(-2, 2), randint(-2, 2))
                    ent = ent[1:]

                if new_items_data and [x, y] != [exit_x, exit_y]:
                    item = new_items_data.pop(0)
                    x_offset = randint(-game_map.room_width//4, game_map.room_width//4)
                    y_offset = randint(-game_map.room_height//4, game_map.room_height//4)
                    game_map.set_entity(item, x, y, x_offset, y_offset)
                    new_items.append(item)

        items = new_items  # Обновляем список предметов

        while exit_x == start_x and exit_y == start_y:
            exit_x = randint(0, game_map.map_width - 1)
            exit_y = randint(0, game_map.map_height - 1)

        rooms = game_map.generate_global_map(exit_x, exit_y)
        game_map.visited_rooms.clear()
        game_map.set_entity(player, start_x, start_y)
        player_has_moved = False
        continue
    
    
    
    if event.event_type == keyboard.KEY_DOWN:
        match event.name:
            case 'w' | 'ц':
                if game_map.is_walkable(player.position + Vector2(0, -1), rooms):
                    player.move(Vector2(0, -1))
                    player_has_moved = True  # Игрок сделал ход
            case 's'| 'ы':
                if game_map.is_walkable(player.position + Vector2(0, 1), rooms):
                    player.move(Vector2(0, 1))
                    player_has_moved = True
            case 'a'| 'ф':
                if game_map.is_walkable(player.position + Vector2(-1, 0), rooms):
                    player.move(Vector2(-1, 0))
                    player_has_moved = True
            case 'd'| 'в':
                if game_map.is_walkable(player.position + Vector2(1, 0), rooms):
                    player.move(Vector2(1, 0))
                    player_has_moved = True
            case 'e'| 'у':
                try:
                    nearest = None
                    min_distance = float('inf')
                    
                    # Ищем ближайшего врага
                    for enemy in entities:
                        distance = abs(enemy.position.x - player.position.x) + abs(enemy.position.y - player.position.y)
                        if distance <= 2:  # Если враг в радиусе 2 клеток
                            if distance < min_distance:
                                min_distance = distance
                                nearest = enemy
                    
                    if nearest:
                        print(f"Attacking enemy at distance {min_distance}")
                        interface.add_event(player.attack(nearest))
                        nearest.attack(player)

                        if nearest.health <= 0:
                            interface.add_event("Enemy died!")
                            entities.remove(nearest)
                    else:
                        interface.add_event("No enemies nearby!")
                except Exception as e:
                    print(f"Can't attack enemy! {e}")
                    time.sleep(1)
            case 'esc':
                break
            
            case 'i'| 'ш' | 'tab':
                while True:
                    os.system("cls")
                    inventory()
                    inv_event = keyboard.read_event()
                    if inv_event.event_type == keyboard.KEY_DOWN:
                        if inv_event.name == "esc":
                            event = None
                            break  # Выходим из цикла инвентаря
                        player.player_inventory(inv_event.name)
                player_has_moved = False
            
            case _:
                continue
                        
    if player_has_moved:
        # Проверяем, есть ли предмет на позиции игрока
        for item in items[:]:  # Используем срез для безопасного удаления
            if item.position == player.position:
                inventory.add_item(item)
                interface.add_event(f"Вы подобрали {item.title}!")
                items.remove(item)
                break

    # Двигаем врагов ТОЛЬКО если игрок сделал ход
    if player_has_moved and not player.invisibility:
        occupied = []
        for enemy in entities:
            if enemy.position == player.position:
                enemy.attack(player)

            if abs(enemy.position - player.position) <= min(game_map.room_height, game_map.room_width)/2:
                enemy.move(player, occupied, game_map, rooms)

        player_has_moved = False  # Сбрасываем флаг после движения врагов
            
    