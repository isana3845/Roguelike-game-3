from file import Vector2
import keyboard
import time

class Item:
    def __init__(self, title, ty, ch):
        self.title = title
        self.ty = ty
        self.ch = ch
    
    def __repr__(self):
        return f"{self.title}: {self.ty}, {self.ch}"


class Inventory:
    def __init__(self):
        self.inv = {}
        self.order = 0
        self.chosen_item = None
    
    def add_item(self, *items: tuple[Item]):
        for item in items:
            if item.title.lower() not in self.inv:
                self.inv[item.title.lower()] = [item, 0]
            self.inv[item.title.lower()][1] += 1
    
    def pop_item(self, *items: tuple[Item]):
        try:
            for item in items:
                self.inv[item.lower()][1] -= 1
                if not self.inv[item.lower()][1]:
                    if self.order > 0:
                        self.order -= 1
                    self.inv.pop(item.lower())
        except KeyError:
            print(f"There is no such item as {item}")
            time.sleep(5)
        
    def change_item(self, d = 0):
        if self.order + d not in [-1, len(self.inv)]:
            self.order += d

    def __call__(self):
        print("┌──────────────────────────────────┐")
        print("|   MEGA COOL INVETORY TYPE SHI~   |")
        print("└──────────────────────────────────┘")
        if not(self.inv):
            print("Empty... you're cooked by now")
        for i, j in enumerate(self.inv):
            if i == self.order:
                self.chosen_item = j
                print(f"\033[7;92m{j}: {self.inv[j][1]}\033[0m", end = " ")
            else:
                print(f"{j}: {self.inv[j][1]}", end = " ")
        print("\nCharacteristics:")
        try:
            item = self.inv[self.chosen_item][0]
            match item.ty:
                case "weapon":
                    print(f"Damage: {item.ch}")
                case "healing":
                    print(f"Restores {item.ch} HP")
                case "armor":
                    print(f"Gives you {item.ch} armor")
                case _:
                    print("i dunno...")
        except KeyError:
            print("Cant access any item!")
        print("\n\nx - destroy item  e - use item  i - for inventory  esc - to close")

class Player:
    def __init__(self, coords: Vector2, health: int, max_health: int, armor: int, max_armor: int, inv = Inventory()):
        self.position = coords
        self.health = health
        self.max_health = max_health
        self.max_armor = max_armor
        self.armor = armor
        self.inv = inv

    def move(self, direction: Vector2):
        self.position += direction

    def player_inventory(self, act):
        match act:
            case "a":
                self.inv.order -= 1
            case "d":
                self.inv.order += 1
            case "x":
                self.inv.pop_item(self.inv.chosen_item)
            case "e":
                item = self.inv.inv[self.inv.chosen_item][0]
                if item.ty == "weapon":
                    print(f"You equiped {item.title}")
                elif item.ty == "healing":
                    if self.health < self.max_health:
                        self.health += item.ch - (self.health + item.ch)%self.max_health
                        print(f"You restored your health by {item.ch}")
                        self.inv.pop_item(self.inv.chosen_item)
                    else:
                        print("You're healthy bitch! Chill")
                elif item.ty == "armor":
                    if self.armor < self.max_armor:
                        self.armor += item.ch
                        print(f"You equiped {self.inv.chosen_item}")
                        self.inv.pop_item(self.inv.chosen_item)
                    else:
                        print("You're helluva armored bitch! Can you chill?")
                time.sleep(1)
            case _:
                print("Nah...")
                    
            

    def attack(self, target):
        ...

class Enemy(Player):
    def __init__(self, coords, health, armor, type):
        super().__init__(coords, health, armor)
        self.type = type


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
        inventory = self.player.inv
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
        lines.append(f"┌{'─' * (self.width - 2)}┐")
        lines.append(f"│{"MEGA COOL INVETORY TYPE SHI~":^{self.width - 2}}│")
        lines.append(f"└{'─' * (self.width - 2)}┘")
        if not(inventory.inv):
            lines.append(f"│{"Empty... you're cooked by now":^{self.width - 2}}│")
        for i, j in enumerate(inventory.inv):
            if i == inventory.order:
                inventory.chosen_item = j
                lines.append(f"\033[7;92m{j}: {inventory.inv[j][1]}\033[0m")
            else:
                lines.append(f"{j}: {inventory.inv[j][1]}")
        lines.append("x - destroy item  e - use item  i - for inventory  esc - to close")

        return lines
