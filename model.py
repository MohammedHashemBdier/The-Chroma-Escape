from enum import Enum
from typing import Union, List, Tuple, Set
import copy

class MovementType(Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    ANY = 3

class Block:
    def __init__(self, color: str, x: int, y: int, shape: List[Tuple[int, int]], movement_type: MovementType):
        self.color = color
        self.x = x
        self.y = y
        self.shape = shape
        self.movement_type = movement_type

    def get_absolute_coords(self) -> List[Tuple[int, int]]:
        absolute_coords = []
        for dx, dy in self.shape:
            absolute_coords.append((self.x + dx, self.y + dy))
        return absolute_coords

    def can_move(self, direction: Tuple[int, int]) -> bool:
        """تحقق مما إذا كان يمكن للقطعة التحرك في الاتجاه المحدد"""
        dx, dy = direction
        if dx != 0 and self.movement_type == MovementType.VERTICAL:
            return False
        if dy != 0 and self.movement_type == MovementType.HORIZONTAL:
            return False
        return True

    def move(self, direction: Tuple[int, int], distance: int = 1):
        """إنشاء نسخة جديدة من القطعة بعد التحرك"""
        if not self.can_move(direction):
            return self
        
        dx, dy = direction
        new_block = copy.deepcopy(self)
        new_block.x += dx * distance
        new_block.y += dy * distance
        return new_block

    def __repr__(self):
        return f"Block(Color: {self.color}, Pos: ({self.x}, {self.y}), Type: {self.movement_type.name})"
    
class Board:
    def __init__(self, width: int, height: int, exits: dict, barriers: set):
        self.width = width
        self.height = height
        self.exits = exits
        self.barriers = barriers

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.barriers

    def get_exit_color(self, x: int, y: int) -> Union[str, None]:
        exit_info = self.exits.get((x, y))
        if exit_info:
            return exit_info.get("color") # نرجع اللون فقط كما قبل
        return None

class GameState:
    def __init__(self, board: Board, blocks: List[Block], parent=None, action=None, depth=0):
        self.board = board
        self.blocks = blocks 
        self.parent = parent  # للبحث والتراجع
        self.action = action  # الحركة التي أدت إلى هذه الحالة
        self.depth = depth  # عمق الحالة في شجرة البحث

    def check_win_condition(self) -> bool:
        return len(self.blocks) == 0

    def get_occupied_coords(self) -> Set[Tuple[int, int]]:
        occupied = set()
        for block in self.blocks:
            occupied.update(block.get_absolute_coords())
        return occupied
    
    def get_possible_moves(self) -> List[Tuple['GameState', Tuple[int, int, int]]]:
        """إرجاع قائمة بالحركات الممكنة والحالات الناتجة"""
        possible_moves = []
        max_dist = max(self.board.width, self.board.height)
        
        for block_index, block in enumerate(self.blocks):
            # تحديد الاتجاهات المسموح بها بناءً على نوع الحركة
            directions = []
            if block.movement_type in [MovementType.HORIZONTAL, MovementType.ANY]:
                directions.extend([(1, 0), (-1, 0)])
            if block.movement_type in [MovementType.VERTICAL, MovementType.ANY]:
                directions.extend([(0, 1), (0, -1)])
            
            for dx, dy in directions:
                for distance in range(1, max_dist):
                    new_block = block.move((dx, dy), distance)
                    new_coords = set(new_block.get_absolute_coords())
                    
                    # التحقق من أن المسار خالٍ
                    if not self._is_path_clear(block, (dx, dy), distance):
                        break
                    
                    # التحقق من الخروج من اللوحة
                    if self._is_exit_move_valid(new_coords, block):
                        new_blocks = self.blocks[:block_index] + self.blocks[block_index+1:]
                        new_state = GameState(self.board, new_blocks, self, (block_index, dx, dy), self.depth + 1)
                        possible_moves.append((new_state, (block_index, dx, dy)))
                        break
                    
                    # التحقق من التصادم
                    if self._is_collision(new_coords, block_index):
                        break
                    
                    # إنشاء حالة جديدة
                    new_blocks = self.blocks[:]
                    new_blocks[block_index] = new_block
                    new_state = GameState(self.board, new_blocks, self, (block_index, dx, dy), self.depth + 1)
                    possible_moves.append((new_state, (block_index, dx, dy)))
        
        return possible_moves
    
    def _is_path_clear(self, block: Block, direction: Tuple[int, int], distance: int) -> bool:
        """التحقق من أن المسار خالٍ من العوائق"""
        dx, dy = direction
        occupied = self.get_occupied_coords()
        
        for step in range(1, distance + 1):
            for shape_dx, shape_dy in block.shape:
                x = block.x + dx * step + shape_dx
                y = block.y + dy * step + shape_dy
                
                # التحقق من الخروج من اللوحة
                if not (0 <= x < self.board.width and 0 <= y < self.board.height):
                    exit_color = self.board.get_exit_color(x, y)
                    if exit_color is None or exit_color.lower() != block.color.lower():
                        return False
                
                # التحقق من التصادم مع العوائق
                if (x, y) in occupied:
                    return False
        
        return True
    
    def _is_exit_move_valid(self, new_coords: Set[Tuple[int, int]], block: Block) -> bool:
        """التحقق من أن الحركة تؤدي إلى خروج صحيح"""
        for x, y in new_coords:
            exit_color = self.board.get_exit_color(x, y)
            if exit_color is not None and exit_color.lower() == block.color.lower():
                return True
        return False
    
    def _is_collision(self, new_coords: Set[Tuple[int, int]], block_index: int) -> bool:
        """التحقق من وجود تصادم"""
        occupied = self.get_occupied_coords()
        for i, block in enumerate(self.blocks):
            if i != block_index:
                occupied.update(block.get_absolute_coords())
        
        return not new_coords.isdisjoint(occupied)
    
    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.get_hashable_key() == other.get_hashable_key()

    def __hash__(self):
        return hash(self.get_hashable_key())

    def get_hashable_key(self) -> tuple:
        positions_list = [(block.y, block.x, block.color) for block in self.blocks]
        return tuple(sorted(positions_list))
    
    def get_solution_path(self) -> List['GameState']:
        """إرجاع المسار من الحالة الحالية إلى الحالة الأولية"""
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.parent
        return list(reversed(path))