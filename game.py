import pygame
from pygame import Vector2
from pygame import Rect
import math
import random 
import heapq  

class Command:
    def run(self):
        raise NotImplementedError()

class MoveUnitCommand(Command):
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
    def __init__(self, game_state, unit, direction, bullet_type):
        self.game_state = game_state    
        self.unit = unit
        self.direction = direction
        self.bullet_type = bullet_type
    
    def run(self):
        if self.unit.health == 0:
            return
        if self.game_state.epoch - self.unit.last_bullet_epoch < self.game_state.bullet_delay:
            return
        
        self.unit.last_bullet_epoch = self.game_state.epoch
        
        if self.bullet_type == "fireball":
            projectile = Fireball(self.game_state, self.unit, self.unit.orientation)
            self.game_state.bullets.append(projectile)

class MoveBulletCommand(Command):
    def __init__(self, game_state, bullet):
        self.game_state = game_state
        self.bullet = bullet
        
    def handle_collision(self, unit):
        unit.health -= self.bullet.damage
        
        knockback_strength = 0.5
        knockback_direction = self.bullet.direction.normalize()
        unit.position += knockback_direction * knockback_strength
        unit.position.x = max(0, min(unit.position.x, self.game_state.world_size.x - 1))
        unit.position.y = max(0, min(unit.position.y, self.game_state.world_size.y - 1))
        
        self.bullet.health = 0

    def run(self):
        new_bullet_position = self.bullet.position + self.bullet.direction * self.bullet.velocity

        if not self.game_state.is_inside_world(new_bullet_position):
            self.bullet.create_impact_particles()
            self.bullet.health = 0
            return
        
        if new_bullet_position.distance_to(self.bullet.start_position) >= self.bullet.range:
            self.bullet.create_impact_particles()
            self.bullet.health = 0
            return
        
        unit = self.game_state.check_unit_collision(new_bullet_position)
        if unit is not None and unit != self.bullet.unit:
            self.bullet.create_impact_particles()
            self.handle_collision(unit)
            return
        
        self.bullet.position = new_bullet_position
        self.bullet.update()

    def run(self):
        new_bullet_position = self.bullet.position + self.bullet.direction * self.bullet.velocity

        if not self.game_state.is_inside_world(new_bullet_position):
            self.bullet.create_impact_particles()
            self.bullet.health = 0
            return
        
        if new_bullet_position.distance_to(self.bullet.start_position) >= self.bullet.range:
            self.bullet.create_impact_particles()
            self.bullet.health = 0
            return
        
        unit = self.game_state.check_unit_collision(new_bullet_position)
        if unit is not None and unit != self.bullet.unit:
            self.bullet.create_impact_particles()
            self.handle_collision(unit)
            return
        
        self.bullet.position = new_bullet_position
        self.bullet.update()

class MoveEnemiesCommand(Command):
    def __init__(self, game_state):
        self.game_state = game_state
    
    def run(self):
        for unit in self.game_state.units:
            if isinstance(unit, Enemy):
                unit.update_path(self.game_state.player_unit.position)
                unit.move_along_path()

class UpdateParticlesCommand(Command):
    def __init__(self, particles):
        self.particles = particles
    
    def run(self):
        for particle in self.particles:
            if particle.lifetime > 0:
                particle.update()
class DeleteDestroyedUnitsCommand(Command):
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

class Enemy(Player): 
    def __init__(self, game_state, position):
        super().__init__(game_state, position, Vector2(2, 2))
        self.velocity = 0.05
        self.path = []
        self.path_update_delay = 30
        self.last_path_update = 0
    
    def update_path(self, target_pos):
        if self.game_state.epoch - self.last_path_update < self.path_update_delay:
            return
            
        self.last_path_update = self.game_state.epoch
        self.path = self.find_path(self.position, target_pos)
    
    def find_path(self, start, end):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        start_pos = (int(start.x), int(start.y))
        end_pos = (int(end.x), int(end.y))
        
        frontier = [(0, start_pos)]
        came_from = {start_pos: None}
        cost_so_far = {start_pos: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == end_pos:
                break
                
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]: 
                next_pos = (current[0] + dx, current[1] + dy)
                
                if (0 <= next_pos[0] < self.game_state.world_size.x and 
                    0 <= next_pos[1] < self.game_state.world_size.y):
                    new_cost = cost_so_far[current] + 1
                    
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + heuristic(end_pos, next_pos)
                        heapq.heappush(frontier, (priority, next_pos))
                        came_from[next_pos] = current
        
        path = []
        current = end_pos
        while current != start_pos:
            if current not in came_from:
                return [] 
            path.append(Vector2(current[0], current[1]))
            current = came_from[current]
        path.reverse()
        return path
    
    def move_along_path(self):
        if not self.path:
            return
            
        target = self.path[0]
        direction = target - self.position
        
        if direction.length() < self.velocity:
            self.position = target
            self.path.pop(0)
        else:
            self.is_moving = True
            normalized_dir = direction.normalize()
            self.position += normalized_dir * self.velocity
            self.orientation = normalized_dir
