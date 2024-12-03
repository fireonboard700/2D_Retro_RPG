import pygame
from pygame import Vector2
from pygame import Rect

class GameState:
    def __init__(self):
        self.world_size = Vector2(16, 10)
        self.plane_pos = Vector2(5, 5)

    def update(self, move_plane_command):
        self.plane_pos.x += move_plane_command.x
        self.plane_pos.y += move_plane_command.y


class UserInterface:
    def __init__(self):
        pygame.init()

        self.game_state = GameState()

        self.cell_size = Vector2(25, 15)
        self.move_plane_command = Vector2(0, 0)
        self.units_texture = pygame.image.load("assets/image.png")

        window_size = self.game_state.world_size.elementwise() *  self.cell_size
        self.window = pygame.display.set_mode((int(window_size.x), int(window_size.y)))

        pygame.display.set_caption("Dogfight")

        self.clock = pygame.time.Clock()
        self.running = True
        

    def process_input(self):
        self.move_plane_command = Vector2(0, 0)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.move_plane_command = Vector2(0, 1)
                if event.key == pygame.K_UP:
                    self.move_plane_command = Vector2(0, -1)
                if event.key == pygame.K_LEFT:
                    self.move_plane_command = Vector2(-1,0)
                if event.key == pygame.K_RIGHT:
                    self.move_plane_command = Vector2(1, 0)
    
    def update(self):
        self.game_state.update(self.move_plane_command)

    def render(self):
        self.window.fill((0,0,0))

        sprite_point = self.game_state.plane_pos.elementwise() * self.cell_size
        texture_point = Vector2(0, 0)
        texture_rect = Rect(int(texture_point.x), int(texture_point.y), self.cell_size.x, self.cell_size.y)
        self.window.blit(self.units_texture, sprite_point, texture_rect)

        pygame.display.update()


    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)

u = UserInterface()
u.run()

pygame.quit()
