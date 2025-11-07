import pygame
from model import GameState, Block, Board

CELL_SIZE = 80
GRID_LINE_COLOR = (150, 150, 150)
BACKGROUND_COLOR = (240, 240, 240) 
WIN_COLOR = (0, 255, 0)

COLOR_MAP = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "gray": (100, 100, 100),
}

class GameVisualizer:
    def __init__(self, board_width, board_height):
        pygame.init()
        
        self.width = board_width
        self.height = board_height
        
        self.screen_width = self.width * CELL_SIZE
        self.screen_height = self.height * CELL_SIZE
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Unblock Jam - Smart Search")
        
        self.clock = pygame.time.Clock()


    def draw(self, state: GameState, selected_block_coords: set = None):
        
        self.screen.fill(BACKGROUND_COLOR)
        
        for x, y in state.board.barriers:
            self._draw_cell(x, y, COLOR_MAP['gray'])
            
        for (x, y), color_name in state.board.exits.items():
            color = COLOR_MAP.get(color_name, (200, 200, 200)) # لون افتراضي لو ما انوجد
            self._draw_cell(x, y, color, is_exit=True)

        for block in state.blocks:
            color = COLOR_MAP.get(block.color, (0, 0, 0)) # لون القطعة
            
            is_selected = set(block.get_absolute_coords()) == selected_block_coords
            
            for x, y in block.get_absolute_coords():
                self._draw_cell(x, y, color, is_selected=is_selected)

        self._draw_grid()

        pygame.display.flip()

    
    def _draw_cell(self, x: int, y: int, color: tuple, is_selected: bool = False, is_exit: bool = False):
        
        left = x * CELL_SIZE
        top = y * CELL_SIZE
        
        pygame.draw.rect(self.screen, color, (left, top, CELL_SIZE, CELL_SIZE))

        border_thickness = 3 if is_selected else 1
        border_color = (0, 0, 0) if is_selected else GRID_LINE_COLOR
        
        pygame.draw.rect(self.screen, border_color, (left, top, CELL_SIZE, CELL_SIZE), border_thickness)

        if is_exit:
            pygame.draw.rect(self.screen, color, (left, top, CELL_SIZE, CELL_SIZE), 5)


    def _draw_grid(self):
        for x in range(self.width + 1):
            x_pos = x * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (x_pos, 0), (x_pos, self.screen_height), 1)
        
        for y in range(self.height + 1):
            y_pos = y * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (0, y_pos), (self.screen_width, y_pos), 1)

    
    def wait_for_quit(self):
        

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.clock.tick(10)
        
        pygame.quit()
