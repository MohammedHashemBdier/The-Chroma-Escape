import pygame
from model import GameState, MovementType, Block, Board
import json
import copy
import traceback

MOVE_SUCCESS = "success"
MOVE_INVALID = "invalid"
MOVE_EXIT = "exit"

COLOR_ID_MAP = {
    1: "red", 2: "blue", 3: "green", 4: "yellow",
    5: "cyan", 6: "purple", 7: "orange"
}

class GameLogic:
    def __init__(self):
        self.move_history = []

    def print_possible_moves(self, current_state: GameState):
        print("\n" + "="*50)
        print("POSSIBLE MOVES FOR ALL BLOCKS:")
        print("="*50)

        all_moves = current_state.get_possible_moves()
        
        if not all_moves:
            print("No possible moves available.")
            print("="*50)
            return

        moves_by_block = {}
        for new_state, action in all_moves:
            block_id, dx, dy, distance = action
            if block_id not in moves_by_block:
                moves_by_block[block_id] = []
            moves_by_block[block_id].append((dx, dy, distance))

        blocks_by_id = {block.id: block for block in current_state.blocks}

        for block_id, moves in moves_by_block.items():
            if block_id in blocks_by_id:
                block = blocks_by_id[block_id]
                print(f"\nBlock ID: {block_id} | Color: {block.color.capitalize()} | Position: ({block.x}, {block.y}) | Lock: {block.move_lock}")
                print("-" * 30)
                if not moves:
                    print("  No valid moves for this block.")
                else:
                    for dx, dy, distance in moves:
                        if distance == 0 and dx == 0 and dy == 0:
                            print(f"  - EXIT: Block can exit immediately (no movement needed)")
                            continue
                            
                        direction_str = ""
                        if dx > 0:
                            direction_str = "RIGHT"
                        elif dx < 0:
                            direction_str = "LEFT"
                        elif dy > 0:
                            direction_str = "DOWN"
                        elif dy < 0:
                            direction_str = "UP"
                    
                        exit_str = " (EXIT)" if current_state.board.would_be_adjacent_to_exit_after_move(block, (dx, dy), distance) else ""
                    
                        print(f"  - Move: {direction_str} | Distance: {distance}{exit_str}")
        print("\n" + "="*50)

    def try_move_manual(self, current_state: GameState, block_id: int, direction_vector: tuple, distance: int) -> tuple:
        # التحقق الأساسي
        if distance not in [0, 1]:
            print(f"Error: Invalid distance {distance}. Must be 0 or 1.")
            return (current_state, MOVE_INVALID)
        
        # التحقق من صحة الحركة في الحالة الحالية
        if not current_state.is_move_valid(block_id, direction_vector, distance):
            print(f"Error: Move ({block_id}, {direction_vector}, {distance}) is not valid in current state")
            return (current_state, MOVE_INVALID)
        
        # البحث عن القطعة
        block_index = -1
        for i, block in enumerate(current_state.blocks):
            if block.id == block_id:
                block_index = i
                break
        
        if block_index == -1:
            return (current_state, MOVE_INVALID)

        block = current_state.blocks[block_index]
        dx, dy = direction_vector
        
        # حركة خروج مباشرة
        if distance == 0 and dx == 0 and dy == 0:
            action_tuple = (block_id, 0, 0, 0)
            new_state = self._create_new_state_after_exit(current_state, block_index, action_tuple)
            self.move_history.append((current_state, action_tuple))
            return (new_state, MOVE_EXIT)
        
        # حركة عادية
        action_tuple = (block_id, dx, dy, distance)

        # إذا كانت الحركة ستجعل القطعة مجاورة للمخرج
        if current_state.board.would_be_adjacent_to_exit_after_move(block, (dx, dy), distance):
            new_state = self._create_new_state_after_exit(current_state, block_index, action_tuple)
            self.move_history.append((current_state, action_tuple))
            return (new_state, MOVE_EXIT)

        # حركة عادية بدون خروج
        final_x = block.x + dx * distance
        final_y = block.y + dy * distance
        
        moved_block = Block(
            color=block.color, x=final_x, y=final_y, 
            shape=block.shape, movement_type=block.movement_type, id=block.id, move_lock=block.move_lock
        )
        
        new_state = self._create_new_state_after_move(current_state, block_index, moved_block, action_tuple)
        self.move_history.append((current_state, action_tuple))
        return (new_state, MOVE_SUCCESS)
    
    def try_move_keyboard(self, current_state: GameState, direction: str) -> tuple:
        move_info = current_state.get_keyboard_move(direction)
        if move_info is None:
            return (current_state, MOVE_INVALID)
        
        block_id, (dx, dy), distance = move_info
        return self.try_move_manual(current_state, block_id, (dx, dy), distance)
    
    def select_next_block(self, current_state: GameState, forward: bool = True) -> GameState:
        new_state = copy.deepcopy(current_state)
        new_state.select_next_block(forward)
        return new_state
    
    def select_block_at(self, current_state: GameState, x: int, y: int) -> GameState:
        block_index = current_state.get_block_at(x, y)
        if block_index is not None:
            new_state = copy.deepcopy(current_state)
            new_state.selected_block_index = block_index
            return new_state
        return current_state
    
    def undo_move(self, current_state: GameState) -> tuple:
        if not self.move_history:
            return (current_state, MOVE_INVALID)
        
        previous_state, _ = self.move_history.pop()
        return (previous_state, MOVE_SUCCESS)
    
    def _create_new_state_after_move(self, current_state: GameState, block_index: int, moved_block: Block, action: tuple) -> GameState:
        new_blocks = current_state.blocks[:]
        new_blocks[block_index] = moved_block
        
        new_state = GameState(board=current_state.board, blocks=new_blocks, parent=current_state, action=action)
        new_state.selected_block_index = current_state.selected_block_index
        new_state.move_count = current_state.move_count + 1
        new_state._inherit_display_locks(current_state)
        return new_state
    
    def _create_new_state_after_exit(self, current_state: GameState, block_index: int, action: tuple) -> GameState:
        new_blocks = copy.deepcopy(current_state.blocks)
        new_blocks.pop(block_index)
        
        new_state = GameState(board=current_state.board, blocks=new_blocks, parent=current_state, action=action)
        new_state.selected_block_index = None
        new_state.move_count = current_state.move_count + 1
        new_state._inherit_display_locks(current_state)
        new_state.decrease_all_move_locks()
        return new_state
    
    def get_possible_moves(self, current_state: GameState) -> list:
        return current_state.get_possible_moves()

