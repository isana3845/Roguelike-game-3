from random import choice, randint
import time
from important_classes import Player, Inventory, Interface, Item, Enemy, MainMenu, PauseMenu
from world import Map
from vector_database import Vector2, SaveManager
import keyboard
import os


save_manager = SaveManager()

def restore_game_state(load_data):    
    p_data = load_data['player']
    g_data = load_data['game']
    i_data = load_data['inventory']
    enemies_data = load_data.get('enemies', [])
    world_items_data = load_data.get('world_items', [])

    game_map = Map(map_height=g_data[0], map_width=g_data[1])
    player = Player(Vector2(p_data[4], p_data[5]), p_data[0], p_data[1], p_data[2], p_data[3], Inventory())
    player.invisibility = p_data[7]
    interface = Interface(player, p_data[6])

    for name, ty, power, qty in i_data:
        item = Item(name, ty, power)

        for _ in range(qty):
            player.inv.add_item(item)

    connections = load_data.get('map_connections', [])
    if connections:
        rooms = game_map.generate_global_map_from_connections(connections, g_data[4], g_data[5])
    else:
        rooms = game_map.generate_global_map(g_data[4], g_data[5])

    for (room_x, room_y) in load_data.get('visited_rooms', []):
        game_map.visited_rooms[(room_x, room_y)] = [row[:] for row in rooms[room_y][room_x]]

    entities = []
    for e_data in enemies_data:
        enemy = Enemy(Vector2(e_data[1], e_data[2]),e_data[3], e_data[4], e_data[5], e_data[6], e_data[7])
        entities.append(enemy)

    items = []
    for w_data in world_items_data:
        item = Item(w_data[3], w_data[4], w_data[5], w_data[6],Vector2(w_data[1], w_data[2]))
        items.append(item)

    return player, game_map, rooms, items, entities, interface, g_data[0], g_data[1], g_data[2], g_data[3], g_data[4], g_data[5]


def handle_pause(player, game_map, items, entities, interface, map_h, map_w, s_x, s_y, e_x, e_y, rooms):
    menu = PauseMenu()
    while True:
        action = menu.run()
        if action is None or action == 1:
            return "continue"
        elif action == 2:
            os.system("cls")
            name = input("Введите имя сохранения: ").strip() or f"save_{int(time.time())}"
            save_manager.save_game(name, player, game_map, items, entities, interface, map_h, map_w, s_x, s_y, e_x, e_y)
            time.sleep(1)
        elif action == 3:
            saves = save_manager.load_saves()
            if not saves:
                print("\nСохранений не найдено!")
                time.sleep(1)
                continue
            os.system("cls")

            for i, (sid, sname, sdate) in enumerate(saves):
                print(f"{i+1}. {sname} | {sdate}")
            sel = input("\nВведите номер или ESC: ").strip()
            if sel.upper() == 'ESC':
                continue
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(saves):
                    data = save_manager.load_game(saves[idx][0])

                    if data:
                        return data
                    
            except ValueError:
                continue
        elif action == 4:
            return "quit"


