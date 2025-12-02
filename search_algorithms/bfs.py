from collections import deque
from typing import List, Optional, Set
from model import GameState
from .base import SearchAlgorithm

class BFSSolver(SearchAlgorithm):
    def __init__(self):
        super().__init__("BFS")

    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        if initial_state.check_win_condition():
            print("BFS: Already at win condition!")
            return [initial_state]

        frontier = deque([initial_state])
        explored: Set[GameState] = set()
        
        # لتخزين أفضل حالة
        self.best_state_found = initial_state
        self.best_score = self._evaluate_state(initial_state)
        
        print(f"BFS: Starting solver from state with {len(initial_state.blocks)} blocks")
        print("Blocks in initial state:")
        for block in initial_state.blocks:
            print(f"  ID: {block.id}, Color: {block.color}, Pos: ({block.x}, {block.y}), Lock: {block.move_lock}")
        
        # لتخزين الوالدين لمسار الحل
        parent_map = {initial_state: None}
        
        iteration = 0
        while frontier:
            state = frontier.popleft()
            iteration += 1
            
            if state in explored:
                continue
            explored.add(state)

            self.nodes_explored += 1
            self._update_best_state(state)

            # طباعة التقدم
            if iteration % 1000 == 0:
                print(f"BFS: Nodes explored: {self.nodes_explored}, Frontier: {len(frontier)}")

            if state.check_win_condition():
                print(f"BFS Solution found! Total nodes explored: {self.nodes_explored}")
                print(f"Solution depth: {state.depth}")
                
                # إضافة طباعة لمسار الحل للتحقق
                solution_states = self.reconstruct_path(state)
                print(f"Solution path has {len(solution_states)} states:")
                for i, sol_state in enumerate(solution_states):
                    block_ids = [block.id for block in sol_state.blocks]
                    print(f"  State {i}: {len(sol_state.blocks)} blocks, IDs: {block_ids}")
                
                return solution_states

            possible_moves = state.get_possible_moves()
            
            # تصفية الحركات الصالحة فقط
            valid_moves = []
            for next_state, action in possible_moves:
                block_id, dx, dy, distance = action
                if state.is_move_valid(block_id, (dx, dy), distance):
                    valid_moves.append((next_state, action))
            
            if iteration <= 3 and valid_moves:  # طباعة أول 3 حركات
                print(f"BFS: State {iteration} has {len(valid_moves)} valid moves")
                for next_state, action in valid_moves[:3]:
                    print(f"  Move: {action}, Next blocks: {len(next_state.blocks)}")
            
            for next_state, action in valid_moves:
                if next_state not in explored and next_state not in frontier:
                    parent_map[next_state] = state
                    frontier.append(next_state)
        
        # إذا وصلنا هنا ولم نجد حل، نعيد أفضل حالة
        print(f"BFS: No solution found. Best state has {len(self.best_state_found.blocks)} blocks remaining.")
        print(f"Total nodes explored: {self.nodes_explored}")
        
        # إذا كانت أفضل حالة هي الحالة الأولية، نعيدها فقط
        if self.best_state_found == initial_state:
            return [initial_state]
        
        # إعادة بناء المسار إلى أفضل حالة
        path = []
        current = self.best_state_found
        while current is not None:
            path.append(current)
            current = parent_map.get(current)
        return list(reversed(path))