class SimpleParticle(GameUnit):
    def __init__(self, game_state, position, velocity, lifetime):
        super().__init__(game_state, position, Vector2(0, 0))
        self.lifetime = lifetime
        self.tile = Vector2(0, 0)
        self.next_move_time = random.randint(0, 10)  
        self.moves = [
                Vector2(0, -0.1),    # Up
                Vector2(0.1, 0),     # Right
            ]
        self.move_interval = 12  
        
    def update(self):
        self.lifetime -= 1
        if self.game_state.epoch >= self.next_move_time:
            
            move = random.choice(self.moves)
            self.position += move
            self.next_move_time = self.game_state.epoch + self.move_interval + random.randint(-2, 2)
    
class Fireball(GameUnit):
    def __init__(self, game_state, unit, direction):
        super().__init__(game_state, unit.position, Vector2(0, 1))
        self.unit = unit
        self.direction = direction
        self.start_position = unit.position.copy()
        self.velocity = 0.5
        self.range = 15
        self.damage = 25
        
        self.animation_frames = [Vector2(0, 0), Vector2(0, 1), Vector2(0, 2)]
        self.current_frame = 0
        self.animation_speed = 10
        self.tile = self.animation_frames[self.current_frame]
    
    def create_impact_particles(self):
        for _ in range(25):
            spread = 0.3
            position = self.position + Vector2(
                random.uniform(-spread, spread),
                random.uniform(-spread, spread)
            )
            velocity = Vector2(
                random.uniform(-0.08, 0.08),
                random.uniform(-0.08, 0.08)
            )
            particle = SimpleParticle(
                self.game_state,
                position,
                velocity,
                lifetime=random.randint(100, 300)
            )
            self.game_state.particles.append(particle)
    
    def update(self):
        if self.game_state.epoch % self.animation_speed == 0:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.tile = self.animation_frames[self.current_frame]
        
        if self.game_state.epoch % 3 == 0:
            num_particles = random.randint(1, 3)
            
            for _ in range(num_particles):
                spread = 0.15
                position = self.position + Vector2(
                    random.uniform(-spread, spread),
                    random.uniform(-spread, spread)
                )
                
                velocity = -self.direction * 0.005
                
                particle = SimpleParticle(
                    self.game_state,
                    position,
                    velocity,
                    lifetime=random.randint(100, 300)
                )
                self.game_state.particles.append(particle)

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

class TileMapLayer(Layer):
    def __init__(self, user_interface, tileset, game_state):
        super().__init__(user_interface, tileset)
        self.game_state = game_state
        self.tile_map = [
            [Vector2(0, 0) for _ in range(int(game_state.world_size.x))]
            for _ in range(int(game_state.world_size.y))
        ]
        self.generate_simple_map()
    
    def generate_simple_map(self):
        for y in range(len(self.tile_map)):
            for x in range(len(self.tile_map[0])):
                if random.random() < 0.1:  # 10% chance for variant
                    self.tile_map[y][x] = Vector2(1, 0)  # Variant floor tile
                else:
                    self.tile_map[y][x] = Vector2(0, 0)  # Basic floor tile
    
    def render(self, surface):
        for y in range(len(self.tile_map)):
            for x in range(len(self.tile_map[0])):
                self.draw_tile(surface, Vector2(x, y), self.tile_map[y][x])

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
        base_row = 2 if isinstance(unit, Enemy) else 0
        
        if unit.is_moving:
            frame = (self.game_state.epoch // self.frame_switch_threshold) % 2
            tile.y = base_row + frame  
        
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

class ParticlesLayer(Layer):
    def __init__(self, user_interface, tileset, game_state):
        super().__init__(user_interface, tileset)
        self.game_state = game_state

    def render(self, surface):
        # Render game_state particles directly
        for particle in self.game_state.particles:
            if particle.lifetime > 0:
                self.draw_tile(surface, particle.position, particle.tile)
class GameState:
    def __init__(self):
        self.epoch = 0
        self.world_size = Vector2(16, 16)
        self.player_unit = Player(self, Vector2(5, 4), Vector2(2, 0))
        self.units = [
            self.player_unit,
            Enemy(self, Vector2(14, 14)),  
            Enemy(self, Vector2(2, 14)),   
        ]
        self.bullet_delay = 15
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
                    TileMapLayer(self, "assets/tiles.png", self.game_state),    
                    UnitsLayer(self, "assets/player_sprites.png", self.game_state, self.game_state.units),
                    BulletsLayer(self, "assets/fireball.png", self.game_state, self.game_state.bullets),
                    ParticlesLayer(self, "assets/particle.png", self.game_state),  # Add particles layer
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
                    shoot_command = ShootCommand(self.game_state, self.player_unit, self.player_unit.orientation, "fireball")
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
                
        command = MoveUnitCommand(self.game_state, self.player_unit, direction)
        self.commands.append(command)
        self.commands.append(MoveEnemiesCommand(self.game_state))

        for bullet in self.game_state.bullets:
            self.commands.append(MoveBulletCommand(self.game_state, bullet))

        self.commands.append(UpdateParticlesCommand(self.game_state.particles))

        self.commands.append(DeleteDestroyedUnitsCommand(self.game_state.bullets))
        self.commands.append(DeleteDestroyedUnitsCommand(self.game_state.particles))
        self.commands.append(DeleteDestroyedUnitsCommand(self.game_state.units))
                
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
