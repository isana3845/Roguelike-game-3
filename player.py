class Vector2:
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def normalize(self):
        absolute = abs(self)
        self.x /= absolute
        self.y /= absolute
        self.z /= absolute
        return Vector2(self.x / absolute, self.y / absolute)

    def __contains__(self, item):
        return item in [self.x, self.y]

    def __repr__(self):
        return f"X: {self.x} Y: {self.y}"
    
    @staticmethod
    def up(direction = -1):
        return Vector2(0, -1*direction)

    @staticmethod
    def right(direction = 1):
        return Vector2(1*direction, 0)

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
    
    
class Player:
    def __init__(self, coords: Vector2, health: int, max_health: int, armor: int, max_armor: int):
        self.position = coords
        self.health = health
        self.max_health = max_health
        self.max_armor = max_armor
        self.armor = armor

    def move(self, direction: Vector2):
        self.position += direction


class Enemy(Player):
    def __init__(self, coords, health, armor):
        super().__init__(coords, health, armor)


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