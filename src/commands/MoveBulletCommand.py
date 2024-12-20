from .Command import Command

class MoveBulletCommand(Command):
    def __init__(self, game_state, bullet):
        self.game_state = game_state
        self.bullet = bullet
        
    def handle_collision(self, unit):
        unit.health -= self.bullet.damage
        unit.last_hit_epoch = self.game_state.epoch
        knockback_direction = self.bullet.direction.normalize()
        unit.position += knockback_direction
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