def start_game(load_data=None):
    if load_data:
        player, game_map, rooms, items, entities, interface, map_height, map_width, start_x, start_y, exit_x, exit_y = restore_game_state(load_data)
        print("📂 Игра загружена!")
        time.sleep(1)
    else:
        map_height = randint(2, 5)
        map_width = randint(2, 4)
        game_map = Map(map_height=map_height, map_width=map_width)
        start_x, start_y = randint(0, map_width-1), randint(0, map_height-1)
        exit_x, exit_y = randint(0, map_width-1), randint(0, map_height-1)

        while exit_x == start_x and exit_y == start_y:
            exit_x, exit_y = randint(0, map_width-1), randint(0, map_height-1)

        rooms = game_map.generate_global_map(exit_x, exit_y)
        inv = Inventory()
        inv.add_item(Item("Sword", "weapon", 5), Item("shlyapka", "armor", 5), Item("apple", "healing", 5), Item("apple", "healing", 5), Item("apple", "healing", 5))
        player = Player(Vector2(0, 0), 16, 20, 2, 10, inv)
        interface = Interface(player)
        game_map.set_entity(player, start_x, start_y)

        entities = [Enemy(Vector2(0, 0), 20, 20, 2, 20) for _ in range(map_height * map_width - 1)]
        items_to_choose = [Item("Golden sword", "weapon", 10), Item("Apple", "healing", 5), 
                           Item("Potion", "invisibility_potion", 20), Item("Iron chest", "armor", 5)]
        items = [choice(items_to_choose) for _ in range(map_height * map_width - 2)]
        
        placed_items, ent_list = [], entities.copy()
        for y in range(map_height):
            for x in range(map_width):
                if [x, y] == [start_x, start_y]:
                    continue
                if ent_list:
                    game_map.set_entity(ent_list.pop(0), x, y)
                if items:
                    item = items.pop(0)
                    game_map.set_entity(item, x, y, randint(-2,2), randint(-2,2))
                    placed_items.append(item)
        items = placed_items

    player_has_moved = False
    while True and player.health > 0:
        os.system("cls")
        game_map.draw_map(player, entities, items, rooms, interface)
        event = keyboard.read_event()

        if game_map.is_exit(player.position, rooms):
            os.system("cls")
            interface.add_event("Вы перешли на следующий уровень!")
            interface.level += 1
            map_height, map_width = randint(2, 5), randint(2, 4)
            game_map = Map(map_height=map_height, map_width=map_width)

            entities = [Enemy(Vector2(0, 0), 20, 20, 2, 20) for i in range(map_height*map_width - 4)]
            ent = entities.copy()
            new_items_data = [choice(items_to_choose) for i in range(map_height*map_width)]
            new_items = []

            start_x, start_y = randint(0, map_width-1), randint(0, map_height-1)
            exit_x, exit_y = randint(0, map_width-1), randint(0, map_height-1)

            while exit_x == start_x and exit_y == start_y:
                exit_x, exit_y = randint(0, map_width-1), randint(0, map_height-1)

            for y in range(game_map.map_height):
                for x in range(game_map.map_width):
                    if [x, y] == [start_x, start_y]:
                        continue
                    
                    if ent:
                        game_map.set_entity(ent[0], x, y, randint(-2, 2), randint(-2, 2))
                        ent[0].weapon.ch += interface.level // 5
                        ent = ent[1:]

                    if new_items_data and [x, y] != [exit_x, exit_y]:
                        item = new_items_data.pop(0)
                        x_offset = randint(-game_map.room_width//4, game_map.room_width//4)
                        y_offset = randint(-game_map.room_height//4, game_map.room_height//4)
                        game_map.set_entity(item, x, y, x_offset, y_offset)
                        new_items.append(item)

            items = new_items  # Обновляем список предметов

            rooms = game_map.generate_global_map(exit_x, exit_y)
            game_map.visited_rooms.clear()
            game_map.set_entity(player, start_x, start_y)
            player_has_moved = False
            continue

        if event.event_type == keyboard.KEY_DOWN:
            match event.name.lower():
                case 'w' | 'ц':
                    if game_map.is_walkable(player.position + Vector2(0, -1), rooms):
                        player.move(Vector2(0, -1)); player_has_moved = True
                case 's' | 'ы':
                    if game_map.is_walkable(player.position + Vector2(0, 1), rooms):
                        player.move(Vector2(0, 1)); player_has_moved = True
                case 'a' | 'ф':
                    if game_map.is_walkable(player.position + Vector2(-1, 0), rooms):
                        player.move(Vector2(-1, 0)); player_has_moved = True
                case 'd' | 'в':
                    if game_map.is_walkable(player.position + Vector2(1, 0), rooms):
                        player.move(Vector2(1, 0)); player_has_moved = True
                case 'e' | 'у':
                    nearest, min_dist = None, float('inf')
                    for enemy in entities:
                        dist = abs(enemy.position.x - player.position.x) + abs(enemy.position.y - player.position.y)
                        if dist <= 2 and dist < min_dist:
                            min_dist, nearest = dist, enemy
                    if nearest:
                        interface.add_event(player.attack(nearest))
                        nearest.attack(player)
                        if nearest.health <= 0:
                            interface.add_event("Враг повержен!")
                            entities.remove(nearest)
                    else:
                        interface.add_event("Нет врагов рядом!")
                case 'esc':
                    result = handle_pause(player, game_map, items, entities, interface, map_height, map_width, start_x, start_y, exit_x, exit_y, rooms)
                    if result == "quit":
                        return
                    if isinstance(result, dict):
                        (player, game_map, rooms, items, entities, interface,
                         map_height, map_width, start_x, start_y, exit_x, exit_y) = restore_game_state(result)
                        print("📂 Игра загружена!")
                        time.sleep(1)
                    player_has_moved = False
                case 'i' | 'ш' | 'tab':
                    while True:
                        os.system("cls")
                        player.inv()
                        inv_event = keyboard.read_event()
                        if inv_event.event_type == keyboard.KEY_DOWN:
                            if inv_event.name == "esc":
                                break
                            player.player_inventory(inv_event.name)
                    player_has_moved = False

        if player_has_moved:
            for item in items[:]:
                if item.position == player.position:
                    player.inv.add_item(item)
                    interface.add_event(f"Подобрано: {item.title}!")
                    items.remove(item)
                    break

            if not player.invisibility:
                occupied = []
                for enemy in entities[:]:
                    if enemy.position == player.position:
                        enemy.attack(player)
                    elif abs(enemy.position - player.position) <= min(game_map.room_height, game_map.room_width)/2:
                        enemy.move(player, occupied, game_map, rooms)
            player_has_moved = False


def main():
    while True:
        os.system("cls")
        menu = MainMenu()
        result = menu.run()
        if result == "new":
            start_game()
        elif result == "load":
            saves = save_manager.load_saves()
            if not saves:
                os.system("cls")
                print("Сохранений не найдено!")
                time.sleep(1)
                continue
            os.system("cls")

            for i, (sid, sname, sdate) in enumerate(saves):
                print(f"{i+1}. {sname} | {sdate}")
            sel = input("\nВведите номер сохранения: ").strip()
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(saves):
                    data = save_manager.load_game(saves[idx][0])
                    if data:
                        start_game(data)
                    else:
                        print("Ошибка загрузки!")
                        time.sleep(1)

            except ValueError:
                pass
        elif result is False:
            os.system("cls")
            print("Спасибо за игру!")
            break

main()