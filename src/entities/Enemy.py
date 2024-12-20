from pygame import Vector2
import heapq
from .Player import Player

class Enemy(Player):
    def __init__(self, game_state, position):
        super().__init__(game_state, position, Vector2(2, 2))
        self.velocity = 0.03
        self.path = []
        self.path_update_delay = 30
        self.last_path_update = 0
    
    def update_path(self, target_pos):
        if self.game_state.epoch - self.last_path_update < self.path_update_delay:
            return
        self.last_path_update = self.game_state.epoch
        self.path = self.find_path(self.position, target_pos)
    
    # A* pathfinding implementation
    def find_path(self, start, end):
        def heuristic(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        start_pos = (int(start.x), int(start.y))
        end_pos = (int(end.x), int(end.y))
        
        frontier = [(0, start_pos)]
        came_from = {start_pos: None}
        cost_so_far = {start_pos: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            if current == end_pos: break
            
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
            if current not in came_from: return []
            path.append(Vector2(current[0], current[1]))
            current = came_from[current]
        path.reverse()
        return path
    
    def move_along_path(self):
        if not self.path: return
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