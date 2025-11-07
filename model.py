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

    def get_absolute_coords(self) -> list:
        absolute_coords = []
        for dx, dy in self.shape:
            absolute_coords.append((self.x + dx, self.y + dy))
        return absolute_coords

    def __repr__(self):
        return f"Block(Color: {self.color}, Pos: ({self.x}, {self.y}), Type: {self.movement_type.name})"