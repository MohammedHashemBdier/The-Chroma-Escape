import random
from typing import List, Optional
from model import GameState
from .base import SearchAlgorithm

class HillClimbingSolver(SearchAlgorithm):
    
    def __init__(self, max_steps: int = 500):
        super().__init__("Simple Hill Climbing")
        self.max_steps = max_steps
        self.best_state_found = None
        self.best_score = float('inf')
    
    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        self.best_state_found = initial_state
        self.best_score = self._simple_evaluate(initial_state)
        
        current = initial_state
        path = [current]
        
        print(f"Simple HC: Starting with {len(current.blocks)} blocks, max {self.max_steps} steps")
        print(f"Initial score: {self.best_score:.1f}")
        
        for step in range(self.max_steps):
            self.nodes_explored += 1
            
            if current.check_win_condition():
                print(f"✅ Simple HC: Solved in {step} steps!")
                return path
            
            moves = current.get_possible_moves()
            if not moves:
                print(f"❌ Simple HC: No moves at step {step}")
                break
            
            current_score = self._simple_evaluate(current)
            
            if current_score < self.best_score:
                self.best_state_found = current
                self.best_score = current_score
            
            found_better = False
            random.shuffle(moves)
            
            for next_state, action in moves:
                if next_state is None:
                    continue
                    
                next_score = self._simple_evaluate(next_state)
                
                if next_score < current_score:
                    current = next_state
                    path.append(current)
                    found_better = True
                    
                    if step < 10:
                        block_id, dx, dy, dist = action
                        direction = "UP" if dy < 0 else "DOWN" if dy > 0 else "LEFT" if dx < 0 else "RIGHT"
                        print(f"  Step {step}: Block {block_id} {direction} (score: {next_score:.1f})")
                    break
            
            if not found_better:
                valid_moves = [(ns, act) for ns, act in moves if ns is not None]
                if valid_moves:
                    next_state, _ = random.choice(valid_moves)
                    current = next_state
                    path.append(current)
                    
                    if step < 10:
                        current_score = self._simple_evaluate(current)
                        print(f"  Step {step}: Random move (score: {current_score:.1f})")
        
        print(f"Simple HC: Finished after {self.max_steps} steps")
        
        if self.best_state_found is None:
            print("Warning: best_state_found is None, returning initial state")
            return [initial_state]
        
        print(f"Best state: {len(self.best_state_found.blocks)} blocks remaining")
        print(f"Best score: {self.best_score:.1f}")
        
        return self._get_path_to_best(path, initial_state)
    
    def _simple_evaluate(self, state: GameState) -> float:
        if state is None:
            return float('inf')
            
        if state.check_win_condition():
            return 0
        
        score = len(state.blocks) * 10
        
        for block in state.blocks:
            min_dist = 100
            for (x, y), exit_info in state.board.exits.items():
                if exit_info.get("color", "").lower() == block.color.lower():
                    dist = abs(block.x - x) + abs(block.y - y)
                    min_dist = min(min_dist, dist)
            
            score += min_dist * 0.5
        
        return score
    
    def _get_path_to_best(self, path: List[GameState], initial_state: GameState) -> List[GameState]:
        if not path:
            return [self.best_state_found] if self.best_state_found else [initial_state]
        
        if self.best_state_found is None:
            return [initial_state]
        
        best_idx = 0
        best_blocks = len(path[0].blocks) if path[0] else float('inf')
        
        for i, state in enumerate(path):
            if state is None:
                continue
            if len(state.blocks) < best_blocks:
                best_blocks = len(state.blocks)
                best_idx = i
        
        return path[:best_idx + 1]