from model import GameState, MovementType


class GameLogic:
    
    def get_possible_moves(self, current_state: GameState) -> list:
        possible_next_states = []
        
        for block_index, block in enumerate(current_state.blocks):
                        
            for direction in self._get_allowed_directions(block.movement_type):

                pass 
                
        return possible_next_states
        
    def _get_allowed_directions(self, movement_type: MovementType) -> list:
        pass