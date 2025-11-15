from collections import deque
from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class BFSSolver(SearchAlgorithm):
    """
    خوارزمية البحث بالعرض (Breadth-First Search).
    تضمن إيجاد الحل الأمثل (الأقصر) من حيث عدد الخطوات.
    """
    def __init__(self):
        super().__init__("BFS")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        # frontier (الحافة) هي طابور FIFO
        frontier = deque([initial_state])
        # explored (المستكشفة) هي مجموعة لتجنب تكرار الحالات
        explored: Set[GameState] = {initial_state}

        while frontier:
            state = frontier.popleft()
            self.nodes_explored += 1

            for next_state, _ in state.get_possible_moves():
                if next_state.check_win_condition():
                    return self.reconstruct_path(next_state)

                if next_state not in explored:
                    explored.add(next_state)
                    frontier.append(next_state)
        
        return None