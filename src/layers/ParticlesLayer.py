from .Layer import Layer

class ParticlesLayer(Layer):
    def __init__(self, user_interface, tileset, game_state):
        super().__init__(user_interface, tileset)
        self.game_state = game_state

    def render(self, surface):
        for particle in self.game_state.particles:
            if particle.lifetime > 0:
                self.draw_tile(surface, particle.position, particle.tile)