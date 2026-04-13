import sqlite3


class Vector2:
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def normalize(self):
        absolute = abs(self)
        self.x /= absolute
        self.y /= absolute
        return Vector2(self.x / absolute, self.y / absolute)

    def __contains__(self, item):
        return item in [self.x, self.y]

    def __repr__(self):
        return f"X: {self.x} Y: {self.y}"

    def __eq__(self, value):
        return self.x == value.x and self.y == value.y

    def __bool__(self):
        return Vector2(0, 0) != self
        
    def __add__(self, vec):
        return Vector2(self.x + vec.x, self.y + vec.y)
    
    def __sub__(self, vec):
        return Vector2(self.x - vec.x, self.y - vec.y)

    def __abs__(self):
        return (self.x**2 + self.y**2)**0.5
    

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:    
            self.conn.commit()
        self.conn.close()

    def init_tables(self):
        with self as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    save_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_state (
                    save_id INTEGER,
                    health INTEGER,
                    max_health INTEGER,
                    armor INTEGER,
                    max_armor INTEGER,
                    position_x INTEGER,
                    position_y INTEGER,
                    level INTEGER,
                    invisibility INTEGER,
                    FOREIGN KEY (save_id) REFERENCES saves (id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_items (
                    save_id INTEGER,
                    item_name TEXT,
                    item_type TEXT,
                    item_power INTEGER,
                    quantity INTEGER,
                    FOREIGN KEY (save_id) REFERENCES saves (id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_state (
                    save_id INTEGER,
                    map_height INTEGER,
                    map_width INTEGER,
                    start_x INTEGER,
                    start_y INTEGER,
                    exit_x INTEGER,
                    exit_y INTEGER,
                    FOREIGN KEY (save_id) REFERENCES saves (id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enemies (
                    save_id INTEGER,
                    enemy_index INTEGER,
                    position_x INTEGER,
                    position_y INTEGER,
                    health INTEGER,
                    max_health INTEGER,
                    armor INTEGER,
                    max_armor INTEGER,
                    enemy_type TEXT,
                    FOREIGN KEY (save_id) REFERENCES saves (id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS world_items (
                    save_id INTEGER,
                    item_index INTEGER,
                    position_x INTEGER,
                    position_y INTEGER,
                    item_name TEXT,
                    item_type TEXT,
                    item_power INTEGER,
                    icon TEXT,
                    FOREIGN KEY (save_id) REFERENCES saves (id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS map_connections (
                    save_id INTEGER,
                    room_from INTEGER,
                    room_to INTEGER,
                    FOREIGN KEY (save_id) REFERENCES saves (id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visited_rooms (
                    save_id INTEGER,
                    room_x INTEGER,
                    room_y INTEGER,
                    FOREIGN KEY (save_id) REFERENCES saves (id)
                )
            """)


class SaveManager:
    def __init__(self, db_name="game_saves.db"):
        self.db = Database(db_name)
        self.db.init_tables()


    def save_game(self, save_name, player, game_map, items, entities, interface, 
                  map_height, map_width, start_x, start_y, exit_x, exit_y):
        with self.db as cursor:
            try:
                cursor.execute("INSERT INTO saves (save_name) VALUES (?)", (save_name,))
                save_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO player_state 
                    (save_id, health, max_health, armor, max_armor, position_x, position_y, level, invisibility)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (save_id, player.health, player.max_health, player.armor, player.max_armor,
                      player.position.x, player.position.y, interface.level, player.invisibility))

                for item_name, item_data in player.inv.inv.items():
                    item = item_data[0]
                    quantity = item_data[1]
                    cursor.execute("""
                        INSERT INTO inventory_items (save_id, item_name, item_type, item_power, quantity)
                        VALUES (?, ?, ?, ?, ?)
                    """, (save_id, item.title, item.ty, item.ch, quantity))
                
                cursor.execute("""
                    INSERT INTO game_state (save_id, map_height, map_width, start_x, start_y, exit_x, exit_y)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (save_id, map_height, map_width, start_x, start_y, exit_x, exit_y))
                
                for idx, enemy in enumerate(entities):
                    cursor.execute("""
                        INSERT INTO enemies (save_id, enemy_index, position_x, position_y, 
                                            health, max_health, armor, max_armor, enemy_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (save_id, idx, enemy.position.x, enemy.position.y,
                            enemy.health, enemy.max_health, enemy.armor, enemy.max_armor,
                            getattr(enemy, 'enemy_type', 'normal')))
                
                for idx, item in enumerate(items):
                    cursor.execute("""
                        INSERT INTO world_items (save_id, item_index, position_x, position_y,
                                                item_name, item_type, item_power, icon)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (save_id, idx, item.position.x, item.position.y,
                            item.title, item.ty, item.ch, getattr(item, 'icon', '^')))

                for room_from, neighbors in game_map.map.items():
                    for room_to in neighbors:
                        if room_from < room_to:  # Каждое ребро один раз
                            cursor.execute("""
                                INSERT INTO map_connections (save_id, room_from, room_to)
                                VALUES (?, ?, ?)
                            """, (save_id, room_from, room_to))

                for (room_x, room_y) in game_map.visited_rooms:
                    cursor.execute("""
                        INSERT INTO visited_rooms (save_id, room_x, room_y)
                        VALUES (?, ?, ?)
                    """, (save_id, room_x, room_y))
                
                print(f"\n✅ Игра сохранена как '{save_name}'!")
                return True
            
            except Exception as e:
                print(f"\n❌ Ошибка при сохранении: {e}")
                return False


    def load_saves(self):
        with self.db as cursor:
            cursor.execute("SELECT id, save_name, created_at FROM saves ORDER BY created_at DESC")
            return cursor.fetchall()


    def load_game(self, save_id):
        with self.db as cursor:
            try:
                cursor.execute("""
                    SELECT health, max_health, armor, max_armor, position_x, position_y, level, invisibility
                    FROM player_state WHERE save_id = ?
                """, (save_id,))
                player_data = cursor.fetchone()
                if not player_data:
                    return None
                
                cursor.execute("""
                    SELECT map_height, map_width, start_x, start_y, exit_x, exit_y 
                    FROM game_state WHERE save_id = ?
                """, (save_id,))
                game_data = cursor.fetchone()

                cursor.execute("""
                    SELECT item_name, item_type, item_power, quantity 
                    FROM inventory_items WHERE save_id = ?
                """, (save_id,))
                inventory_items = cursor.fetchall()
                
                cursor.execute("""
                    SELECT enemy_index, position_x, position_y, health, max_health, armor, max_armor, enemy_type
                    FROM enemies WHERE save_id = ? ORDER BY enemy_index
                """, (save_id,))
                enemies_data = cursor.fetchall()
                
                cursor.execute("""
                    SELECT item_index, position_x, position_y, item_name, item_type, item_power, icon
                    FROM world_items WHERE save_id = ? ORDER BY item_index
                """, (save_id,))
                world_items_data = cursor.fetchall()

                cursor.execute("""
                    SELECT room_from, room_to FROM map_connections WHERE save_id = ?
                """, (save_id,))
                connections_data = cursor.fetchall()

                cursor.execute("""
                    SELECT room_x, room_y FROM visited_rooms WHERE save_id = ?
                """, (save_id,))
                visited_data = cursor.fetchall()

                return {
                    'player': player_data,
                    'game': game_data,
                    'inventory': inventory_items,
                    'enemies': enemies_data,
                    'world_items': world_items_data,
                    'map_connections': connections_data,
                    'visited_rooms': visited_data,
                }
            
            except Exception as e:
                print(f"\n❌ Ошибка при загрузке: {e}")
                return None