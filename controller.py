from model import GameState, MovementType, Block, Board

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