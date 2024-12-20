from pygame import Vector2
import random
from ..entities.Player import Player
from ..entities.Enemy import Enemy

class GameState:
    def __init__(self):
        self.epoch = 0
        self.world_size = Vector2(16, 16)
        self.player_unit = Player(self, Vector2(5, 4), Vector2(2, 0))
        self.units = [
            self.player_unit,
            Enemy(self, Vector2(14, 14)),
            Enemy(self, Vector2(2, 14)),
            Enemy(self, Vector2(7, 12)),
            Enemy(self, Vector2(10, 1)),
        ]
        self.bullets = []
        self.particles = []
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_unit_move(self, unit, direction):
        for observer in self.observers:
            observer.on_unit_move(unit, direction)
    
    def notify_unit_stop(self, unit):
        for observer in self.observers:
            observer.on_unit_stop(unit)
    
    def check_unit_collision(self, position):
        for unit in self.units:
            if unit.health == 0:
                continue
            if position.distance_to(unit.position) < 1:
                return unit
        return None
    
    def spawn_enemy(self):
        while True:
            random_pos = Vector2(
                random.randint(0, int(self.world_size.x - 1)),
                random.randint(0, int(self.world_size.y - 1))
            )
            if not self.check_unit_collision(random_pos):
                self.units.append(Enemy(self, random_pos))
                break

    def is_inside_world(self, position):
        return (0 <= position.x < self.world_size.x and 
                0 <= position.y < self.world_size.y)