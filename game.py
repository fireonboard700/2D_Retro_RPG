import pygame
from pygame import Vector2
from pygame import Rect
import math


class Unit:
    def __init__(self, game_state, position, tile, angle):
        self.game_state = game_state
        self.position = position
        self.tile = tile
        self.angle = angle

    def move(self):
        raise NotImplementedError()

class Plane(Unit):
    def __init__(self, game_state, position, tile, angle):
        super().__init__(game_state, position, tile, angle)
        self.velocity = 0.09

    def move(self, delta):
        self.angle += delta
        angle_in_radians = math.radians(self.angle)
        move_vector = Vector2(math.cos(angle_in_radians), -math.sin(angle_in_radians))
        if move_vector.y > 0: move_vector.y *= self.game_state.downward_bias
        else: move_vector.y *= self.game_state.upward_bias
        self.position += move_vector * self.velocity
        
        if self.position.x > (self.game_state.world_size.x + self.game_state.margin) or (self.position.x < -self.game_state.margin) \
        or self.position.y < -self.game_state.margin:
            self.angle = (self.angle + 180) % 360 


class Layer:
    def __init__(self, user_interface, tileset):
        self.user_interface = user_interface
        self.tileset = pygame.image.load(tileset)
    
    def draw_tile(self, surface, position, tile, angle):
        sprite_point = position.elementwise() * self.user_interface.cell_size
        texture_point = tile.elementwise() * self.user_interface.cell_size
        texture_rect = Rect(int(texture_point.x), int(texture_point.y), self.user_interface.cell_size.x, self.user_interface.cell_size.y)


        texture_tile = pygame.surface.Surface(self.user_interface.cell_size, pygame.SRCALPHA)
        texture_tile.blit(self.tileset, (0, 0), texture_rect)

        rotated_tile = pygame.transform.rotate(texture_tile, angle)

        sprite_point.x -= (rotated_tile.get_width() - texture_tile.get_width()) // 2
        sprite_point.y -= (rotated_tile.get_height() - texture_tile.get_height()) // 2

        surface.blit(rotated_tile, sprite_point)
        
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



class GameState:
    def __init__(self):
        self.world_size = Vector2(15, 35)
        self.units = [Plane(self, Vector2(5, 4), Vector2(0, 0), 0), Plane(self, Vector2(5, 5), Vector2(0, 0), 0)]
        self.downward_bias = 2.25  # Faster downward motion
        self.upward_bias = 1.5    # Slightly faster upward motion
        self.margin = 2

    def update(self, delta):
        for unit in self.units:
            unit.move(delta)


class UserInterface:
    def __init__(self):
        pygame.init()

        self.game_state = GameState()
        self.cell_size = Vector2(35, 15)
        self.delta = 0

        window_size = self.game_state.world_size.elementwise() *  self.cell_size
        self.window = pygame.display.set_mode((int(window_size.x), int(window_size.y)))

        self.layers = [UnitsLayer(self, "assets/image.png", self.game_state, self.game_state.units)]

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
                    self.delta = 2
                elif event.key == pygame.K_DOWN:
                    self.delta = -2
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.delta = 0
                
    def update(self):
        self.game_state.update(self.delta)

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
