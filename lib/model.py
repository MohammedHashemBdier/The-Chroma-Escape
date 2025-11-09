from enum import Enum
from typing import Union

class MovementType(Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    ANY = 3

class Block:
    def __init__(self, color: str, x: int, y: int, shape: list, movement_type: MovementType):
        self.color = color
        self.x = x
        self.y = y
        self.shape = shape
        self.movement_type = movement_type

    def get_absolute_coords(self) -> list:
        absolute_coords = []
        for dx, dy in self.shape:
            absolute_coords.append((self.x + dx, self.y + dy))
        return absolute_coords

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
        return self.exits.get((x, y))

class GameState:
    def __init__(self, board: Board, blocks: list):
        self.board = board
        self.blocks = blocks 

    def check_win_condition(self) -> bool:
        return len(self.blocks) == 0

    def get_occupied_coords(self) -> set:
        occupied = set()
        for block in self.blocks:
            occupied.update(block.get_absolute_coords())
        return occupied
    
    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False

        return self.get_hashable_key() == other.get_hashable_key()

    def __hash__(self):
        return hash(self.get_hashable_key())

    def get_hashable_key(self) -> tuple:
        positions_list = [(block.y, block.x, block.color) for block in self.blocks]
        
        return tuple(sorted(positions_list))