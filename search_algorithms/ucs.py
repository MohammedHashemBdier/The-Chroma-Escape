import heapq
from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class UCSSolver(SearchAlgorithm):
    """
    خوارزمية البحث بتكلفة موحدة (Uniform-Cost Search).
    تضمن إيجاد الحل الأمثل (الأقل تكلفة).
    في هذه اللعبة، بما أن تكلفة كل حركة هي 1، فإنها تعمل تماماً مثل BFS.
    """
    def __init__(self):
        super().__init__("UCS")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        # frontier (الحافة) هي قائمة أولويات (heap)
        # العنصر في الـ heap هو (التكلفة g(n), العداد, الحالة)
        frontier = [(0, 0, initial_state)]
        heapq.heapify(frontier)
        explored: Set[GameState] = {initial_state}
        counter = 1

        while frontier:
            cost, _, state = heapq.heappop(frontier)
            self.nodes_explored += 1

            for next_state, _ in state.get_possible_moves():
                if next_state.check_win_condition():
                    return self.reconstruct_path(next_state)

                if next_state not in explored:
                    new_cost = cost + 1
                    explored.add(next_state)
                    heapq.heappush(frontier, (new_cost, counter, next_state))
                    counter += 1
        
        return None