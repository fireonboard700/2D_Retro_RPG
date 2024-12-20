from .Layer import Layer

class BulletsLayer(Layer):
    def __init__(self, user_interface, tileset, game_state, bullets):
        super().__init__(user_interface, tileset)
        self.game_state = game_state
        self.bullets = bullets

    def render(self, surface):
        for bullet in self.bullets:
            if bullet.health != 0:
                self.draw_tile(surface, bullet.position, bullet.tile)