from pygame import Vector2
import random
from .GameUnit import GameUnit
from .SimpleParticle import SimpleParticle

class Fireball(GameUnit):
    def __init__(self, game_state, unit, direction):
        super().__init__(game_state, unit.position, Vector2(0, 1))
        self.unit = unit
        self.direction = direction
        self.start_position = unit.position.copy()
        self.velocity = 0.2
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
        # Handle animation frame updates
        if self.game_state.epoch % self.animation_speed == 0:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.tile = self.animation_frames[self.current_frame]
        
        # Create trail particles
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