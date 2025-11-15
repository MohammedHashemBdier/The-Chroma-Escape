import pygame
import os
import sys
import copy
from controller import GameLogic, load_game_state, MOVE_SUCCESS, MOVE_INVALID, MOVE_EXIT
from view import GameVisualizer, CELL_SIZE
from sound_manager import SoundManager

LEVEL_FILES = [
    "levels/level_01.json",
    "levels/level_02.json",
    "levels/level_03.json",
    "levels/level_04.json"
]

def run_game(level_index=0):
    current_level = level_index % len(LEVEL_FILES)
    LEVEL_FILE = LEVEL_FILES[current_level]
    
    current_state = load_game_state(LEVEL_FILE)
    
    if current_state is None:
        print(f"Error: Failed to load game state from {LEVEL_FILE}.")
        return

    logic = GameLogic()
    sound_manager = SoundManager()
    sound_manager.load_sounds()
    
    if current_state.board.width <= 0 or current_state.board.height <= 0:
        print(f"Error: Invalid board dimensions.")
        return
        
    viz = GameVisualizer(current_state.board.width, current_state.board.height)

    running = True
    selected_block_index = None
    drag_start_cell = None
    move_count = 0
    message = ""
    control_mode = "mouse"
    initial_state = current_state
    auto_solving = False
    
    while running:
        if current_state.check_win_condition():
            print("Congratulations! You solved the puzzle!")
            sound_manager.play_win()
            viz.draw_win_screen(move_count)
            
            waiting_for_exit = True
            while waiting_for_exit:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        waiting_for_exit = False
                        running = False
                viz.clock.tick(10)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_u:
                    new_state, status = logic.undo_move(current_state)
                    if status == MOVE_SUCCESS:
                        current_state = new_state
                        move_count = max(0, move_count - 1)
                        message = "Move undone"
                        sound_manager.play_undo()
                    else:
                        message = "No moves to undo"
                elif event.key == pygame.K_r:
                    current_state = copy.deepcopy(initial_state)
                    move_count = 0
                    logic.move_history = []
                    message = "Level restarted"
                    sound_manager.play_restart()
                elif event.key == pygame.K_m:
                    control_mode = "mouse"
                    message = "Switched to mouse control"
                elif event.key == pygame.K_k:
                    control_mode = "keyboard"
                    message = "Switched to keyboard control"
                elif event.key == pygame.K_a:
                    if not auto_solving:
                        message = "Searching for solution..."
                        solution_path = logic.get_solution_path(current_state)
                        if solution_path:
                            message = f"Solution found with {len(solution_path)} steps"
                            auto_solving = True
                            logic.auto_solve(current_state, viz, delay=300)
                            current_state.check_win_condition()
                        else:
                            message = "No solution found"
                
                elif control_mode == "keyboard":
                    if event.key == pygame.K_TAB:
                        new_state = logic.select_next_block(current_state, not event.mod & pygame.KMOD_SHIFT)
                        if new_state.selected_block_index != current_state.selected_block_index:
                           sound_manager.play_select()
                        current_state = new_state
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        new_state, status = logic.try_move_keyboard(current_state, "UP")
                        if status == MOVE_SUCCESS:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_move()
                        elif status == MOVE_EXIT:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_exit()
                        else:
                            message = "Invalid move!"; sound_manager.play_invalid()
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        new_state, status = logic.try_move_keyboard(current_state, "DOWN")
                        if status == MOVE_SUCCESS:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_move()
                        elif status == MOVE_EXIT:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_exit()
                        else:
                            message = "Invalid move!"; sound_manager.play_invalid()
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        new_state, status = logic.try_move_keyboard(current_state, "LEFT")
                        if status == MOVE_SUCCESS:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_move()
                        elif status == MOVE_EXIT:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_exit()
                        else:
                            message = "Invalid move!"; sound_manager.play_invalid()
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        new_state, status = logic.try_move_keyboard(current_state, "RIGHT")
                        if status == MOVE_SUCCESS:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_move()
                        elif status == MOVE_EXIT:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_exit()
                        else:
                            message = "Invalid move!"; sound_manager.play_invalid()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN and control_mode == "mouse":
                mouse_x, mouse_y = event.pos
                cell_x = mouse_x // CELL_SIZE
                cell_y = mouse_y // CELL_SIZE
                
                for i, block in enumerate(current_state.blocks):
                    if (cell_x, cell_y) in block.get_absolute_coords():
                        selected_block_index = i
                        drag_start_cell = (cell_x, cell_y)
                        sound_manager.play_select()
                        break
                        
            elif event.type == pygame.MOUSEBUTTONUP and control_mode == "mouse":
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
                        distance = abs(total_dy)
                    
                    if distance > 0:
                        new_state, status = logic.try_move_manual(
                            current_state, 
                            selected_block_index, 
                            direction_vector, 
                            distance
                        )
                        
                        if status == MOVE_SUCCESS:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_move()
                        elif status == MOVE_EXIT:
                            current_state = new_state; move_count += 1; message = ""; sound_manager.play_exit()
                        else:
                            message = "Invalid move!"; sound_manager.play_invalid()

                selected_block_index = None
                drag_start_cell = None

        selected_coords = None
        if selected_block_index is not None:
             selected_coords = set(current_state.blocks[selected_block_index].get_absolute_coords())
        
        trapped_indices = current_state.get_trapped_block_indices()
             
        viz.draw(current_state, selected_block_coords=selected_coords, move_count=move_count, message=message, control_mode=control_mode, trapped_block_indices=trapped_indices)
        viz.clock.tick(60)
        
    pygame.quit()

def show_level_selection():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("The Chroma Escape - Level Selection")
    clock = pygame.time.Clock()
    
    try:
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.SysFont(None, 24)
    except pygame.error:
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
    
    running = True
    while running:
        screen.fill((240, 240, 240))
        
        title_text = font.render("Select Level", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(300, 50))
        screen.blit(title_text, title_rect)
        
        for i, level_file in enumerate(LEVEL_FILES):
            level_name = os.path.basename(level_file).replace(".json", "").replace("_", " ").title()
            level_text = small_font.render(f"{i+1}. {level_name}", True, (0, 0, 0))
            level_rect = level_text.get_rect(center=(300, 120 + i * 40))
            screen.blit(level_text, level_rect)
        
        max_level = len(LEVEL_FILES)
        instructions_text = f"Press 1-{max_level} to select a level, ESC to quit"
        instructions = small_font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions.get_rect(center=(300, 350))
        screen.blit(instructions, instructions_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif pygame.K_1 <= event.key <= pygame.K_1 + len(LEVEL_FILES) - 1:
                    level_index = event.key - pygame.K_1
                    pygame.quit()
                    run_game(level_index)
                    return
        
        clock.tick(30)
    
    pygame.quit()

if __name__ == '__main__':
    show_level_selection()