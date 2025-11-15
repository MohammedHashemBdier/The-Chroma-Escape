import heapq
from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class GreedySolver(SearchAlgorithm):
    """
    خوارزمية البحث الجشع (Greedy Best-First Search).
    تستخدم دالة التقييم h(n) فقط. سريعة ولكن غير مضمونة الأمثلية.
    """
    def __init__(self):
        super().__init__("Greedy")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        # frontier (الحافة) هي قائمة أولويات (heap)
        # العنصر في الـ heap هو (التقييم, العداد, الحالة)
        frontier = [(initial_state.evaluate_state(), 0, initial_state)]
        heapq.heapify(frontier)
        explored: Set[GameState] = {initial_state}
        counter = 1

        while frontier:
            _, _, state = heapq.heappop(frontier)
            self.nodes_explored += 1

            for next_state, _ in state.get_possible_moves():
                if next_state.check_win_condition():
                    return self.reconstruct_path(next_state)

                if next_state not in explored:
                    explored.add(next_state)
                    heapq.heappush(frontier, (next_state.evaluate_state(), counter, next_state))
                    counter += 1
        
        return None