import pygame
from pygame import Vector2
from pygame import Rect
import math

class Command:
    def run(self):
        raise NotImplementedError()

class MoveCommand(Command):
    def __init__(self, game_state, unit, direction):  
        self.game_state = game_state
        self.unit = unit
        self.direction = direction

    def run(self):
        if self.direction.length() > 0:
            new_position = self.unit.position + self.direction.normalize() * self.unit.velocity

            new_position.x = max(0, min(new_position.x, self.game_state.world_size.x - 1))
            new_position.y = max(0, min(new_position.y, self.game_state.world_size.y - 1))

            self.unit.position = new_position
            self.unit.orientation = self.direction.normalize()
            self.game_state.notify_unit_move(self.unit, self.direction)
        else:
            self.game_state.notify_unit_stop(self.unit)
            
class ShootCommand(Command):
    def __init__(self, game_state, unit, direction):
        self.game_state = game_state    
        self.unit = unit
        self.direction = direction
    
    def run(self):
        if self.unit.health == 0:
            return
        if self.game_state.epoch - self.unit.last_bullet_epoch < self.game_state.bullet_delay:
            return
        
        self.unit.last_bullet_epoch = self.game_state.epoch
        self.game_state.bullets.append(Bullet(self.game_state, self.unit, self.unit.orientation))

class MoveBulletCommand(Command):
    def __init__(self, game_state, bullet):
        self.game_state = game_state
        self.bullet = bullet
    def run(self):
    
        new_bullet_position = self.bullet.position + self.bullet.direction * self.bullet.velocity

        if not self.game_state.is_inside_world(new_bullet_position):
            self.bullet.health = 0
            return
        
        if new_bullet_position.distance_to(self.bullet.start_position) >= self.bullet.range:
            self.bullet.health = 0
            return
        
        unit = self.game_state.check_unit_collision(new_bullet_position)
        if unit is not None and unit != self.bullet.unit:
            self.bullet.health = 0
            unit.health = 0
            return
        
        self.bullet.position = new_bullet_position
class DeleteDestroyedCommand(Command):
    def __init__(self, item_list):
        self.item_list = item_list
    
    def run(self):
        new_list = [item for item in self.item_list if item.health != 0]
        self.item_list[:] = new_list
        
class GameUnit:
    def __init__(self, game_state, position, tile):
        self.game_state = game_state
        self.health = 100
        self.position = position
        self.tile = tile

class Player(GameUnit):
    def __init__(self, game_state, position, tile):
        super().__init__(game_state, position, tile)
        self.velocity = 0.1
        self.last_bullet_epoch = 0 
        self.orientation = Vector2(1, 0)
        self.is_moving = False    

class Bullet(GameUnit):
    def __init__(self, game_state, unit, direction):
        super().__init__(game_state, unit.position, Vector2(0, 0))
        self.unit = unit
        self.direction = direction
        self.start_position = unit.position.copy()
        self.velocity = 0.4
        self.range = 20

class GameStateObserver:
    def on_unit_move(self, unit, direction):
        pass

    def on_unit_stop(self, unit):
        pass        
class Layer(GameStateObserver):
    def __init__(self, user_interface, tileset):
        self.user_interface = user_interface
        self.tileset = pygame.image.load(tileset)
    
    def draw_tile(self, surface, position, tile):
        sprite_coords = position.elementwise() * self.user_interface.cell_size
        tile_coords = tile.elementwise() * self.user_interface.cell_size
        tile_rect = Rect(int(tile_coords.x), int(tile_coords.y), self.user_interface.cell_size.x, self.user_interface.cell_size.y)

        surface.blit(self.tileset, sprite_coords, tile_rect)
        
    def render(self, surface):
        raise NotImplementedError()

