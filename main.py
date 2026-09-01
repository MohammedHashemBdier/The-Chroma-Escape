import pygame
import os
import copy
import traceback
import time
from controller import GameLogic, load_game_state, MOVE_SUCCESS, MOVE_INVALID, MOVE_EXIT
from model import GameState
from search_algorithms.astar import AStarSolver
from search_algorithms.bfs import BFSSolver
from search_algorithms.dfs import DFSSolver
from search_algorithms.dfs_recursive import DFSRecursiveSolver
from search_algorithms.hillclimbing import HillClimbingSolver
from search_algorithms.ucs import UCSSolver
from search_algorithms.greedy import GreedySolver
from view import GameVisualizer
from sound_manager import SoundManager

LEVEL_FILES = [
    "levels/level_01.json",
    "levels/level_02.json",
    "levels/level_03.json",
    "levels/level_04.json",
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

def extract_moves_from_solution_path(solution_path, current_state):
    """استخراج الحركات الصالحة من مسار الحل، بدءاً من الحالة الحالية."""
    if len(solution_path) <= 1:
        return []
    
    # البحث عن الحالة الحالية في مسار الحل
    current_state_key = current_state.get_hashable_key()
    start_index = -1
    
    # البحث عن أقرب حالة مطابقة
    for i, state in enumerate(solution_path):
        # أولاً: تحقق إذا كانت الحالة مطابقة تماماً
        if state.get_hashable_key() == current_state_key:
            start_index = i
            break
    
    # إذا لم نجد مطابقة تامة، نبحث عن حالة متشابهة (نفس القطع في نفس المواقع)
    if start_index == -1:
        for i, state in enumerate(solution_path):
            if len(state.blocks) == len(current_state.blocks):
                # تحقق إذا كانت جميع القطع في نفس المواقع
                match = True
                blocks_matched = 0
                for state_block in state.blocks:
                    # ابحث عن القطعة في الحالة الحالية
                    found = False
                    for current_block in current_state.blocks:
                        if (current_block.id == state_block.id and 
                            current_block.x == state_block.x and 
                            current_block.y == state_block.y):
                            found = True
                            blocks_matched += 1
                            break
                    if not found:
                        match = False
                        break
                
                if match and blocks_matched == len(state.blocks):
                    start_index = i
                    break
    
    # إذا لم نجد أي مطابقة، نبدأ من بداية المسار
    if start_index == -1:
        print(f"Warning: Current state not found in solution path!")
        print(f"Current: {len(current_state.blocks)} blocks, IDs: {sorted([b.id for b in current_state.blocks])}")
        print(f"Path states: {[len(s.blocks) for s in solution_path[:5]]} blocks")
        start_index = 0
    
    # استخراج الحركات من هذه النقطة
    moves = []
    for i in range(start_index, len(solution_path) - 1):
        state = solution_path[i]
        next_state = solution_path[i + 1]
        
        if next_state.action is not None:
            moves.append(next_state.action)
    
    print(f"Extracted {len(moves)} moves from solution path (starting from index {start_index})")
    return moves

def get_algorithm_for_level(level_index):
    """اختر أفضل خوارزمية حسب مستوى الصعوبة."""
    # مستوى 1 (الكبير): A* أو Greedy
    if level_index == 0:
        return "A*"
    # مستوى 2 (المتوسط): BFS أو A*
    elif level_index == 1:
        return "BFS"
    # مستوى 3 و4 (الصغير): BFS (أسرع)
    else:
        return "BFS"

def run_game(level_index=0, algorithm_name=None):
    try:
        current_level = level_index % len(LEVEL_FILES)
        LEVEL_FILE = LEVEL_FILES[current_level]
        
        # اختيار الخوارزمية المناسبة إذا لم تحدد
        if algorithm_name is None:
            algorithm_name = get_algorithm_for_level(current_level)
        
        print(f"Loading level: {LEVEL_FILE}")
        print(f"Selected algorithm: {algorithm_name}")
        
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
        ai_move_delay = 500  # سرعة الحركة بالمللي ثانية
        last_ai_move_time = 0
        ai_replan_count = 0
        max_replan_attempts = 3
        
        # تعريف الخوارزمية حسب الاختيار
        algorithm_map = {
            "BFS": BFSSolver,
            "DFS": DFSSolver,
            "DFS_Recursive": DFSRecursiveSolver,
            "UCS": UCSSolver,
            "Hill_Climbing": HillClimbingSolver,
            "Greedy": GreedySolver,
            "A*": AStarSolver
        }
        
        if algorithm_name not in algorithm_map:
            print(f"Warning: Algorithm '{algorithm_name}' not found. Defaulting to BFS.")
            algorithm_name = "BFS"
        
        ai_solver_class = algorithm_map[algorithm_name]
        ai_solver = ai_solver_class()

        clock = pygame.time.Clock()
        
        while running:
            current_time = pygame.time.get_ticks()

            if is_ai_playing and ai_solution_path:
                if current_time - last_ai_move_time > ai_move_delay:
                    # محاولة تنفيذ الحركة الحالية
                    if len(ai_solution_path) > 0:
                        action = ai_solution_path[0]
                        block_id, dx, dy, distance = action
                        
                        print(f"\nAI attempting move {len(ai_solution_path)}: {action}")
                        
                        # التحقق من صحة الحركة
                        if not current_state.is_move_valid(block_id, (dx, dy), distance):
                            print(f"Move {action} is no longer valid! Skipping.")
                            ai_solution_path.pop(0)  # إزالة الحركة غير الصالحة
                            message = f"AI skipped invalid move"
                            
                            # إذا أصبحت القائمة فارغة، توقف
                            if not ai_solution_path:
                                is_ai_playing = False
                                message = "AI: Path completed (some moves skipped)"
                        else:
                            # تنفيذ الحركة
                            new_state, status = logic.try_move_manual(current_state, block_id, (dx, dy), distance)
                            
                            if status in [MOVE_SUCCESS, MOVE_EXIT]:
                                # نجاح الحركة
                                current_state = new_state
                                move_count += 1
                                ai_solution_path.pop(0)  # إزالة الحركة المنفذة
                                
                                if status == MOVE_SUCCESS:
                                    sound_manager.play_move()
                                    print(f"Move successful. Remaining moves: {len(ai_solution_path)}")
                                    message = f"AI moved block {block_id}"
                                else:
                                    sound_manager.play_exit()
                                    print(f"Exit successful. Remaining moves: {len(ai_solution_path)}")
                                    message = f"AI exited block {block_id}"
                            else:
                                print(f"Move execution failed. Skipping.")
                                ai_solution_path.pop(0)
                                message = f"AI: Move execution failed"
                    
                    last_ai_move_time = current_time

                    # إذا نفذت كل الحركات
                    if not ai_solution_path and is_ai_playing:
                        is_ai_playing = False
                        if current_state.check_win_condition():
                            message = f"AI solved the puzzle in {move_count} moves!"
                            sound_manager.play_win()
                            print("Puzzle solved by AI!")
                        else:
                            # لا تقم بإعادة التخطيط تلقائياً
                            message = f"AI finished path. Press S to re-plan."
                            print("AI path completed but puzzle not solved.")
                            print(f"Current state: {len(current_state.blocks)} blocks remaining")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if event.key == pygame.K_s:  # بدء/إيقاف الـ AI
                        if is_ai_playing:
                            # إيقاف الـ AI إذا كان يعمل
                            is_ai_playing = False
                            ai_solution_path = []
                            message = "AI stopped."
                            print("AI stopped by user.")
                        else:
                            # بدء الـ AI من الحالة الحالية
                            message = f"{algorithm_name} is solving from current state..."
                            viz.draw(current_state, move_count=move_count, message=message)
                            pygame.display.flip()

                            # استخدام الخوارزمية المحددة
                            print(f"\n{'='*50}")
                            print(f"Starting AI solver ({algorithm_name}) from CURRENT state...")
                            print(f"Current state has {len(current_state.blocks)} blocks")
                            print(f"Blocks IDs: {[block.id for block in current_state.blocks]}")
                            
                            # إعادة تهيئة الخوارزمية
                            ai_solver = ai_solver_class()
                            start_time = time.time()
                            solution_path = ai_solver.solve(current_state)
                            end_time = time.time()
                            solve_time = end_time - start_time
                            
                            if solution_path:
                                print(f"Found solution path with {len(solution_path)} states")
                                print(f"Time taken: {solve_time:.2f} seconds")
                                print(f"Nodes explored: {ai_solver.nodes_explored}")
                                
                                # استخراج الحركات الصالحة من الحل
                                ai_solution_path = extract_moves_from_solution_path(solution_path, current_state)
                                
                                if ai_solution_path:
                                    print(f"Found {len(ai_solution_path)} valid moves from current state")
                                    print(f"First 5 moves:")
                                    for i, action in enumerate(ai_solution_path[:5]):
                                        print(f"  Move {i+1}: {action}")
                                    
                                    # التحقق من أن الحركة الأولى صالحة
                                    if ai_solution_path:
                                        first_action = ai_solution_path[0]
                                        block_id, dx, dy, distance = first_action
                                        
                                        if current_state.is_move_valid(block_id, (dx, dy), distance):
                                            is_ai_playing = True
                                            last_ai_move_time = 0
                                            ai_replan_count = 0
                                            
                                            if solution_path[-1].check_win_condition():
                                                message = f"AI found solution in {len(ai_solution_path)} moves!"
                                                print(f"Complete solution found! {len(ai_solution_path)} moves to win.")
                                            else:
                                                message = f"AI found path to improve state ({len(ai_solution_path)} moves)"
                                                print(f"Improvement path found. Target has {len(solution_path[-1].blocks)} blocks.")
                                        else:
                                            message = f"Error: First move is not valid."
                                            print(f"ERROR: First move is invalid in current state!")
                                            ai_solution_path = []
                                else:
                                    message = f"{algorithm_name}: No valid moves found."
                                    print("No valid moves could be extracted from solution.")
                            else:
                                message = f"{algorithm_name}: No solution found."
                                print("No solution found from current state.")
                                print(f"Time taken: {solve_time:.2f} seconds")
                                print(f"Nodes explored: {ai_solver.nodes_explored}")
                            
                            print(f"{'='*50}\n")
                        
                        continue

                    if is_ai_playing:
                        # إذا كان الـ AI يعمل، أي زر يوقفه
                        is_ai_playing = False
                        ai_solution_path = []
                        message = "AI stopped by user."
                        print("AI stopped by user input.")
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
                    elif event.key == pygame.K_p:
                        logic.print_possible_moves(current_state)
                    
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
                        
                        if distance > 0 and distance <= 1:  # سماح فقط بمسافة 1
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
                 
            viz.draw(current_state, selected_block_coords=selected_coords, move_count=move_count, 
                    message=message, control_mode=control_mode, trapped_block_indices=trapped_indices,
                    is_ai_playing=is_ai_playing)
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
        screen = pygame.display.set_mode((800, 500))
        pygame.display.set_caption("The Chroma Escape - Level Selection")
        clock = pygame.time.Clock()
        
        try:
            font = pygame.font.Font(None, 36)
            small_font = pygame.font.Font(None, 24)
            medium_font = pygame.font.Font(None, 20)
        except pygame.error:
            font = pygame.font.SysFont(None, 36)
            small_font = pygame.font.SysFont(None, 24)
            medium_font = pygame.font.SysFont(None, 20)
        
        algorithms = ["BFS", "DFS", "DFS_Recursive", "UCS", "Greedy", "A*","Hill_Climbing",
]
        selected_algorithm = 0
        selected_level = 0
        
        # اقتراح أفضل خوارزمية لكل مستوى
        algorithm_suggestions = ["A*", "BFS", "BFS", "BFS"]
        
        running = True
        while running:
            screen.fill((240, 240, 240))
            
            title_text = font.render("The Chroma Escape - Level Selection", True, (0, 0, 0))
            title_rect = title_text.get_rect(center=(400, 50))
            screen.blit(title_text, title_rect)
            
            # عرض المستويات
            level_text = medium_font.render("Select Level:", True, (0, 0, 0))
            screen.blit(level_text, (50, 100))
            
            for i, level_file in enumerate(LEVEL_FILES):
                level_name = os.path.basename(level_file).replace(".json", "").replace("_", " ").title()
                color = (0, 100, 0) if i == selected_level else (0, 0, 0)
                level_display = small_font.render(f"{i+1}. {level_name}", True, color)
                screen.blit(level_display, (70, 130 + i * 30))
                
                # عرض الخوارزمية المقترحة
                suggested = algorithm_suggestions[i]
                suggestion_text = small_font.render(f"Suggested: {suggested}", True, (100, 100, 100))
                screen.blit(suggestion_text, (200, 130 + i * 30))
            
            # عرض خوارزميات البحث
            algo_text = medium_font.render("Select Algorithm:", True, (0, 0, 0))
            screen.blit(algo_text, (50, 250))
            
            for i, algo in enumerate(algorithms):
                color = (0, 100, 0) if i == selected_algorithm else (0, 0, 0)
                algo_display = small_font.render(f"{i+1}. {algo}", True, color)
                screen.blit(algo_display, (70, 280 + i * 30))
            
            # تعليمات
            instructions = [
                "UP/DOWN: Navigate levels",
                "LEFT/RIGHT: Navigate algorithms",
                "ENTER: Start Game",
                "ESC: Quit"
            ]
            
            for i, instruction in enumerate(instructions):
                inst_text = small_font.render(instruction, True, (100, 100, 100))
                screen.blit(inst_text, (400, 300 + i * 25))
            
            # عرض الخوارزمية المقترحة للمستوى المختار
            suggested_algo = algorithm_suggestions[selected_level]
            suggestion_text = font.render(f"Suggested for this level: {suggested_algo}", True, (0, 100, 0))
            screen.blit(suggestion_text, (400, 200))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        selected_level = (selected_level - 1) % len(LEVEL_FILES)
                    elif event.key == pygame.K_DOWN:
                        selected_level = (selected_level + 1) % len(LEVEL_FILES)
                    elif event.key == pygame.K_LEFT:
                        selected_algorithm = (selected_algorithm - 1) % len(algorithms)
                    elif event.key == pygame.K_RIGHT:
                        selected_algorithm = (selected_algorithm + 1) % len(algorithms)
                    elif event.key == pygame.K_RETURN:
                        pygame.quit()
                        run_game(selected_level, algorithms[selected_algorithm])
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