import pygame
from pygame import Vector2
from ..state.GameState import GameState
from ..layers.TileMapLayer import TileMapLayer
from ..layers.UnitsLayer import UnitsLayer
from ..layers.BulletsLayer import BulletsLayer
from ..layers.ParticlesLayer import ParticlesLayer
from ..commands.MoveUnitCommand import MoveUnitCommand
from ..commands.ShootCommand import ShootCommand
from ..commands.MoveEnemiesCommand import MoveEnemiesCommand
from ..commands.EnemyDamageCommand import EnemyDamageCommand
from ..commands.MoveBulletCommand import MoveBulletCommand
from ..commands.UpdateParticlesCommand import UpdateParticlesCommand
from ..commands.DeleteDestroyedUnitsCommand import DeleteDestroyedUnitsCommand

class UserInterface:
    def __init__(self):
        pygame.init()
        
        self.game_state = GameState()
        self.cell_size = Vector2(32, 32)
        window_size = self.game_state.world_size.elementwise() * self.cell_size
        self.window = pygame.display.set_mode((int(window_size.x), int(window_size.y)))
        
        self.layers = [
            TileMapLayer(self, "assets/tiles.png", self.game_state),    
            UnitsLayer(self, "assets/player_sprites.png", self.game_state, self.game_state.units),
            BulletsLayer(self, "assets/fireball.png", self.game_state, self.game_state.bullets),
            ParticlesLayer(self, "assets/particle.png", self.game_state),
        ]
        
        for layer in self.layers:
            self.game_state.add_observer(layer)

        self.commands = []
        self.player_unit = self.game_state.units[0]
        pygame.display.set_caption("2D Retro RPG!")
        self.clock = pygame.time.Clock()
        self.running = True

    def process_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                if event.key == pygame.K_SPACE:
                    self.commands.append(ShootCommand(self.game_state, self.player_unit, self.player_unit.orientation))

        direction = Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: direction.y -= 1
        if keys[pygame.K_DOWN]: direction.y += 1
        if keys[pygame.K_LEFT]: direction.x -= 1
        if keys[pygame.K_RIGHT]: direction.x += 1
                
        self.commands.extend([
            MoveUnitCommand(self.game_state, self.player_unit, direction),
            MoveEnemiesCommand(self.game_state),
            EnemyDamageCommand(self.game_state)
        ])
        
        for bullet in self.game_state.bullets:
            self.commands.append(MoveBulletCommand(self.game_state, bullet))

        self.commands.extend([
            UpdateParticlesCommand(self.game_state.particles),
            DeleteDestroyedUnitsCommand(self.game_state.bullets),
            DeleteDestroyedUnitsCommand(self.game_state.particles),
            DeleteDestroyedUnitsCommand(self.game_state.units)
        ])
                
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