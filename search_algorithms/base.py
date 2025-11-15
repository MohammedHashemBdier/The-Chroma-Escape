from abc import ABC, abstractmethod
from typing import List, Optional
from model import GameState

class SearchAlgorithm(ABC):
    """
    الفئة الأساسية التي ستسترشد بها جميع خوارزميات البحث.
    هذا يضمن واجهة موحدة.
    """
    def __init__(self, name: str):
        self.name = name
        self.nodes_explored = 0

    @abstractmethod
    def solve(self, initial_state: GameState) -> Optional[List[GameState]]:
        """
        يجد حلاً للمشكلة انطلاقاً من الحالة الأولية.

        Args:
            initial_state: الحالة الأولية للعبة.

        Returns:
            قائمة من GameState تمثل مسار الحل، أو None إذا لم يتم العثور على حل.
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