from random import choice, shuffle, randint
import time
from important_classes import Player, Inventory, Interface, Item, Enemy
from world import Map
from vector_database import Vector2
import keyboard
import os


game_map = Map(map_height=randint(2, 5), map_width=randint(2, 4))

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

entities = [Enemy(Vector2(0, 0), 20, 20, 20, 20), Enemy(Vector2(0, 0), 20, 20, 20, 20), Enemy(Vector2(0, 0), 20, 20, 20, 20)]

ent = entities

for y in range(game_map.map_height):
    if not ent:
        break
    for x in range(game_map.map_width):
        if [x, y] == [start_x, start_y]:
            continue
        if not ent:
            break
        game_map.set_player(ent[0], x, y)
        ent = ent[1:]


inventory.add_item(Item("Sword", "weapon", 5), Item("Apple", "healing", 5), Item("Shlyapka", "armor", 5), Item("Potion", "invisibility_potion", 20))
interface = Interface(player)
game_map.set_player(player, start_x, start_y)
nearest = None


player_has_moved = False  # Флаг, что игрок сделал ход

while True and player.health > 0:
    os.system("cls")
    game_map.draw_map(player, entities, rooms, interface)
    event = keyboard.read_event()

    if game_map.is_exit(player.position, rooms):
        os.system("cls")
        interface.add_event("Вы перешли на следующий уровень!")
        interface.level += 1
        game_map = Map(map_height=randint(2, 5), map_width=randint(2, 4))

        start_x = randint(0, game_map.map_width - 1)
        start_y = randint(0, game_map.map_height - 1)
        exit_x = randint(0, game_map.map_width - 1)
        exit_y = randint(0, game_map.map_height - 1)
        ent = entities

        for y in range(game_map.map_height):
            if not ent:
                break
            for x in range(game_map.map_width):
                if [x, y] == [start_x, start_y]:
                    continue
                if not ent:
                    break
                game_map.set_player(ent[0], x, y)
                ent = ent[1:]
        while exit_x == start_x and exit_y == start_y:
            exit_x = randint(0, game_map.map_width - 1)
            exit_y = randint(0, game_map.map_height - 1)

        rooms = game_map.generate_global_map(exit_x, exit_y)
        game_map.visited_rooms.clear()
        game_map.set_player(player, start_x, start_y)
        player_has_moved = False  # Сбрасываем флаг
        continue
    
    
    
    if event.event_type == keyboard.KEY_DOWN:
        match event.name:
            case 'w':
                if game_map.is_walkable(player.position + Vector2(0, -1), rooms):
                    player.move(Vector2(0, -1))
                    player_has_moved = True  # Игрок сделал ход
            case 's':
                if game_map.is_walkable(player.position + Vector2(0, 1), rooms):
                    player.move(Vector2(0, 1))
                    player_has_moved = True
            case 'a':
                if game_map.is_walkable(player.position + Vector2(-1, 0), rooms):
                    player.move(Vector2(-1, 0))
                    player_has_moved = True
            case 'd':
                if game_map.is_walkable(player.position + Vector2(1, 0), rooms):
                    player.move(Vector2(1, 0))
                    player_has_moved = True
            case 'e':
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
                        player.attack(nearest)
                        nearest.attack(player)
                        if nearest.health <= 0:
                            print(f"Enemy died!")
                            entities.remove(nearest)
                    else:
                        print("No enemies nearby!")
                        time.sleep(1)
                except Exception as e:
                    raise ValueError("1111")
                    print(f"Can't attack enemy! {e}")
                    time.sleep(1)
            case 'esc':
                print(111)
                break
            
            case 'i':
                while True:
                    os.system("cls")
                    inventory()
                    inv_event = keyboard.read_event()
                    if inv_event.event_type == keyboard.KEY_DOWN:
                        if inv_event.name == "esc":
                            break  # Выходим из цикла инвентаря
                        player.player_inventory(inv_event.name)
                player_has_moved = False
            
            case _:
                continue

            
    
    # Двигаем врагов ТОЛЬКО если игрок сделал ход
    if player_has_moved and not player.invisibility:
        for enemy in entities:
            enemy.move(player, game_map, rooms)
        player_has_moved = False  # Сбрасываем флаг после движения врагов
            
    

