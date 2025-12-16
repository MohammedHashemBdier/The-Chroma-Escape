from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class DFSSolver(SearchAlgorithm):
    def __init__(self):
        super().__init__("DFS")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        frontier = [initial_state]
        explored: Set[GameState] = set()
        
        # تحديث أفضل حالة بالحالة الأولية
        self.best_state_found = initial_state
        self.best_score = self._evaluate_state(initial_state)
        
        print(f"Starting DFS solver...")
        
        depth_limit = 500  # حد العمق لتجنب التعمق الشديد
        iteration = 0
        
        while frontier:
            state = frontier.pop()
            self.nodes_explored += 1
            
            if state in explored:
                continue
            explored.add(state)

            # تحديث أفضل حالة
            self._update_best_state(state)

            iteration += 1
            if iteration % 1000 == 0:
                print(f"DFS: Nodes explored: {self.nodes_explored}, Current depth: {state.depth}")

            if state.check_win_condition():
                print(f"DFS Solution found! Total nodes explored: {self.nodes_explored}")
                return self.reconstruct_path(state)
            
            # تطبيق حدود العمق
            if state.depth < depth_limit:
                for next_state, action in state.get_possible_moves():
                    if next_state not in explored:
                        frontier.append(next_state)
        
        # إذا وصلنا هنا ولم نجد حل، نعيد أفضل حالة
        print(f"DFS: No solution found. Best state has {len(self.best_state_found.blocks)} blocks remaining.")
        print(f"Total nodes explored: {self.nodes_explored}")
        
        return self.reconstruct_path(self.best_state_found)