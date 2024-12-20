from .Command import Command

class UpdateParticlesCommand(Command):
    def __init__(self, particles):
        self.particles = particles
    
    def run(self):
        for particle in self.particles:
            if particle.lifetime > 0:
                particle.update()