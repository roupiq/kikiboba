import sys
import copy

CELL_SIZE = 40
GRID_COLOR = (250, 250, 250)
X_COLOR = (255, 100, 100)
O_COLOR = (100, 100, 255)
BG_COLOR = (10, 10, 30)

WINDOW_SIZE = 800


class TicTacToeVisualizer:
    def __init__(self):
        try:
            import pygame
            self.pygame = pygame
        except:
            print("To run game with render enabled install pygame: https://www.pygame.org/news")
            exit(1)

        self.pygame.init()
        self.window = self.pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE), pygame.RESIZABLE | pygame.SCALED)
        self.pygame.display.set_caption("Infinite Tic Tac Toe")
        self.base_surface = self.pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))

        self.clock = self.pygame.time.Clock()
        self.board = {}
        self.zoom = 1.0
        self.target_zoom = 1.0
        # self.target_offset_x = win_w // 2 - int(center_x * CELL_SIZE * self.target_zoom)
        # self.target_offset_y = win_h // 2 - int(center_y * CELL_SIZE * self.target_zoom)
        self.offset_x = WINDOW_SIZE // 2 - int(0 * CELL_SIZE * self.target_zoom)
        self.offset_y = WINDOW_SIZE // 2 - int(0 * CELL_SIZE * self.target_zoom)
        self.target_offset_x = self.offset_x
        self.target_offset_y = self.offset_y

        self.recent_moves = []
        self.history = []
        self.history_index = -1
        self.dragging = False
        self.last_mouse_pos = (0, 0)

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
        self.base_surface.fill(BG_COLOR)

        win_w, win_h = self.window.get_size()
        grid_range_x = int(win_w / (CELL_SIZE * self.zoom)) + 4
        grid_range_y = int(win_h / (CELL_SIZE * self.zoom)) + 4
        start_x = int(-self.offset_x / (CELL_SIZE * self.zoom)) - 2
        start_y = int(-self.offset_y / (CELL_SIZE * self.zoom)) - 2

        for i in range(start_x, start_x + grid_range_x):
            x = round(i * CELL_SIZE * self.zoom + self.offset_x)
            self.pygame.draw.line(self.base_surface, GRID_COLOR, (x, 0), (x, win_h))

        for j in range(start_y, start_y + grid_range_y):
            y = round(j * CELL_SIZE * self.zoom + self.offset_y)
            self.pygame.draw.line(self.base_surface, GRID_COLOR, (0, y), (win_w, y))

        for (x, y), player in board.items():
            sx, sy = self.world_to_screen(x, y)
            rect = self.pygame.Rect(sx, sy, CELL_SIZE * self.zoom, CELL_SIZE * self.zoom)

            color = X_COLOR if player == 'X' else O_COLOR

            if (x, y) in self.recent_moves:
                index = self.recent_moves.index((x, y))
                alpha = int(255 * (0.7 - 0.2 * (3 - index)))
                highlight_surface = self.pygame.Surface((rect.width, rect.height), self.pygame.SRCALPHA)
                highlight_surface.fill((*color, alpha))
                self.base_surface.blit(highlight_surface, rect.topleft)

            font_size = int(0.9 * CELL_SIZE * self.zoom)
            font = self.pygame.font.SysFont(None, max(font_size, 1))
            img = font.render(player, True, color)
            self.base_surface.blit(img, (sx + 5 * self.zoom, sy + 5 * self.zoom))

        # Scale to fit the resized window
        scaled_surface = self.pygame.transform.smoothscale(self.base_surface, self.window.get_size())
        self.window.blit(scaled_surface, (0, 0))

    def update_move(self, x, y, player):
        self.board[(x, y)] = player
        self.recent_moves.append((x, y))
        if len(self.recent_moves) > 4:
            self.recent_moves.pop(0)
        self.history.append(copy.deepcopy(self.board))
        self.history_index = len(self.history) - 1
        self.adjust_view_to_fit()

    def adjust_view_to_fit(self):
        if not self.board:
            return

        xs = [x for (x, _) in self.board]
        ys = [y for (_, y) in self.board]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        board_w = (max_x - min_x + 1) * CELL_SIZE
        board_h = (max_y - min_y + 1) * CELL_SIZE

        win_w, win_h = self.window.get_size()
        zoom_x = win_w / (board_w * 1.2)
        zoom_y = win_h / (board_h * 1.2)
        self.target_zoom = min(zoom_x, zoom_y, 1.0)

        center_x = (min_x + max_x + 1) / 2
        center_y = (min_y + max_y + 1) / 2
        self.target_offset_x = win_w // 2 - int(center_x * CELL_SIZE * self.target_zoom)
        self.target_offset_y = win_h // 2 - int(center_y * CELL_SIZE * self.target_zoom)

    def interpolate_view(self):
        # Smoothly interpolate zoom and offset
        t = 0.015
        self.zoom += (self.target_zoom - self.zoom) * t
        self.offset_x += (self.target_offset_x - self.offset_x) * t
        self.offset_y += (self.target_offset_y - self.offset_y) * t

    def run_once(self):
        self.interpolate_view()
        self.draw_board()
        self.pygame.display.flip()
        self.clock.tick(60)

    def get_human_move(self):
        while True:
            self.run_once()
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.close()
                elif event.type == self.pygame.VIDEORESIZE:
                    # Only update internal surface
                    self.base_surface = self.pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
                    self.adjust_view_to_fit()
                elif event.type == self.pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Zoom in
                        self.target_zoom *= 1.1
                    elif event.button == 5:  # Zoom out
                        self.target_zoom /= 1.1
                elif event.type == self.pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        x, y = self.screen_to_world(*event.pos)
                        return x, y

    
    def adjust_view_to_fit_from_board(self, board):
        if not board:
            return

        xs = [x for (x, _) in board]
        ys = [y for (_, y) in board]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        board_w = (max_x - min_x + 1) * CELL_SIZE
        board_h = (max_y - min_y + 1) * CELL_SIZE

        win_w, win_h = self.window.get_size()
        zoom_x = win_w / (board_w * 1.2)
        zoom_y = win_h / (board_h * 1.2)
        self.target_zoom = min(zoom_x, zoom_y, 1.0)

        center_x = (min_x + max_x + 1) / 2
        center_y = (min_y + max_y + 1) / 2
        self.target_offset_x = win_w // 2 - int(center_x * CELL_SIZE * self.target_zoom)
        self.target_offset_y = win_h // 2 - int(center_y * CELL_SIZE * self.target_zoom)


    def wait_utill_quit(self):
        while True:
            self.run_once()
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    return
                elif event.type == self.pygame.VIDEORESIZE:
                    self.base_surface = self.pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
                    self.adjust_view_to_fit()
                elif event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)
                        self.board = copy.deepcopy(self.history[self.history_index])
                        self.adjust_view_to_fit_from_board(self.board)
                    elif event.key == self.pygame.K_RIGHT:
                        self.history_index = min(len(self.history) - 1, self.history_index + 1)
                        self.board = copy.deepcopy(self.history[self.history_index])
                        self.adjust_view_to_fit_from_board(self.board)


    def close(self):
        self.pygame.quit()
