import pygame
import sys
import copy

CELL_SIZE = 40
GRID_COLOR = (250, 250, 250)
X_COLOR = (255, 100, 100)
O_COLOR = (100, 100, 255)
HIGHLIGHT_COLOR = (155, 155, 155)
BG_COLOR = (10, 10, 30)

WINDOW_SIZE = 800


class TicTacToeVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Infinite Tic Tac Toe")
        self.clock = pygame.time.Clock()
        self.board = {}  # {(x, y): 'X' or 'O'}
        self.offset_x = WINDOW_SIZE // 2
        self.offset_y = WINDOW_SIZE // 2
        self.zoom = 1.0
        self.recent_moves = []  # list of (x, y)
        self.history = []
        self.history_index = -1


    def world_to_screen(self, x, y):
        screen_x = round(x * CELL_SIZE * self.zoom + self.offset_x)
        screen_y = round(y * CELL_SIZE * self.zoom + self.offset_y)
        return screen_x, screen_y

    def screen_to_world(self, sx, sy):
        x = int((sx - self.offset_x) // (CELL_SIZE * self.zoom))
        y = int((sy - self.offset_y) // (CELL_SIZE * self.zoom))
        return x, y

    def draw_board(self, board_override=None):
        board = board_override if board_override is not None else self.board
        self.screen.fill(BG_COLOR)

        # Draw visible grid
        grid_range = int(WINDOW_SIZE / (CELL_SIZE * self.zoom)) + 4
        start_x = int(-self.offset_x / (CELL_SIZE * self.zoom)) - 2
        start_y = int(-self.offset_y / (CELL_SIZE * self.zoom)) - 2

        for i in range(start_x, start_x + grid_range):
            x = round(i * CELL_SIZE * self.zoom + self.offset_x)
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_SIZE))

        for j in range(start_y, start_y + grid_range):
            y = round(j * CELL_SIZE * self.zoom + self.offset_y)
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_SIZE, y))

        # Draw pieces
        for (x, y), player in board.items():


            sx, sy = self.world_to_screen(x, y)
            rect = pygame.Rect(sx, sy, CELL_SIZE * self.zoom, CELL_SIZE * self.zoom)


            if player == 'X':
                color = X_COLOR
            else:
                color = O_COLOR

            if (x, y) in self.recent_moves:
                index = self.recent_moves.index((x, y))
                alpha = int(255 * (0.7 - 0.2 * (3 - index)))  # 0.7, 0.5, 0.3 alpha
                highlight_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                highlight_surface.fill((*color, alpha))
                self.screen.blit(highlight_surface, rect.topleft)

            font_size = int(0.9 * CELL_SIZE * self.zoom)
            font = pygame.font.SysFont(None, max(font_size, 1))
            img = font.render(player, True, color)

            self.screen.blit(img, (sx + 5 * self.zoom, sy + 5 * self.zoom))

    def update_move(self, x, y, player):
        self.board[(x, y)] = player
        self.recent_moves.append((x, y))
        if len(self.recent_moves) > 4:
            self.recent_moves.pop(0)
        self.history.append(copy.deepcopy(self.board))
        self.history_index = len(self.history) - 1

    def run_once(self):
        self.draw_board()
        pygame.display.flip()
        self.clock.tick(60)

    def get_human_move(self):
        while True:
            self.run_once()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.offset_x += 50
                    elif event.key == pygame.K_RIGHT:
                        self.offset_x -= 50
                    elif event.key == pygame.K_UP:
                        self.offset_y += 50
                    elif event.key == pygame.K_DOWN:
                        self.offset_y -= 50
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        x, y = self.screen_to_world(*event.pos)
                        return x, y
                    elif event.button == 4:
                        self.zoom *= 1.1
                    elif event.button == 5:
                        self.zoom /= 1.1

    def wait_utill_quit(self):
        while True:
            if 0 <= self.history_index < len(self.history):
                self.draw_board(self.history[self.history_index])
            else:
                self.draw_board()

            pygame.display.flip()
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.history_index = min(len(self.history) - 1, self.history_index + 1)

                
    def close(self):
        pygame.quit()
