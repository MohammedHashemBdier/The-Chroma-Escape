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

    def try_move_manual(self, current_state: GameState, block_id: int, direction_vector: tuple, distance: int) -> tuple:
        if distance <= 0:
            return (current_state, MOVE_INVALID)

        block_index = -1
        for i, block in enumerate(current_state.blocks):
            if block.id == block_id:
                block_index = i
                break
        
        if block_index == -1:
            return (current_state, MOVE_INVALID)

        block = current_state.blocks[block_index]
        if block.move_lock == 0:
            return (current_state, MOVE_INVALID)

        dx, dy = direction_vector
        board = current_state.board

        if (dx != 0 and block.movement_type == MovementType.VERTICAL) or \
           (dy != 0 and block.movement_type == MovementType.HORIZONTAL):
            return (current_state, MOVE_INVALID)

        if not self._is_path_clear(current_state, block_index, dx, dy, distance):
            return (current_state, MOVE_INVALID)

        final_x = block.x + dx * distance
        final_y = block.y + dy * distance
        
        moved_block = Block(
            color=block.color, x=final_x, y=final_y, 
            shape=block.shape, movement_type=block.movement_type, id=block.id, move_lock=block.move_lock
        )
        final_coords = set(moved_block.get_absolute_coords())

        if self._is_exit_move_valid(final_coords, block, board):
            new_state = self._create_new_state_after_exit(current_state, block_index)
            new_state.update_move_locks_for_color(block.color)
            self.move_history.append((current_state, (block_id, dx, dy, distance)))
            return (new_state, MOVE_EXIT)

        for x, y in final_coords:
            if not (0 <= x < board.width and 0 <= y < board.height):
                return (current_state, MOVE_INVALID)

        new_state = self._create_new_state_after_move(current_state, block_index, moved_block)
        self.move_history.append((current_state, (block_id, dx, dy, distance)))
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
    
    def _is_path_clear(self, current_state: GameState, moving_block_index: int, dx: int, dy: int, distance: int) -> bool:
        block = current_state.blocks[moving_block_index]
        board = current_state.board
        moving_block_shape = block.shape
        
        obstacle_coords = board.barriers.copy()
        for i, other_block in enumerate(current_state.blocks):
            if i != moving_block_index:
                obstacle_coords.update(other_block.get_absolute_coords())
        
        for step in range(1, distance + 1):
            check_x = block.x + dx * step
            check_y = block.y + dy * step
            
            temp_block = Block(block.color, check_x, check_y, moving_block_shape, block.movement_type, block.id, block.move_lock)
            temp_coords = set(temp_block.get_absolute_coords())

            if temp_coords.intersection(obstacle_coords):
                return False
                
            for x, y in temp_coords:
                is_out_of_bounds = not (0 <= x < board.width and 0 <= y < board.height)
                exit_color = board.get_exit_color(x, y)
                
                if is_out_of_bounds:
                    if exit_color is None or exit_color.lower() != block.color.lower():
                        return False 
                
        return True
        
    def _is_exit_move_valid(self, new_coords: set, block: Block, board: Board) -> bool:
        for x, y in new_coords:
            exit_color = board.get_exit_color(x, y)
            if exit_color is not None and exit_color.lower() == block.color.lower():
                return True
        return False

    def _create_new_state_after_move(self, current_state: GameState, block_index: int, moved_block: Block) -> GameState:
        new_blocks = current_state.blocks[:]
        new_blocks[block_index] = moved_block
        
        new_state = GameState(board=current_state.board, blocks=new_blocks, parent=current_state)
        new_state.selected_block_index = current_state.selected_block_index
        new_state.move_count = current_state.move_count + 1
        return new_state
    
    def _create_new_state_after_exit(self, current_state: GameState, block_index: int) -> GameState:
        new_blocks = current_state.blocks[:]
        new_blocks.pop(block_index)
        
        new_state = GameState(board=current_state.board, blocks=new_blocks, parent=current_state)
        new_state.selected_block_index = None
        new_state.move_count = current_state.move_count + 1
        return new_state
    
    def get_possible_moves(self, current_state: GameState) -> list:
        possible_next_states = []
        board = current_state.board
        max_dist = max(board.width, board.height) 

        for block_index, block in enumerate(current_state.blocks):
            if block.move_lock == 0:
                continue

            directions = []
            if block.movement_type in [MovementType.HORIZONTAL, MovementType.ANY]:
                directions.extend([(1, 0), (-1, 0)])
            if block.movement_type in [MovementType.VERTICAL, MovementType.ANY]:
                directions.extend([(0, 1), (0, -1)])
                
            for dx, dy in directions:
                for distance in range(1, max_dist):
                    if not self._is_path_clear(current_state, block_index, dx, dy, distance):
                        break
                    
                    final_x = block.x + dx * distance
                    final_y = block.y + dy * distance
                    
                    moved_block = Block(
                        color=block.color, x=final_x, y=final_y, 
                        shape=block.shape, movement_type=block.movement_type, id=block.id, move_lock=block.move_lock
                    )
                    final_coords = set(moved_block.get_absolute_coords())
                    
                    if self._is_exit_move_valid(final_coords, block, board):
                        new_state = self._create_new_state_after_exit(current_state, block_index)
                        new_state.update_move_locks_for_color(block.color)
                        possible_next_states.append((new_state, (block.id, dx, dy, distance)))
                        break
                    
                    if not self._is_collision(final_coords, current_state, block_index):
                        new_state = self._create_new_state_after_move(current_state, block_index, moved_block)
                        
                        is_out_of_bounds = False
                        for x_coord, y_coord in final_coords:
                            if not (0 <= x_coord < board.width and 0 <= y_coord < board.height):
                                is_out_of_bounds = True
                                break
                        
                        if not is_out_of_bounds:
                            possible_next_states.append((new_state, (block.id, dx, dy, distance)))
                    else:
                        break

        return possible_next_states
    
    def _is_collision(self, new_coords: set, current_state: GameState, moving_block_index: int) -> bool:
        board = current_state.board
        
        obstacle_coords = board.barriers.copy()
        
        for i, block in enumerate(current_state.blocks):
            if i != moving_block_index:
                obstacle_coords.update(block.get_absolute_coords())
        
        if new_coords.intersection(obstacle_coords):
            return True 
            
        for x, y in new_coords:
            if not (0 <= x < board.width and 0 <= y < board.height):
                exit_color = board.get_exit_color(x, y)
                if exit_color is None or exit_color.lower() != current_state.blocks[moving_block_index].color.lower():
                    return True 
                
        return False

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
            # تبديل الإحداثيات من (y, x) إلى (x, y)
            pos = (coord[1], coord[0])
            if pos not in exits_dict:
                exits_dict[pos] = {"color": color_name}

    barriers_set = set()
    for barrier in data.get('blocks', []):
        # تبديل الإحداثيات من (y, x) إلى (x, y)
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
        
        # تبديل الإحداثيات من (y, x) إلى (x, y) وحساب الشكل النسبي
        base_y, base_x = coords[0]
        shape = [(coord[1] - base_x, coord[0] - base_y) for coord in coords]
        
        move_type_str = shape_data.get('direction', 'any').upper()
        move_type = movement_map.get(move_type_str, MovementType.ANY)
            
        move_lock = shape_data.get('move_lock', -1)
            
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
    
    return start_state