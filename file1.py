from file import Vector2
import keyboard
import time

l = []
with open("settings.txt", "r") as f:
    for i in f.readlines():
        l += list(map(int, i.split()))


class Player:
    def __init__(self, coords: Vector2, health: int, armor: int):
        self.position = coords
        self.health = health
        self.armor = armor

    def move(self, direction: Vector2):
        self.position += direction

class Interface:
    def __init__(self, player: Player):
        self.player = player
    def __call__(self):
        print(f"\033[1;{l[1]*l[2] + 2}HPlayer:")
        print(f"\033[2;{l[1]*l[2] + 4}HHP: {self.player.health}")
        print(f"\033[3;{l[1]*l[2] + 4}HArmor: {self.player.armor}")


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
                self.inv[item.title] -= 1
                if not self.inv[item.title]:
                    self.inv.pop(item.title)
        except KeyError:
            print(f"There is no such item as {item}")
            time.sleep(1)
        
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
                print(f"   \033[7;92m{self.inv[j]}\033[0m", end = " ")
            else:
                print(f"   {self.inv[j]}", end = " ")
        print("\n\n   1 - pop item  2 - use item  i - for inventory  esc - to close")