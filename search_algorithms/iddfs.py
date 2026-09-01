from typing import List, Optional
from model import GameState
from .base import SearchAlgorithm

class IDDFSSolver(SearchAlgorithm):
    def __init__(self, max_depth: int = 50):
        super().__init__("IDDFS")
        self.max_depth = max_depth
        
    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]
        
        for depth_limit in range(1, self.max_depth + 1):
            print(f"IDDFS: Searching with depth limit {depth_limit}")
            result = self._depth_limited_search(initial_state, depth_limit)
            if result:
                print(f"IDDFS: Solution found at depth {depth_limit}")
                return result
        
        print(f"IDDFS: No solution found within depth {self.max_depth}")
        return None
    
    def _depth_limited_search(self, state: GameState, depth_limit: int) -> Optional[List[GameState]]:
        if state.check_win_condition():
            return [state]
        
        if depth_limit == 0:
            return None
        
        self.nodes_explored += 1
        
        for next_state, action in state.get_possible_moves():
            result = self._depth_limited_search(next_state, depth_limit - 1)
            if result:
                return [state] + result
        
        return None