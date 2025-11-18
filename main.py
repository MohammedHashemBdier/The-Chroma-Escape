import pygame
import os
import sys
import copy
import traceback
from controller import GameLogic, load_game_state, MOVE_SUCCESS, MOVE_INVALID, MOVE_EXIT
from view import GameVisualizer
from sound_manager import SoundManager
from search_algorithms import AStarSolver

LEVEL_FILES = [
    "levels/level_01.json",
]

def show_error_screen(screen, font, error_message):
    screen.fill((50, 0, 0))
    title_text = font.render("FATAL ERROR", True, (255, 0, 0))
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
    screen.blit(title_text, title_rect)

    lines = error_message.split('\n')
    y_offset = 120
    for line in lines:
        error_text = font.render(line, True, (255, 255, 255))
        error_rect = error_text.get_rect(center=(screen.get_width() // 2, y_offset))
        screen.blit(error_text, error_rect)
        y_offset += 30

    exit_text = font.render("Press ESC to quit", True, (200, 200, 200))
    exit_rect = exit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
    screen.blit(exit_text, exit_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                waiting = False

def run_game(level_index=0):
    try:
        current_level = level_index % len(LEVEL_FILES)
        LEVEL_FILE = LEVEL_FILES[current_level]
        
        initial_state = load_game_state(LEVEL_FILE)
        
        if initial_state is None:
            raise Exception(f"Failed to load game state from {LEVEL_FILE}. Check the file path and format.")

        logic = GameLogic()
        sound_manager = SoundManager()
        sound_manager.load_sounds()
        
        if initial_state.board.width <= 0 or initial_state.board.height <= 0:
            raise Exception(f"Invalid board dimensions: {initial_state.board.width}x{initial_state.board.height}")
            
        viz = GameVisualizer(initial_state.board)

        running = True
        current_state = copy.deepcopy(initial_state)
        move_count = 0
        message = ""
        control_mode = "mouse"
        selected_block_index = None
        selected_block_id = None
        drag_start_cell = None
        
        is_ai_playing = False
        ai_solution_path = []
        ai_move_delay = 500
        last_ai_move_time = 0
        
        ai_solver = AStarSolver()

        clock = pygame.time.Clock()
        
        while running:
            current_time = pygame.time.get_ticks()

            if is_ai_playing and ai_solution_path:
                if current_time - last_ai_move_time > ai_move_delay:
                    action = ai_solution_path.pop(0)
                    block_id, dx, dy, distance = action
                    
                    new_state, status = logic.try_move_manual(current_state, block_id, (dx, dy), distance)
                    
                    if status in [MOVE_SUCCESS, MOVE_EXIT]:
                        current_state = new_state
                        move_count += 1
                        if status == MOVE_SUCCESS:
                            sound_manager.play_move()
                        else:
                            sound_manager.play_exit()
                    
                    last_ai_move_time = current_time

                    if not ai_solution_path:
                        is_ai_playing = False
                        message = "AI finished solving!"
                        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if is_ai_playing:
                        is_ai_playing = False
                        ai_solution_path = []
                        message = "AI play stopped."
                        pygame.time.set_timer(pygame.USEREVENT + 1, 2000)
                        continue

                    if event.key == pygame.K_u:
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
                    
                    elif event.key == pygame.K_s:
                        message = "AI is solving..."
                        viz.draw(current_state, move_count=move_count, message=message)
                        pygame.display.flip()

                        solution_path = ai_solver.solve(current_state)
                        
                        if solution_path:
                            ai_solution_path = []
                            temp_state = solution_path[0]
                            for i in range(1, len(solution_path)):
                                found_action = None
                                for next_state, action in temp_state.get_possible_moves():
                                    if next_state.get_hashable_key() == solution_path[i].get_hashable_key():
                                        found_action = action
                                        break
                                if found_action:
                                    ai_solution_path.append(found_action)
                                    temp_state = solution_path[i]

                            if ai_solution_path:
                                is_ai_playing = True
                                last_ai_move_time = 0
                                message = "AI is now playing..."
                                print(f"Solution found in {len(solution_path)-1} moves! ({ai_solver.nodes_explored} nodes explored)")
                            else:
                                 message = "Could not reconstruct solution path."
                        else:
                            message = "No solution found!"
                        
                        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)

                    elif event.type == pygame.USEREVENT + 1:
                        message = ""
                        pygame.time.set_timer(pygame.USEREVENT + 1, 0)

                    elif control_mode == "keyboard" and not is_ai_playing:
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
                        
                elif event.type == pygame.MOUSEBUTTONDOWN and control_mode == "mouse" and not is_ai_playing:
                    mouse_x, mouse_y = event.pos
                    cell_x = mouse_x // viz.CELL_SIZE
                    cell_y = mouse_y // viz.CELL_SIZE
                    
                    selected_block_index = None
                    selected_block_id = None
                    for i, block in enumerate(current_state.blocks):
                        if (cell_x, cell_y) in block.get_absolute_coords():
                            selected_block_index = i
                            selected_block_id = block.id
                            drag_start_cell = (cell_x, cell_y)
                            sound_manager.play_select()
                            break
                            
                elif event.type == pygame.MOUSEBUTTONUP and control_mode == "mouse" and not is_ai_playing:
                    if selected_block_index is not None and drag_start_cell is not None:
                        mouse_x, mouse_y = event.pos
                        cell_x_end = mouse_x // viz.CELL_SIZE
                        cell_y_end = mouse_y // viz.CELL_SIZE
                        
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
                                selected_block_id, 
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
                    selected_block_id = None
                    drag_start_cell = None

            if current_state.check_win_condition():
                print("Congratulations! Puzzle solved!")
                sound_manager.play_win()
                viz.draw_win_screen(move_count)
                is_ai_playing = False
                
                waiting_for_exit = True
                while waiting_for_exit:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            waiting_for_exit = False
                            running = False
                    clock.tick(10)
                break

            selected_coords = None
            if selected_block_index is not None:
                 selected_coords = set(current_state.blocks[selected_block_index].get_absolute_coords())
            
            trapped_indices = current_state.get_trapped_block_indices()
                 
            viz.draw(current_state, selected_block_coords=selected_coords, move_count=move_count, message=message, control_mode=control_mode, trapped_block_indices=trapped_indices)
            clock.tick(60)
            
        pygame.quit()

    except Exception as e:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Error")
        font = pygame.font.SysFont("consolas", 18)
        show_error_screen(screen, font, traceback.format_exc())
        pygame.quit()


def show_level_selection():
    try:
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

    except Exception as e:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Error")
        font = pygame.font.SysFont("consolas", 18)
        show_error_screen(screen, font, traceback.format_exc())
        pygame.quit()


if __name__ == '__main__':
    show_level_selection()