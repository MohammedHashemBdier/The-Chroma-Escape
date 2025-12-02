import heapq
from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class UCSSolver(SearchAlgorithm):
    def __init__(self):
        super().__init__("UCS")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        frontier = []
        heapq.heappush(frontier, (0, 0, initial_state))
        explored: Set[GameState] = set()
        counter = 1
        
        # تحديث أفضل حالة بالحالة الأولية
        self.best_state_found = initial_state
        self.best_score = self._evaluate_state(initial_state)
        
        print(f"Starting UCS solver...")

        while frontier:
            cost, _, state = heapq.heappop(frontier)
            self.nodes_explored += 1
            
            if state in explored:
                continue
            explored.add(state)

            # تحديث أفضل حالة
            self._update_best_state(state)

            if self.nodes_explored % 1000 == 0:
                print(f"UCS: Nodes explored: {self.nodes_explored}")

            if state.check_win_condition():
                print(f"UCS Solution found! Total nodes explored: {self.nodes_explored}")
                return self.reconstruct_path(state)

            for next_state, action in state.get_possible_moves():
                if next_state not in explored:
                    new_cost = cost + 1
                    heapq.heappush(frontier, (new_cost, counter, next_state))
                    counter += 1
        
        # إذا وصلنا هنا ولم نجد حل، نعيد أفضل حالة
        print(f"UCS: No solution found. Best state has {len(self.best_state_found.blocks)} blocks remaining.")
        print(f"Total nodes explored: {self.nodes_explored}")
        
        return self.reconstruct_path(self.best_state_found)