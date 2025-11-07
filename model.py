from enum import Enum
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