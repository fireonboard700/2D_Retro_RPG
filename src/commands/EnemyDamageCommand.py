from pygame import Vector2
from .Command import Command
from ..entities.Enemy import Enemy

class EnemyDamageCommand(Command):
    def __init__(self, game_state):
        self.game_state = game_state
        self.damage_amount = 5
        
    def run(self):
        player = self.game_state.player_unit
        for unit in self.game_state.units:
            if isinstance(unit, Enemy) and unit.health > 0:
                distance = player.position.distance_to(unit.position)
                if distance < 1.0:
                    knockback_vector = player.position - unit.position
                    knockback_dir = knockback_vector.normalize() if knockback_vector.length() > 0 else Vector2(1, 0)
                    
                    player.position += knockback_dir * 1.0
                    player.position.x = max(0, min(player.position.x, self.game_state.world_size.x - 1))
                    player.position.y = max(0, min(player.position.y, self.game_state.world_size.y - 1))
                    
                    player.health -= self.damage_amount
                    player.last_hit_epoch = self.game_state.epoch
                    break