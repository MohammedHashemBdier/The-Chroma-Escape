from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class DFSRecursiveSolver(SearchAlgorithm):
    def __init__(self):
        super().__init__("DFS (Recursive)")
        self.explored: Set[GameState] = set()
        self.depth_limit = 500

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            return [initial_state]

        self.explored = set()
        self.best_state_found = initial_state
        self.best_score = self._evaluate_state(initial_state)
        self.nodes_explored = 0
        
        print(f"Starting DFS Recursive solver...")
        
        solution = self._dfs_recursive(initial_state, 0)
        
        if solution:
            print(f"DFS Recursive: Solution found! Total nodes explored: {self.nodes_explored}")
            return solution
        else:
            print(f"DFS Recursive: No solution found. Best state has {len(self.best_state_found.blocks)} blocks remaining.")
            print(f"Total nodes explored: {self.nodes_explored}")
            
            if len(self.best_state_found.blocks) >= len(initial_state.blocks):
                return [initial_state]
            
            return self.reconstruct_path(self.best_state_found)

    def _dfs_recursive(self, state: GameState, depth: int) -> Optional[List[GameState]]:
        if state in self.explored:
            return None
        
        self.explored.add(state)
        self.nodes_explored += 1
        
        self._update_best_state(state)
        
        if self.nodes_explored % 1000 == 0:
            print(f"DFS Recursive: Nodes explored: {self.nodes_explored}, Current depth: {depth}")

        if state.check_win_condition():
            print(f"Solution found at depth {depth}!")
            return self.reconstruct_path(state)
        
        if depth >= self.depth_limit:
            return None
        
        possible_moves = state.get_possible_moves()
        possible_moves.sort(key=lambda x: self._evaluate_state(x[0]))
        
        for next_state, action in possible_moves:
            if next_state not in self.explored:
                solution = self._dfs_recursive(next_state, depth + 1)
                if solution:
                    return solution
        
        return None
