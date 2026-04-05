from file import Vector2
import keyboard
import time


class Player:
    def __init__(self, coords: Vector2, health: int, max_health: int, armor: int, max_armor: int):
        self.position = coords
        self.health = health
        self.max_health = max_health
        self.max_armor = max_armor
        self.armor = armor

    def move(self, direction: Vector2):
        self.position += direction

class Interface:
    def __init__(self, player: Player, current_level=1):
        self.player = player
        self.width = 50
        self.height = 15
        self.level = current_level
        self.event_log = []
        self.max_events = 15


    def add_event(self, event_text: str):
        self.event_log.append(event_text)

        if len(self.event_log) > self.max_events:
            self.event_log.pop(0)
    

    def get_lines(self):
        lines = []

        lines.append(f"┌{'─' * (self.width - 2)}┐")
        lines.append(f"│{"Статус":^{self.width - 2}}│")
        lines.append(f"├{'─' * (self.width - 2)}┤")

        hp_color = '\033[91m' if self.player.health < (self.player.max_health * 0.4) else '\033[92m'
        reset = '\033[0m'
        hp_text = f"❤️  HP: {self.player.health}/{self.player.max_health}"
        hp_bar = f"{hp_color}{'█' * self.player.health}{'░' * (self.player.max_health - self.player.health)}{reset}"
        lines.append(f"│ {hp_text:<{self.width - 4}} │")
        lines.append(f"│ {hp_bar:<{self.width + 5}} │")

        armor_text = f"🛡️  ARMOR: {self.player.armor}/{self.player.max_armor}"
        armor_bar = f"\033[94m{'█' * self.player.armor}{'░' * (self.player.max_armor - self.player.armor)}\033[0m"
        lines.append(f"│ {armor_text:<{self.width - 4}} │")
        lines.append(f"│ {armor_bar:<{self.width + 5}} │")

        lines.append(f"│ {f"🎮  LEVEL: {self.level}":<{self.width - 5}} │")

        lines.append(f"├{'─' * (self.width - 2)}┤")
        lines.append(f"│{"Журнал собыйтий":^{self.width - 2}}│")
        lines.append(f"├{'─' * (self.width - 2)}┤")

        for i in range(self.height):
            if i < len(self.event_log):
                event = self.event_log[-(self.height - i)] if len(self.event_log) > self.height - i else self.event_log[i]

                if len(event) > self.width - 4:
                    event = event[:self.width - 7] + "..."
                lines.append(f"│ {event:<{self.width - 3}}│")
            else:
                lines.append(f"│{' ' * (self.width - 2)}│")

        lines.append(f"└{'─' * (self.width - 2)}┘")

        return lines


class Item:
    def __init__(self, title, ty, ch):
        self.title = title
        self.ty = ty
        self.ch = ch
    
    def __repr__(self):
        return f"{self.title}: {self.ty}, {self.ch}"
    

class Enemy(Player):
    def __init__(self, coords, health, armor, type):
        super().__init__(coords, health, armor)
        self.type = type
    
    


class Inventory:
    def __init__(self):
        self.inv = {}
        self.order = 0
        self.chosen_item = ""
    
    def add_item(self, *items: tuple[Item]):
        for item in items:
            if item.title not in self.inv:
                self.inv[item.title] = [item, 0]
            self.inv[item.title][1] += 1
    
    def pop_item(self, *items: tuple[Item]):
        try:
            for item in items:
                self.inv[item][1] -= 1
                if not self.inv[item][1]:
                    self.inv.pop(item)
        except KeyError:
            print(self.inv, item)
            print(f"There is no such item as {item}")
            time.sleep(5)
        
    def change_item(self, d = 0):
        if self.order + d not in [-1, len(self.inv)]:
            self.order += d
    
    def action(self, act):
        
        match act:
            case "1":
                keyboard.send("esc")
                self.pop_item(input("which item: "))
            case "2":
                print("potom pridumau")
                time.sleep(1)
            case "a":
                self.change_item(-1)
            case "d":
                self.change_item(1)
            case "e":
                print(self.chosen_item)
                time.sleep(1)
            case _:
                print("Nah...")
    
    def __getitem__(self, key):
        return self.inv[self.chosen_item]

    def __call__(self):
        print("   ------------------------------------")
        print("   |   MEGA COOL INVETORY TYPE SHI~   |")
        print("   ------------------------------------")
        if not(self.inv):
            print("   Empty... you're cooked by now")
        for i, j in enumerate(self.inv):
            if i == self.order:
                self.chosen_item = j
                print(f"   \033[7;92m{j}: {self.inv[j][1]}\033[0m", end = " ")
            else:
                print(f"   {j}: {self.inv[j][1]}", end = " ")
        print("\n\n   1 - pop item  2 - use item  i - for inventory  esc - to close")