def load_game_state(file_path: str) -> GameState:
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}")
        print(f"Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}")
        traceback.print_exc()
        return None
        
    exits_dict = {}
    for exit_data in data.get('exists', []):
        color_id = exit_data['color']
        color_name = COLOR_ID_MAP.get(color_id, "grey")
        for coord in exit_data['coordinates']:
            pos = (coord[1], coord[0])
            if pos not in exits_dict:
                exits_dict[pos] = {"color": color_name}

    barriers_set = set()
    for barrier in data.get('blocks', []):
        barriers_set.add((barrier[1], barrier[0]))
    
    board = Board(
        width=data['cols'],
        height=data['rows'],
        exits=exits_dict,
        barriers=barriers_set
    )
    
    blocks_list = []
    
    movement_map = {
        "HORIZONTAL": MovementType.HORIZONTAL,
        "VERTICAL": MovementType.VERTICAL,
        "ANY": MovementType.ANY
    }
    
    for i, shape_data in enumerate(data['shapes']):
        color_id = shape_data['colors']
        color_name = COLOR_ID_MAP.get(color_id, "grey")
        
        coords = shape_data['coordinates']
        if not coords:
            print(f"Warning: Shape {i} has no coordinates. Skipping.")
            continue
        base_y, base_x = coords[0]
        shape = [(coord[1] - base_x, coord[0] - base_y) for coord in coords]
        
        move_type_str = shape_data.get('direction', 'any').upper()
        move_type = movement_map.get(move_type_str, MovementType.ANY)
            
        move_lock = shape_data.get('move_lock', 0)
            
        block = Block(
            color=color_name,
            x=base_x,
            y=base_y,
            shape=shape, 
            movement_type=move_type,
            id=i,
            move_lock=move_lock
        )
        blocks_list.append(block)

    start_state = GameState(board=board, blocks=blocks_list)
    start_state._initialize_display_locks()
    
    return start_state