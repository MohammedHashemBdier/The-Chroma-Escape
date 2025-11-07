import pygame
from controller import GameLogic, load_game_state
from view import GameVisualizer, CELL_SIZE

LEVEL_FILE = "levels/level_01.json" 


def run_game():
    
    current_state = load_game_state(LEVEL_FILE)
    
    if current_state is None:
        print("Error: Failed to load game state from JSON. Check file path or content.")
        return

    logic = GameLogic()
    
    if current_state.board.width <= 0 or current_state.board.height <= 0:
        print(f"Error: Invalid board dimensions ({current_state.board.width}x{current_state.board.height}).")
        return
        
    viz = GameVisualizer(current_state.board.width, current_state.board.height)

    running = True
    selected_block_index = None
    drag_start_cell = None
    
    
    while running:
        
        if current_state.check_win_condition():
            print("Congratulations! You solved the puzzle!")
            viz.draw(current_state)
            viz.wait_for_quit()
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                cell_x = mouse_x // CELL_SIZE
                cell_y = mouse_y // CELL_SIZE
                
                for i, block in enumerate(current_state.blocks):
                    if (cell_x, cell_y) in block.get_absolute_coords():
                        selected_block_index = i
                        drag_start_cell = (cell_x, cell_y)
                        break
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_block_index is not None and drag_start_cell is not None:
                    
                    mouse_x, mouse_y = event.pos
                    cell_x_end = mouse_x // CELL_SIZE
                    cell_y_end = mouse_y // CELL_SIZE
                    
                    total_dx = cell_x_end - drag_start_cell[0]
                    total_dy = cell_y_end - drag_start_cell[1]

                    direction_vector = (0, 0)
                    distance = 0
                    
                    if abs(total_dx) > abs(total_dy):
                        direction_vector = (1 if total_dx > 0 else -1, 0)
                        distance = abs(total_dx)
                    elif abs(total_dy) > 0:
                        direction_vector = (0, 1 if total_dy > 0 else -1)
                        distance = abs(abs(total_dy))
                    
                    if distance > 0:
                        current_state = logic.try_move_manual(
                            current_state, 
                            selected_block_index, 
                            direction_vector, 
                            distance
                        )

                selected_block_index = None
                drag_start_cell = None

        selected_coords = None
        if selected_block_index is not None:
             selected_coords = set(current_state.blocks[selected_block_index].get_absolute_coords())
             
        viz.draw(current_state, selected_block_coords=selected_coords)
        viz.clock.tick(60)
        
    pygame.quit()


if __name__ == '__main__':
    run_game()