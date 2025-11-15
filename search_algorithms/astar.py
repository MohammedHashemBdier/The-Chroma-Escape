import heapq
from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class AStarSolver(SearchAlgorithm):
    """
    خوارزمية A* (A-Star).
    تجمع بين تكلفة المسار g(n) والتقييم h(n).
    تضمن إيجاد الحل الأمثل إذا كانت h(n) مقبولة (admissible).
    """
    def __init__(self):
        super().__init__("A*")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        # frontier (الحافة) هي قائمة أولويات (heap)
        # العنصر في الـ heap هو (f(n), g(n), العداد, الحالة)
        # حيث f(n) = g(n) + h(n)
        frontier = [(initial_state.evaluate_state(), 0, 0, initial_state)]
        heapq.heapify(frontier)
        explored: Set[GameState] = {initial_state}
        counter = 1

        while frontier:
            _, g, _, state = heapq.heappop(frontier)
            self.nodes_explored += 1

            for next_state, _ in state.get_possible_moves():
                if next_state.check_win_condition():
                    return self.reconstruct_path(next_state)

                if next_state not in explored:
                    g_new = g + 1
                    h_new = next_state.evaluate_state()
                    f_new = g_new + h_new
                    explored.add(next_state)
                    heapq.heappush(frontier, (f_new, g_new, counter, next_state))
                    counter += 1
        
        return None