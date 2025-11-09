import copy
import pygame
import os
import sys
from controller import GameLogic, load_game_state
from view import GameVisualizer, CELL_SIZE

# قائمة بالمستويات المتاحة
# تأكد من وجود مجلد 'levels' وبداخله هذه الملفات
LEVEL_FILES = [
    "levels/level_01.json",
    "levels/level_02.json",
    "levels/level_03.json",
    "levels/level_04.json"
]

def run_game(level_index=0):
    """
    تشغيل اللعبة للمستوى المحدد
    """
    current_level = level_index % len(LEVEL_FILES)
    LEVEL_FILE = LEVEL_FILES[current_level]
    
    current_state = load_game_state(LEVEL_FILE)
    
    if current_state is None:
        print(f"Error: Failed to load game state from {LEVEL_FILE}. Check file path or content.")
        return

    logic = GameLogic()
    
    if current_state.board.width <= 0 or current_state.board.height <= 0:
        print(f"Error: Invalid board dimensions ({current_state.board.width}x{current_state.board.height}).")
        return
        
    viz = GameVisualizer(current_state.board.width, current_state.board.height)

    running = True
    selected_block_index = None
    drag_start_cell = None
    move_count = 0
    message = ""
    control_mode = "mouse"  # "mouse" أو "keyboard"
    
    # حفظ الحالة الأولية لإعادة التشغيل
    initial_state = current_state
    
    while running:
        # التحقق من حالة الفوز
        if current_state.check_win_condition():
            print("Congratulations! You solved the puzzle!")
            viz.draw_win_screen(move_count)
            
            # انتظار ضغط ESC للخروج أو الانتقال للمستوى التالي
            waiting_for_exit = True
            while waiting_for_exit:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        waiting_for_exit = False
                        running = False
                    # يمكنك إضافة خيار للانتقال للمستوى التالي هنا
                    # elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    #     run_game(current_level + 1)
                    #     waiting_for_exit = False
                viz.clock.tick(10)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_u:  # التراجع عن الحركة
                    current_state = logic.undo_move(current_state)
                    move_count = max(0, move_count - 1)
                    message = "Move undone"
                elif event.key == pygame.K_r:  # إعادة التشغيل
                    current_state = copy.deepcopy(initial_state)
                    move_count = 0
                    logic.move_history = [] # تفريغ سجل الحركات
                    message = "Level restarted"
                elif event.key == pygame.K_m:  # التبديل إلى التحكم بالماوس
                    control_mode = "mouse"
                    message = "Switched to mouse control"
                elif event.key == pygame.K_k:  # التبديل إلى التحكم بالكيبورد
                    control_mode = "keyboard"
                    message = "Switched to keyboard control"
                
                # التحكم بالكيبورد
                elif control_mode == "keyboard":
                    if event.key == pygame.K_TAB:  # تحديد القطعة التالية
                        current_state = logic.select_next_block(current_state, not event.mod & pygame.KMOD_SHIFT)
                    elif event.key in [pygame.K_UP, pygame.K_w]:  # التحرك للأعلى
                        new_state = logic.try_move_keyboard(current_state, "UP")
                        if new_state != current_state:
                            current_state = new_state
                            move_count += 1
                            message = ""
                        else:
                            message = "Invalid move!"
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:  # التحرك للأسفل
                        new_state = logic.try_move_keyboard(current_state, "DOWN")
                        if new_state != current_state:
                            current_state = new_state
                            move_count += 1
                            message = ""
                        else:
                            message = "Invalid move!"
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:  # التحرك لليسار
                        new_state = logic.try_move_keyboard(current_state, "LEFT")
                        if new_state != current_state:
                            current_state = new_state
                            move_count += 1
                            message = ""
                        else:
                            message = "Invalid move!"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:  # التحرك لليمين
                        new_state = logic.try_move_keyboard(current_state, "RIGHT")
                        if new_state != current_state:
                            current_state = new_state
                            move_count += 1
                            message = ""
                        else:
                            message = "Invalid move!"
                    
            elif event.type == pygame.MOUSEBUTTONDOWN and control_mode == "mouse":
                mouse_x, mouse_y = event.pos
                cell_x = mouse_x // CELL_SIZE
                cell_y = mouse_y // CELL_SIZE
                
                # البحث عن القطعة التي تم النقر عليها
                for i, block in enumerate(current_state.blocks):
                    if (cell_x, cell_y) in block.get_absolute_coords():
                        selected_block_index = i
                        drag_start_cell = (cell_x, cell_y)
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
                        new_state = logic.try_move_manual(
                            current_state, 
                            selected_block_index, 
                            direction_vector, 
                            distance
                        )
                        
                        # التحقق مما إذا كانت الحركة ممكنة
                        if new_state != current_state:
                            current_state = new_state
                            move_count += 1
                            message = ""
                        else:
                            message = "Invalid move!"

                selected_block_index = None
                drag_start_cell = None

        selected_coords = None
        if selected_block_index is not None:
             selected_coords = set(current_state.blocks[selected_block_index].get_absolute_coords())
             
        viz.draw(current_state, selected_block_coords=selected_coords, move_count=move_count, message=message, control_mode=control_mode)
        viz.clock.tick(60)
        
    pygame.quit()

def show_level_selection():
    """
    عرض قائمة المستويات المتاحة للسماح للاعب بالاختيار
    """
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
        
        # عرض المستويات المتاحة بشكل ديناميكي
        for i, level_file in enumerate(LEVEL_FILES):
            level_name = os.path.basename(level_file).replace(".json", "").replace("_", " ").title()
            level_text = small_font.render(f"{i+1}. {level_name}", True, (0, 0, 0))
            level_rect = level_text.get_rect(center=(300, 120 + i * 40))
            screen.blit(level_text, level_rect)
        
        # تحديث التعليمات بناءً على عدد المستويات المتاحة
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
                # --- هذا هو الجزء المهم الذي تم تعديله ---
                # أصبح الآن يتحقق من كل المفاتيح من 1 إلى عدد المستويات المتاحة
                elif pygame.K_1 <= event.key <= pygame.K_1 + len(LEVEL_FILES) - 1:
                    level_index = event.key - pygame.K_1
                    # إغلاق نافذة الاختيار قبل بدء اللعبة
                    pygame.quit()
                    # بدء اللعبة بالمستوى المختار
                    run_game(level_index)
                    # بعد انتهاء اللعبة، لا نعود إلى قائمة الاختيار
                    return
        
        clock.tick(30)
    
    pygame.quit()

if __name__ == '__main__':
    show_level_selection()