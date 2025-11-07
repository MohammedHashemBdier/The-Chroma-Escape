from model import GameState, MovementType, Block, Board
import json
class GameLogic:
    
    def get_possible_moves(self, current_state: GameState) -> list:
        possible_next_states = []
        
        for block_index, block in enumerate(current_state.blocks):
                        
            for direction in self._get_allowed_directions(block.movement_type):

                pass 
                
        return possible_next_states
        
    def _get_allowed_directions(self, movement_type: MovementType) -> list:
        pass
    def _get_allowed_directions(self, movement_type: MovementType) -> list:
        directions = []
        if movement_type in [MovementType.HORIZONTAL, MovementType.ANY]:
            directions.extend([(1, 0), (-1, 0)])
        
        if movement_type in [MovementType.VERTICAL, MovementType.ANY]:
            directions.extend([(0, 1), (0, -1)])
            
        return directions
    
    def get_possible_moves(self, current_state: GameState) -> list:
        possible_next_states = []
        board = current_state.board
        max_dist = max(board.width, board.height)

        for block_index, block in enumerate(current_state.blocks):
            
            for dx, dy in self._get_allowed_directions(block.movement_type):
                
                for distance in range(1, max_dist):
                    
                    new_x = block.x + dx * distance
                    new_y = block.y + dy * distance
                    
                    moved_block = Block(
                        color=block.color, 
                        x=new_x, 
                        y=new_y, 
                        shape=block.shape, 
                        movement_type=block.movement_type
                    )

                    new_coords = set(moved_block.get_absolute_coords())

                    if self._is_exit_move_valid(new_coords, block, board):
                        new_state = self._create_new_state_after_exit(current_state, block_index)
                        possible_next_states.append(new_state)
                        
                        break 
                    
                    if self._is_collision(new_coords, current_state, block_index):
                        break
                    
                    new_state = self._create_new_state_after_move(current_state, block_index, moved_block)
                    possible_next_states.append(new_state)
                    

        return possible_next_states

    def _is_exit_move_valid(self, new_coords: set, block: Block, board: Board) -> bool:
        
        in_bounds_coords = set()
        out_of_bounds_coords = set()
        
        for x, y in new_coords:
            if 0 <= x < board.width and 0 <= y < board.height:
                in_bounds_coords.add((x, y))
            else:
                out_of_bounds_coords.add((x, y))

        if not out_of_bounds_coords:
            return False 

        if in_bounds_coords:
            return False

        for x_out, y_out in out_of_bounds_coords:
            exit_color = board.get_exit_color(x_out, y_out)
            
            if exit_color is None:
                return False
                
            if exit_color != block.color:
                return False
                
        return True

    def _is_collision(self, new_coords: set, current_state: GameState, moving_block_index: int) -> bool:
        board = current_state.board
        
        obstacle_coords = board.barriers.copy()
        
        for i, block in enumerate(current_state.blocks):
            if i != moving_block_index:
                obstacle_coords.update(block.get_absolute_coords())
        
        if new_coords & obstacle_coords:
            return True 
            
        for x, y in new_coords:
            if not (0 <= x < board.width and 0 <= y < board.height):
                if board.get_exit_color(x, y) is None:
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
            move_type = movement_map.get(block_data.get('movement_type'))
            if not move_type:
                raise ValueError(f"Invalid movement type: {block_data.get('movement_type')}")
                
            block = Block(
                color=block_data['color'],
                x=block_data['x'],
                y=block_data['y'],
                shape=[tuple(s) for s in block_data['shape']], 
                movement_type=move_type
            )
            blocks_list.append(block)

        start_state = GameState(board=board, blocks=blocks_list)
        
        return start_state
