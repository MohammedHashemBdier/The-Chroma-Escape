import os
import pygame
from model import GameState, Block, Board, MovementType
import math
import random

BACKGROUND_COLOR = (240, 240, 240) 
GRID_LINE_COLOR = (150, 150, 150)

COLOR_MAP = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "gray": (100, 100, 100),
    "green": (0, 255, 0),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "cyan": (0, 255, 255),
}

class GameVisualizer:
    def __init__(self, board: Board):
        pygame.init() 
        
        self.width = board.width
        self.height = board.height
        
        info = pygame.display.Info()
        screen_w, screen_h = info.current_w, info.current_h
        
        self.CELL_SIZE = self._calculate_cell_size(board.width, board.height, screen_w, screen_h)
        
        self.screen_width = self.width * self.CELL_SIZE
        self.screen_height = self.height * self.CELL_SIZE

        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{(screen_w - self.screen_width) // 2},{(screen_h - self.screen_height) // 2}"
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("The Chroma Escape - Smart Search")
        
        self.clock = pygame.time.Clock()
        
        try:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except pygame.error:
            self.font = pygame.font.SysFont(None, 36)
            self.small_font = pygame.font.SysFont(None, 24)
        
        self.particles = []

    def _calculate_cell_size(self, board_w, board_h, screen_w, screen_h):
        MARGIN = 100
        max_cell_width = (screen_w - MARGIN) // board_w
        max_cell_height = (screen_h - MARGIN) // board_h
        optimal_size = min(max_cell_width, max_cell_height)
        MAX_CELL_SIZE = 100
        MIN_CELL_SIZE = 30
        return max(MIN_CELL_SIZE, min(optimal_size, MAX_CELL_SIZE))

    def _draw_movement_arrow(self, block: Block, is_selected: bool = False):
        arrow_color = (255, 255, 255) if is_selected else (200, 200, 200)
        arrow_size = self.CELL_SIZE // 4
        center_x = int(block.x * self.CELL_SIZE + self.CELL_SIZE // 2)
        center_y = int(block.y * self.CELL_SIZE + self.CELL_SIZE // 2)
        
        if block.movement_type.name == 'ANY':
            pygame.draw.line(self.screen, arrow_color, (center_x - arrow_size, center_y), (center_x + arrow_size, center_y), 5)
            pygame.draw.line(self.screen, arrow_color, (center_x, center_y - arrow_size), (center_x, center_y + arrow_size), 5)
            return
        elif block.movement_type.name == 'HORIZONTAL':
            pygame.draw.line(self.screen, arrow_color, (center_x - arrow_size, center_y), (center_x + arrow_size, center_y), 5)
            pygame.draw.polygon(self.screen, arrow_color, [(center_x + arrow_size, center_y), (center_x + arrow_size - 5, center_y - 5), (center_x + arrow_size - 5, center_y + 5)])
            pygame.draw.polygon(self.screen, arrow_color, [(center_x - arrow_size, center_y), (center_x - arrow_size + 5, center_y - 5), (center_x - arrow_size + 5, center_y + 5)])
        elif block.movement_type.name == 'VERTICAL':
            pygame.draw.line(self.screen, arrow_color, (center_x, center_y - arrow_size), (center_x, center_y + arrow_size), 5)
            pygame.draw.polygon(self.screen, arrow_color, [(center_x, center_y + arrow_size), (center_x - 5, center_y + arrow_size - 5), (center_x + 5, center_y + arrow_size - 5)])
            pygame.draw.polygon(self.screen, arrow_color, [(center_x, center_y - arrow_size), (center_x - 5, center_y - arrow_size + 5), (center_x + 5, center_y - arrow_size + 5)])

    def _draw_possible_moves(self, state: GameState, selected_block_index: int):
        if selected_block_index is None or selected_block_index >= len(state.blocks):
            return
            
        block = state.blocks[selected_block_index]
        if block.move_lock > 0:
            return

        possible_moves = []
        
        if block.movement_type in [MovementType.HORIZONTAL, MovementType.ANY]:
            possible_moves.extend([(-1, 0), (1, 0)])
        if block.movement_type in [MovementType.VERTICAL, MovementType.ANY]:
            possible_moves.extend([(0, -1), (0, 1)])
        
        for dx, dy in possible_moves:
            arrow_x = block.x + dx * 2
            arrow_y = block.y + dy * 2
            
            if 0 <= arrow_x < state.board.width and 0 <= arrow_y < state.board.height:
                center_x = arrow_x * self.CELL_SIZE + self.CELL_SIZE // 2
                center_y = arrow_y * self.CELL_SIZE + self.CELL_SIZE // 2
                
                s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE))
                s.set_alpha(100)
                s.fill((100, 200, 100))
                self.screen.blit(s, (arrow_x * self.CELL_SIZE, arrow_y * self.CELL_SIZE))
                
                if dx > 0:
                    pygame.draw.polygon(self.screen, (0, 150, 0), 
                                       [(center_x + 10, center_y), 
                                        (center_x - 5, center_y - 8), 
                                        (center_x - 5, center_y + 8)])
                elif dx < 0:
                    pygame.draw.polygon(self.screen, (0, 150, 0), 
                                       [(center_x - 10, center_y), 
                                        (center_x + 5, center_y - 8), 
                                        (center_x + 5, center_y + 8)])
                elif dy > 0:
                    pygame.draw.polygon(self.screen, (0, 150, 0), 
                                       [(center_x, center_y + 10), 
                                        (center_x - 8, center_y - 5), 
                                        (center_x + 8, center_y - 5)])
                elif dy < 0:
                    pygame.draw.polygon(self.screen, (0, 150, 0), 
                                       [(center_x, center_y - 10), 
                                        (center_x - 8, center_y + 5), 
                                        (center_x + 8, center_y + 5)])

    def _draw_cell(self, x: int, y: int, color: tuple, is_selected: bool = False, is_locked: bool = False, is_trapped: bool = False, display_lock: int = -1):
        left = int(x * self.CELL_SIZE)
        top = int(y * self.CELL_SIZE)
        
        final_color = color
        if is_trapped:
            final_color = tuple(c // 4 for c in color)
        elif is_locked:
            r, g, b = color
            grey = (r + g + b) / 3
            final_color = (int((r + grey) / 2.5), int((g + grey) / 2.5), int((b + grey) / 2.5))

        if is_selected:
            glow_color = tuple(min(255, c + 50) for c in final_color)
            pygame.draw.rect(self.screen, glow_color, (left-2, top-2, self.CELL_SIZE+4, self.CELL_SIZE+4))
            pygame.draw.rect(self.screen, final_color, (left, top, self.CELL_SIZE, self.CELL_SIZE))
        else:
            pygame.draw.rect(self.screen, final_color, (left, top, self.CELL_SIZE, self.CELL_SIZE))

        border_thickness = 3 if is_selected else 1
        border_color = (0, 0, 0) if is_selected else GRID_LINE_COLOR
        pygame.draw.rect(self.screen, border_color, (left, top, self.CELL_SIZE, self.CELL_SIZE), border_thickness)

        if display_lock > 0:
            lock_text = self.small_font.render(str(display_lock), True, (255, 255, 255))
            text_rect = lock_text.get_rect(center=(left + self.CELL_SIZE // 2, top + self.CELL_SIZE // 2))
            self.screen.blit(lock_text, text_rect)
    
    def _draw_grid(self, exits: dict):
        for x in range(self.width + 1):
            x_pos = x * self.CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (x_pos, 0), (x_pos, self.screen_height), 1)
        
        for y in range(self.height + 1):
            y_pos = y * self.CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (0, y_pos), (self.screen_width, y_pos), 1)

        border_thickness = 4
        border_color = (50, 50, 50)
        pygame.draw.rect(self.screen, border_color, (0, 0, self.screen_width, self.screen_height), border_thickness)

        exit_thickness = 8 
        
        for (x, y), exit_info in exits.items():
            color = COLOR_MAP.get(exit_info["color"].lower(), (200, 200, 200))
            is_on_edge = (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1)

            if is_on_edge:
                if x == 0:
                    start_pos = (0, y * self.CELL_SIZE)
                    end_pos = (0, (y + 1) * self.CELL_SIZE)
                    pygame.draw.line(self.screen, color, start_pos, end_pos, exit_thickness)
                elif x == self.width - 1:
                    start_pos = (self.screen_width, y * self.CELL_SIZE)
                    end_pos = (self.screen_width, (y + 1) * self.CELL_SIZE)
                    pygame.draw.line(self.screen, color, start_pos, end_pos, exit_thickness)
                elif y == 0:
                    start_pos = (x * self.CELL_SIZE, 0)
                    end_pos = ((x + 1) * self.CELL_SIZE, 0)
                    pygame.draw.line(self.screen, color, start_pos, end_pos, exit_thickness)
                elif y == self.height - 1:
                    start_pos = (x * self.CELL_SIZE, self.screen_height)
                    end_pos = ((x + 1) * self.CELL_SIZE, self.screen_height)
                    pygame.draw.line(self.screen, color, start_pos, end_pos, exit_thickness)
                
    def draw_win_screen(self, move_count=0):
        WIN_COLOR = (124, 252, 0)
        TEXT_COLOR = (0, 0, 0)
        
        self.screen.fill(WIN_COLOR)
        
        text = self.font.render("PUZZLE SOLVED!", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        self.screen.blit(text, text_rect)
        
        moves_text = self.font.render(f"Moves: {move_count}", True, TEXT_COLOR)
        moves_rect = moves_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(moves_text, moves_rect)
        
        exit_text = self.small_font.render("Press ESC to exit", True, TEXT_COLOR)
        exit_rect = exit_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        self.screen.blit(exit_text, exit_rect)
        
        pygame.display.flip()
    
    def draw_ui(self, state: GameState, move_count=0, message="", control_mode="mouse"):
        moves_text = self.small_font.render(f"Moves: {move_count}", True, (0, 0, 0))
        self.screen.blit(moves_text, (10, 10))
        
        blocks_text = self.small_font.render(f"Blocks: {len(state.blocks)}", True, (0, 0, 0))
        self.screen.blit(blocks_text, (10, 40))

        y_offset = 70
        for color, lock_value in state.display_lock.items():
            lock_text = self.small_font.render(f"{color.capitalize()}: {lock_value}", True, (0, 0, 0))
            self.screen.blit(lock_text, (10, y_offset))
            y_offset += 25

        if state.selected_block_index is not None and state.selected_block_index < len(state.blocks):
            selected_block = state.blocks[state.selected_block_index]
            lock_text = f"Selected: {selected_block.color.capitalize()} (Lock: {selected_block.move_lock})"
            lock_surface = self.small_font.render(lock_text, True, (0, 0, 0))
            self.screen.blit(lock_surface, (10, y_offset))
        
        if message:
            msg_text = self.small_font.render(message, True, (255, 0, 0))
            msg_rect = msg_text.get_rect(center=(self.screen_width // 2, 30))
            self.screen.blit(msg_text, msg_rect)
        
        if control_mode == "keyboard":
            instructions = [
                "Use TAB to select blocks",
                "Use ARROW KEYS or WASD to move",
                "Press U to undo last move",
                "Press R to restart level",
                "Press M to switch to mouse control",
                "Press S to solve with AI",
                "Press ESC to quit"
            ]
        else:
            instructions = [
                "Click and drag to move blocks",
                "Press K to switch to keyboard control",
                "Press U to undo last move",
                "Press R to restart level",
                "Press S to solve with AI",
                "Press ESC to quit"
            ]
        
        y_pos = self.screen_height - 140
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (0, 0, 0))
            self.screen.blit(inst_text, (10, y_pos))
            y_pos += 25
    
    def _draw_particles(self):
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            pygame.draw.circle(
                self.screen, 
                particle['color'], 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
    
    def _create_exit_particles(self, x: int, y: int, color: tuple):
        center_x = x * self.CELL_SIZE + self.CELL_SIZE // 2
        center_y = y * self.CELL_SIZE + self.CELL_SIZE // 2
        
        for _ in range(20):
            angle = math.radians(random.random() * 360)
            speed = random.random() * 3 + 1
            self.particles.append({
                'x': center_x,
                'y': center_y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'color': color,
                'size': random.random() * 5 + 2,
                'life': 30
            })

    def draw(self, state: GameState, selected_block_coords: set = None, move_count=0, message="", control_mode="mouse", trapped_block_indices=None):
        self.screen.fill(BACKGROUND_COLOR)
        
        for x, y in state.board.barriers:
            self._draw_cell(x, y, COLOR_MAP['gray'])
        
        if control_mode == "keyboard" and state.selected_block_index is not None:
            self._draw_possible_moves(state, state.selected_block_index)
            
        for i, block in enumerate(state.blocks):
            base_color = COLOR_MAP.get(block.color.lower(), (0, 0, 0))
            is_trapped_by_obstacles = (trapped_block_indices and i in trapped_block_indices)
            is_locked = (block.move_lock > 0)
            
            color = base_color
            if is_trapped_by_obstacles:
                color = tuple(c // 4 for c in base_color)
            elif is_locked:
                r, g, b = base_color
                grey = (r + g + b) / 3
                color = (int((r + grey) / 2.5), int((g + grey) / 2.5), int((b + grey) / 2.5))
            
            is_selected = (i == state.selected_block_index) or (set(block.get_absolute_coords()) == selected_block_coords)
            
            display_lock_value = block.move_lock if block.move_lock > 0 else -1
            
            for x, y in block.get_absolute_coords():
                self._draw_cell(x, y, color, is_selected=is_selected, is_locked=is_locked, is_trapped=is_trapped_by_obstacles, display_lock=display_lock_value)

            self._draw_movement_arrow(block, is_selected=is_selected)
        
        self._draw_particles()
        self._draw_grid(state.board.exits)
        self.draw_ui(state, move_count, message, control_mode)
        
        pygame.display.flip()
    
    def wait_for_quit(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            self.clock.tick(10)
        
        pygame.quit()