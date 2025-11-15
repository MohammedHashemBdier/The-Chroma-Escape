from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class DFSSolver(SearchAlgorithm):
    """
    خوارزمية البحث بالعمق (Depth-First Search).
    ليست مثالية، لكنها تستهلك ذاكرة أقل.
    """
    def __init__(self):
        super().__init__("DFS")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        # frontier (الحافة) هي مكدس LIFO
        frontier = [initial_state]
        # explored (المستكشفة) هي مجموعة لتجنب تكرار الحالات
        explored: Set[GameState] = {initial_state}

        while frontier:
            state = frontier.pop()
            self.nodes_explored += 1

            for next_state, _ in state.get_possible_moves():
                if next_state.check_win_condition():
                    return self.reconstruct_path(next_state)

                if next_state not in explored:
                    explored.add(next_state)
                    frontier.append(next_state)
        
        return None