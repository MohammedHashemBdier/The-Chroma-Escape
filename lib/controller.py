from model import GameState, MovementType, Block, Board
import json

class GameLogic:
    
    def _get_allowed_directions(self, movement_type: MovementType) -> list:
        directions = []
        if movement_type in [MovementType.HORIZONTAL, MovementType.ANY]:
            directions.extend([(1, 0), (-1, 0)])
        
        if movement_type in [MovementType.VERTICAL, MovementType.ANY]:
            directions.extend([(0, 1), (0, -1)])
            
        return directions

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
            
            temp_block = Block(block.color, check_x, check_y, moving_block_shape, block.movement_type)
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
        
    def try_move_manual(self, current_state: GameState, block_index: int, direction_vector: tuple, distance: int) -> GameState:
        if distance <= 0:
            return current_state

        block = current_state.blocks[block_index]
        dx, dy = direction_vector
        board = current_state.board

        if (dx != 0 and block.movement_type == MovementType.VERTICAL) or \
           (dy != 0 and block.movement_type == MovementType.HORIZONTAL):
            return current_state

        if not self._is_path_clear(current_state, block_index, dx, dy, distance):
             return current_state 

        final_x = block.x + dx * distance
        final_y = block.y + dy * distance
        
        moved_block = Block(
            color=block.color, 
            x=final_x, 
            y=final_y, 
            shape=block.shape, 
            movement_type=block.movement_type
        )
        final_coords = set(moved_block.get_absolute_coords())

        if self._is_exit_move_valid(final_coords, block, board):
            return self._create_new_state_after_exit(current_state, block_index)

        for x, y in final_coords:
            if not (0 <= x < board.width and 0 <= y < board.height):
                return current_state 

        return self._create_new_state_after_move(current_state, block_index, moved_block)
    
    def get_possible_moves(self, current_state: GameState) -> list:
        possible_next_states = []
        board = current_state.board
        max_dist = max(board.width, board.height) 

        for block_index, block in enumerate(current_state.blocks):
            
            for dx, dy in self._get_allowed_directions(block.movement_type):
                
                for distance in range(1, max_dist):
                    
                    final_x = block.x + dx * distance
                    final_y = block.y + dy * distance
                    
                    moved_block = Block(
                        color=block.color, 
                        x=final_x, 
                        y=final_y, 
                        shape=block.shape, 
                        movement_type=block.movement_type
                    )
                    final_coords = set(moved_block.get_absolute_coords())
                    
                    if not self._is_path_clear(current_state, block_index, dx, dy, distance):
                        break
                    
                    if self._is_exit_move_valid(final_coords, block, board):
                        new_state = self._create_new_state_after_exit(current_state, block_index)
                        possible_next_states.append(new_state)
                        break
                    
                    if not self._is_collision(final_coords, current_state, block_index):
                        new_state = self._create_new_state_after_move(current_state, block_index, moved_block)
                        
                        is_out_of_bounds = False
                        for x_coord, y_coord in final_coords:
                            if not (0 <= x_coord < board.width and 0 <= y_coord < board.height):
                                is_out_of_bounds = True
                                break
                        
                        if not is_out_of_bounds:
                            possible_next_states.append(new_state)
                    else:
                        break

        return possible_next_states

    def _is_exit_move_valid(self, new_coords: set, block: Block, board: Board) -> bool:
        
        for x, y in new_coords:
            exit_color = board.get_exit_color(x, y)
            
            if exit_color is not None and exit_color.lower() == block.color.lower():
                return True
            
        return False

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

    def _create_new_state_after_move(self, current_state: GameState, block_index: int, moved_block: Block) -> GameState:
        new_blocks = current_state.blocks[:]
        
        new_blocks[block_index] = moved_block
        
        return GameState(board=current_state.board, blocks=new_blocks)
    
    def _create_new_state_after_exit(self, current_state: GameState, block_index: int) -> GameState:
        new_blocks = current_state.blocks[:]
        
        new_blocks.pop(block_index)
        
        return GameState(board=current_state.board, blocks=new_blocks)
    

def load_game_state(file_path: str) -> GameState:

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
        return None
        
    exits_dict = {
        (exit_data['x'], exit_data['y']): exit_data['color']
        for exit_data in data.get('exits', [])
    }

    barriers_set = {
        (barrier_data['x'], barrier_data['y'])
        for barrier_data in data.get('barriers', [])
    }
    
    board = Board(
        width=data['board_width'],
        height=data['board_height'],
        exits=exits_dict,
        barriers=barriers_set
    )
    
    blocks_list = []
    
    movement_map = {
        "HORIZONTAL": MovementType.HORIZONTAL,
        "VERTICAL": MovementType.VERTICAL,
        "ANY": MovementType.ANY
    }
    
    for block_data in data['blocks']:
        move_type = movement_map.get(block_data.get('movement_type').upper())
        if not move_type:
            raise ValueError(f"Invalid movement type: {block_data.get('movement_type')}")
            
        block = Block(
            color=block_data['color'].lower(),
            x=block_data['x'],
            y=block_data['y'],
            shape=[tuple(s) for s in block_data['shape']], 
            movement_type=move_type
        )
        blocks_list.append(block)

    start_state = GameState(board=board, blocks=blocks_list)
    
    return start_state