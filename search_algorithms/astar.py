import heapq
from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class AStarSolver(SearchAlgorithm):
    def __init__(self):
        super().__init__("A*")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        frontier = []
        heapq.heappush(frontier, (self._evaluate_state(initial_state), 0, 0, initial_state))
        explored: Set[GameState] = set()
        counter = 1
        
        self.best_state_found = initial_state
        self.best_score = self._evaluate_state(initial_state)
        
        print(f"Starting A* solver...")
        
        while frontier:
            f_cost, g_cost, _, state = heapq.heappop(frontier)
            self.nodes_explored += 1
            
            if state in explored:
                continue
            explored.add(state)

            self._update_best_state(state)

            if self.nodes_explored % 1000 == 0:
                print(f"A*: Nodes explored: {self.nodes_explored}")

            if state.check_win_condition():
                print(f"A* Solution found! Total nodes explored: {self.nodes_explored}")
                return self.reconstruct_path(state)

            for next_state, action in state.get_possible_moves():
                if next_state not in explored:
                    g_new = g_cost + 1
                    h_new = self._evaluate_state(next_state)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, g_new, counter, next_state))
                    counter += 1
        
        print(f"A*: No solution found. Best state has {len(self.best_state_found.blocks)} blocks remaining.")
        print(f"Total nodes explored: {self.nodes_explored}")
        
        if len(self.best_state_found.blocks) >= len(initial_state.blocks):
            return [initial_state]
        
        return self.reconstruct_path(self.best_state_found)