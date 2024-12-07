import pygame
from pygame import Vector2
from pygame import Rect
import math

class Command:
    def run(self):
        raise NotImplementedError()

class MoveCommand(Command):
    def __init__(self, game_state, unit, delta):
        self.game_state = game_state
        self.unit = unit
        self.delta = delta

    def run(self):
        self.unit.angle = (self.unit.angle + self.delta) % 360
        angle_in_radians = math.radians(self.unit.angle)
        move_vector = Vector2(math.cos(angle_in_radians), -math.sin(angle_in_radians))
        self.unit.position += move_vector * self.unit.velocity
        
        # Boundary condition handling
        if self.unit.position.x > (self.game_state.world_size.x + self.game_state.margin) or \
        self.unit.position.x < -self.game_state.margin or \
        self.unit.position.y < -self.game_state.margin:
            self.unit.angle = (self.unit.angle + 180) % 360

class ShootCommand(Command):
    def __init__(self, game_state, unit):
        self.game_state = game_state    
        self.unit = unit
    
    def run(self):
        if self.unit.health == 0:
            return
        if self.game_state.epoch - self.unit.last_bullet_epoch < self.game_state.bullet_delay:
            return

        self.unit.last_bullet_epoch = self.game_state.epoch
        self.game_state.bullets.append(Bullet(self.game_state, self.unit))

class MoveBulletCommand(Command):
    def __init__(self, game_state, bullet):
        self.game_state = game_state
        self.bullet = bullet
    
    def run(self):
        new_bullet_position = self.bullet.position + self.game_state.bullet_speed * self.bullet.direction

        if not self.game_state.is_inside(new_bullet_position):
            self.bullet.health = 0
            return
        
        if new_bullet_position.distance_to(self.bullet.start_position) >= self.game_state.bullet_range:
            self.bullet.health = 0
            return
        
        unit = self.game_state.find_live_unit(new_bullet_position)
        if  unit is not None and unit != self.bullet.unit:
            self.bullet.health = 0
            unit.health = 0
            return
        
        self.bullet.position = new_bullet_position
        print(f"bullet at {self.bullet.position}")

class DeleteDestroyedCommand(Command):
    def __init__(self, item_list):
        self.item_list = item_list
    
    def run(self):
        new_list = [item for item in self.item_list if item.health != 0]
        self.item_list[:] = new_list
        

class GameUnit:
    def __init__(self, game_state, position, tile, angle):
        self.game_state = game_state
        self.health = 100
        self.position = position
        self.tile = tile
        self.angle = angle

class Plane(GameUnit):
    def __init__(self, game_state, position, tile, angle):
        super().__init__(game_state, position, tile, angle)
        self.velocity = 0.09
        self.weapon_target = Vector2(0,0)
        self.last_bullet_epoch = 0


class Bullet(GameUnit):
    def __init__(self, game_state, unit):
        super().__init__(game_state, unit.position, Vector2(0, 0), 0)
        self.unit = unit
        self.angle = unit.angle
 
        angle_in_radians = math.radians(self.unit.angle)
        self.direction = Vector2(math.cos(angle_in_radians), -math.sin(angle_in_radians)).normalize()

        # Adjust start position to be at the front of the plane
        # Use the unit's velocity to scale the offset
        self.start_position = unit.position + self.direction * self.unit.velocity * 3

        # Set the bullet's position to the start position
        self.position = self.start_position

class Layer:
    def __init__(self, user_interface, tileset):
        self.user_interface = user_interface
        self.tileset = pygame.image.load(tileset)
    
    def draw_tile(self, surface, position, tile, angle):
        sprite_coords = position.elementwise() * self.user_interface.cell_size
        tile_coords = tile.elementwise() * self.user_interface.cell_size
        tile_rect = Rect(int(tile_coords.x), int(tile_coords.y), self.user_interface.cell_size.x, self.user_interface.cell_size.y)

        tile_surface = pygame.surface.Surface(self.user_interface.cell_size, pygame.SRCALPHA)
        tile_surface.blit(self.tileset, (0, 0), tile_rect)

        rotated_tile = pygame.transform.rotate(tile_surface, angle)

        # shift sprite coords back to adjust for tile rotation
        sprite_coords.x -= (rotated_tile.get_width() - tile_surface.get_width()) // 2
        sprite_coords.y -= (rotated_tile.get_height() - tile_surface.get_height()) // 2

        surface.blit(rotated_tile, sprite_coords)
        
    def render(self, surface):
        raise NotImplementedError()

class UnitsLayer(Layer):
    def __init__(self, user_interface, tileset, game_state, units):
        super().__init__(user_interface, tileset)
        self.game_state = game_state
        self.units = units
    
    def render(self, surface):
        for unit in self.units:
            self.draw_tile(surface, unit.position, unit.tile, unit.angle)

class BulletsLayer(Layer):
    def __init__(self, user_interface, image_file, game_state, bullets):
        super().__init__(user_interface, image_file)
        self.game_state = game_state
        self.bullets = bullets

    def render(self, surface):
        for bullet in self.bullets:
            if bullet.health != 0:
                self.draw_tile(surface, bullet.position, bullet.tile, bullet.angle)


class GameState:
    def __init__(self):
        self.epoch = 0
        self.world_size = Vector2(30, 70)
        self.units = [Plane(self, Vector2(5, 4), Vector2(0, 0), 0)]
        self.margin = 2 # outer bound for sprites moving out of world

        self.bullets = []
        self.bullet_speed = 0.3
        self.bullet_range = 15
        self.bullet_delay = 15

    def is_inside(self, position):
        return 0 <= position.x < self.world_size.x and  0 <= position.y < self.world_size.y
    
    def find_unit(self, position):
        for unit in self.units:
            if int(unit.position.x) == int(position.x) and int(unit.position.y) == int(position.y):
                return unit
        
        return None
    
    def find_live_unit(self, position):
        unit = self.find_unit(position)

        if unit is None or unit.health == 0:
            return None

        return unit

class UserInterface:
    def __init__(self):
        pygame.init()

        self.game_state = GameState()
        self.cell_size = Vector2(35, 25)
        
        window_size = self.game_state.world_size.elementwise() *  self.cell_size
        self.window = pygame.display.set_mode((int(window_size.x), int(window_size.y)))
        self.layers = [UnitsLayer(self, "assets/plane.png", self.game_state, self.game_state.units), BulletsLayer(self, "assets/red_ball.png", self.game_state, self.game_state.bullets)]

        self.commands = []
        self.player_unit = self.game_state.units[0]
        self.delta = 0

        pygame.display.set_caption("Dogfight")
        self.clock = pygame.time.Clock()
        self.running = True
        

    def process_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                break  
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.delta = 3
                elif event.key == pygame.K_DOWN:
                    self.delta = -3
                elif event.key == pygame.K_SPACE:
                    shoot_command = ShootCommand(self.game_state, self.player_unit)
                    self.commands.append(shoot_command)
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.delta = 0
            
        command = MoveCommand(self.game_state, self.player_unit, self.delta)
        self.commands.append(command)

        for bullet in self.game_state.bullets:
            self.commands.append(MoveBulletCommand(self.game_state, bullet))

        self.commands.append(DeleteDestroyedCommand(self.game_state.bullets))
                
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
