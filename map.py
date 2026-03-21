import random
from random import choice
import copy

class Map:
    def __init__(self, height = 10, width: int = 10):
        self.width = width
        self.height = height
        self.map = {}
    

    def generate_map(self):
        k = self.width
        area = self.height*self.width

        for i in range(1, area + 1):
            self.map[i] = set()

        for i in range(1, area + 1):
            if i + k <= area:
                self.map[i].add(i + k)
                self.map[i + k].add(i)

            if i + 1 <= area and i % k:
                self.map[i].add(i + 1)
                self.map[i + 1].add(i)

        for i in self.map:
            route = choice(list(self.map[i]))
            if any([len(list(self.map[i])) == 2, len(list(self.map[route])) == 2]):
                continue
            self.map[i].remove(route)
            self.map[route].remove(i)
            

class Interface:
    def __init__(self, map: Map, entities: list):
        self.map = map
        self.entities = entities
    
    def draw(self, height, width):
        k = -width
        for _ in range(height):
            k += width
            for j in range(k + 1, width + k):
                print(0, end = " ")
                if j in self.map.map[j + 1]:
                    print("-", end=" ")
                else:
                    print(end="  ")
            print(0)
            try:            
                for j in range(k + 1, width + k + 1):
                    if j in self.map.map[j + width]:
                        print("|", end="   ")
                    else:
                        print(end="    ")
            except KeyError:
                continue
            print()



    
m = Map(3, 3)

m.generate_map()
k = Interface(m, [1, 2, 3])


k.draw(3, 3)
