import pygame
import sys

CELL_SIZE = 40
GRID_COLOR = (200, 200, 200)
X_COLOR = (255, 100, 100)
O_COLOR = (100, 100, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
BG_COLOR = (255, 255, 255)

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
        self.latest_move = None

    def world_to_screen(self, x, y):
        screen_x = round(x * CELL_SIZE * self.zoom + self.offset_x)
        screen_y = round(y * CELL_SIZE * self.zoom + self.offset_y)
        return screen_x, screen_y

    def screen_to_world(self, sx, sy):
        x = int((sx - self.offset_x) // (CELL_SIZE * self.zoom))
        y = int((sy - self.offset_y) // (CELL_SIZE * self.zoom))
        return x, y

    def draw_board(self):
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
        for (x, y), player in self.board.items():
            sx, sy = self.world_to_screen(x, y)
            rect = pygame.Rect(sx, sy, CELL_SIZE * self.zoom, CELL_SIZE * self.zoom)

            if player == 'X':
                color = X_COLOR
            else:
                color = O_COLOR

            font_size = int(0.9 * CELL_SIZE * self.zoom)
            font = pygame.font.SysFont(None, max(font_size, 1))
            img = font.render(player, True, color)

            self.screen.blit(img, (sx + 5 * self.zoom, sy + 5 * self.zoom))

            if (x, y) == self.latest_move:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, rect, 2)

    def update_move(self, x, y, player):
        self.board[(x, y)] = player
        self.latest_move = (x, y)

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
                    sys.exit()
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

    def close(self):
        pygame.quit()