class UnitsLayer(Layer):
    def __init__(self, user_interface, tileset, game_state, units):
        super().__init__(user_interface, tileset)
        self.game_state = game_state
        self.units = units
        self.frame_switch_threshold = 15
    
    def on_unit_move(self, unit, direction):
        unit.is_moving = True
        
    def on_unit_stop(self, unit):
        unit.is_moving = False
        
    def get_unit_tile(self, unit):
        tile = unit.tile.copy()
        
        if unit.is_moving:
            frame = (self.game_state.epoch // self.frame_switch_threshold) % 2
            tile.y = frame  
        
        # Column 0: Right-facing sprites
        # Column 1: Left-facing sprites
        # Column 2: Down-facing sprites
        # Column 3: Up-facing sprites

        if unit.orientation.x > 0:  
            tile.x = 0
        elif unit.orientation.x < 0:
            tile.x = 1
        elif unit.orientation.y > 0:
            tile.x = 2
        elif unit.orientation.y < 0:
            tile.x = 3
            
        return tile
    
    def render(self, surface):
        for unit in self.units:
            current_position = unit.position
            current_tile = self.get_unit_tile(unit)
            self.draw_tile(surface, current_position, current_tile)
class BulletsLayer(Layer):
    def __init__(self, user_interface, image_file, game_state, bullets):
        super().__init__(user_interface, image_file)
        self.game_state = game_state
        self.bullets = bullets

    def render(self, surface):
        for bullet in self.bullets:
            if bullet.health != 0:
                self.draw_tile(surface, bullet.position, bullet.tile)

class GameState:
    def __init__(self):
        self.epoch = 0
        self.world_size = Vector2(16, 16)
        self.units = [
            Player(self, Vector2(5, 4), Vector2(2, 0)),
            Player(self, Vector2(5, 6), Vector2(2, 0)),
            Player(self, Vector2(5, 8), Vector2(2, 0)),
            Player(self, Vector2(5, 10), Vector2(2, 0))
        ]
        self.bullet_delay = 15
        self.bullets = []
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_unit_move(self, unit, direction):
        for observer in self.observers:
            observer.on_unit_move(unit, direction)
    
    def notify_unit_stop(self, unit):
        for observer in self.observers:
            observer.on_unit_stop(unit)
    
    def check_unit_collision(self, position: Vector2):
        for unit in self.units:
            if unit.health == 0:
                continue

            distance = position.distance_to(unit.position)
            collision_radius = 1 

            if distance < collision_radius:
                return unit
                
        return None

    def is_inside_world(self, position):
        return 0 <= position.x < self.world_size.x and 0 <= position.y < self.world_size.y
class UserInterface:
    def __init__(self):
        pygame.init()

        self.game_state = GameState()
        self.cell_size = Vector2(32, 32)
        
        window_size = self.game_state.world_size.elementwise() *  self.cell_size
        self.window = pygame.display.set_mode((int(window_size.x), int(window_size.y)))
        self.layers = [
                    UnitsLayer(self, "assets/player_sprites.png", self.game_state, self.game_state.units),
                    BulletsLayer(self, "assets/simple.png", self.game_state, self.game_state.bullets)
                ]
        
        for layer in self.layers:
            self.game_state.add_observer(layer)

        self.commands = []
        self.player_unit = self.game_state.units[0]

        pygame.display.set_caption("Battle of the Elements")
        self.clock = pygame.time.Clock()
        self.running = True
        

    def process_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                break  
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shoot_command = ShootCommand(self.game_state, self.player_unit, self.player_unit.orientation)
                    self.commands.append(shoot_command)

        direction = Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_RIGHT]:
            direction.x += 1
                
        command = MoveCommand(self.game_state, self.player_unit, direction)
        self.commands.append(command)

        for bullet in self.game_state.bullets:
            self.commands.append(MoveBulletCommand(self.game_state, bullet))

        self.commands.append(DeleteDestroyedCommand(self.game_state.bullets))
        self.commands.append(DeleteDestroyedCommand(self.game_state.units))
                
    def update(self):
        for command in self.commands:
            command.run()
        self.commands.clear()

        self.game_state.epoch += 1

    def render(self):
        self.window.fill((0, 0, 0))

        for layer in self.layers:
            layer.render(self.window)
            

        pygame.display.update()


    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)

ui = UserInterface()
ui.run()

pygame.quit()
