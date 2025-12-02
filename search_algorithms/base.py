from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from model import GameState

class SearchAlgorithm(ABC):
    """
    الفئة الأساسية التي ستسترشد بها جميع خوارزميات البحث.
    هذا يضمن واجهة موحدة.
    """
    def __init__(self, name: str):
        self.name = name
        self.nodes_explored = 0
        self.best_state_found = None
        self.best_score = float('inf')

    @abstractmethod
    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        """
        يجد حلاً للمشكلة انطلاقاً من الحالة الأولية.

        Args:
            initial_state: الحالة الأولية للعبة.

        Returns:
            قائمة من GameState تمثل مسار الحل، أو أفضل حالة إذا لم يتم العثور على حل.
        """
        pass

    def reconstruct_path(self, state: GameState) -> List[GameState]:
        """إعادة بناء مسار الحل من الحالة النهائية إلى الحالة الأولية."""
        path = []
        current = state
        while current is not None:
            path.append(current)
            current = current.parent
        return list(reversed(path))
    
    def _update_best_state(self, state: GameState):
        """تحديث أفضل حالة تم العثور عليها."""
        current_score = self._evaluate_state(state)
        if current_score < self.best_score:
            self.best_state_found = state
            self.best_score = current_score
    
    def _evaluate_state(self, state: GameState) -> float:
        """تقييم الحالة (كلما قل الرقم كان أفضل)."""
        if state.check_win_condition():
            return 0
        
        # عدد القطع المتبقية (أهم عامل)
        remaining_blocks = len(state.blocks) * 100
        
        # المسافة الإجمالية للقطع من المخارج
        total_distance = 0
        for block in state.blocks:
            min_distance = float('inf')
            for (x, y), exit_info in state.board.exits.items():
                if exit_info.get("color", "").lower() == block.color.lower():
                    block_center_x = block.x + sum(dx for dx, _ in block.shape) / len(block.shape)
                    block_center_y = block.y + sum(dy for _, dy in block.shape) / len(block.shape)
                    distance = abs(block_center_x - x) + abs(block_center_y - y)
                    min_distance = min(min_distance, distance)
            total_distance += min_distance
        
        # عدد القطع المحاصرة (سالب)
        trapped_blocks = len(state.get_trapped_block_indices()) * 50
        
        return remaining_blocks + total_distance * 0.5 - trapped_blocks