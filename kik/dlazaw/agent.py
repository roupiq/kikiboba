import subprocess
import time
import psutil
from collections import defaultdict
import threading


TIME_LIMIT = 0.25  # seconds
MEMORY_LIMIT_MB = 64


# Starting position for tournament
STARTING_POSITIONS = [
    "0 0 X\n1 0 O",
    "0 0 X\n1 1 O",
    "0 0 X\n2 2 O",
    "0 0 X\n2 0 O",
    "0 0 X\n1 0 O\n-1 -1 X",
    "0 0 X\n1 0 O\n-1 0 X",
    "0 0 X\n1 0 O\n0 -1 X",
    "0 0 X\n1 0 O\n1 -1 X",
]

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


def start_bot(path):
    proc = subprocess.Popen(
        [path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    return proc, psutil.Process(proc.pid)


def start_engine():
    return subprocess.Popen(
        ["./engine"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )


def send_to_bot(bot, msg_lines, end=True):
    for line in msg_lines:
        bot.stdin.write(line + "\n")
    if end:
        bot.stdin.write("END\n")
        bot.stdin.flush()


def read_from_bot(bot, time_limit=TIME_LIMIT):
    move = []

    def target():
        try:
            move.append(bot.stdout.readline().strip())
        except:
            move.append(None)

    t0 = time.perf_counter()
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=time_limit)
    t1 = time.perf_counter()

    if thread.is_alive():
        return None, t1 - t0

    return move[0], t1 - t0


def validate_move(engine, x, y, player):
    engine.stdin.write(f"{x} {y} {player}\n")
    engine.stdin.flush()
    response = engine.stdout.readline().strip()
    return response


def run_match(bot1_path, bot2_path, initial_position="", verbose=True, render=True):
    if render:
        vis = TicTacToeVisualizer()
    
    engine = start_engine()
    bots = [start_bot(bot1_path), start_bot(bot2_path)]

    p = "X"
    if initial_position:
        for line in initial_position.strip().split("\n"):
            x, y, p = line.split()

            if render:
                vis.update_move(int(x), int(y), p)
            
            validate_move(engine, x, y, p)


    players = ["X", "O"]
    if p == "X":
        players = ["O", "X"]
        
    last_moves: list = [None, None]
    turn = 0
    move_history = []


    print(initial_position)
    while True:
        if render:
            time.sleep(0.01)

        bot_proc, bot_ps = bots[turn]
        opponent_move = last_moves[turn]

        if last_moves[1-turn] == None:
            input_lines = initial_position.split('\n')
        else:
            input_lines = []
        if opponent_move:
            x, y, p = opponent_move
            input_lines.append(f"{x} {y} {p}")

        send_to_bot(bot_proc, input_lines)

        move_str, elapsed = read_from_bot(bot_proc)
        if move_str is None:
            if verbose:
                print(f"{players[turn]} TIMED OUT!")
            winner = 1 - turn
            break

        try:
            x, y = map(int, move_str.strip().split())
        except:
            if verbose:
                print(f"{players[turn]} returned invalid move: {move_str}")
            winner = 1 - turn
            break

        mem_used = bot_ps.memory_info().rss / (1024**2)
        if mem_used > MEMORY_LIMIT_MB:
            if verbose:
                print(f"{players[turn]} exceeded memory limit: {mem_used:.1f} MB")
            winner = 1 - turn
            break

        result = validate_move(engine, x, y, players[turn])
        if result.startswith("ERR"):
            if verbose:
                print(f"{players[turn]} made illegal move: {x} {y}")
            winner = 1 - turn
            break

        if verbose:
            print(f"{players[turn]} -> {x} {y} | {elapsed:.3f}s | {mem_used:.1f} MB")

        move_history.append((x, y, players[turn]))
        last_moves[1 - turn] = (x, y, players[turn])
        if render:
            vis.update_move(x, y, players[turn])
        if render:
            vis.run_once()

        if result.endswith("WIN"):
            if verbose:
                print(f"{players[turn]} WINS!")
            winner = turn
            break

        turn = 1 - turn

    # Cleanup
    for bot, _ in bots:
        bot.kill()
    engine.kill()

    if render:
        vis.wait_utill_quit()

    return winner


def run_tournament(bot_paths, rounds=10, render=True):
    results = defaultdict(int)
    bots = list(bot_paths.items())

    for i in range(len(bots)):
        for j in range(i + 1, len(bots)):
            for start_pos in STARTING_POSITIONS:
                for k in range(2):
                    if k:
                        name1, path1 = bots[i]
                        name2, path2 = bots[j]
                    else:
                        name1, path1 = bots[j]
                        name2, path2 = bots[i]

                    print(f"\n=== {name1} vs {name2} ===")
                    winner = run_match(path1, path2, start_pos, render, render)
                    if winner == 0:
                        results[name1] += 1
                        print(f"Winner: {name1}")
                    else:
                        results[name2] += 1
                        print(f"Winner: {name2}")

    print("\n=== FINAL SCORES ===")
    for name, score in sorted(results.items(), key=lambda x: -x[1]):
        print(f"{name}: {score}")


def play_vs_bot(bot_path, human_first=True):
    vis = TicTacToeVisualizer()
    bot, bot_ps = start_bot(bot_path)
    engine = start_engine()

    players = ["X", "O"]
    human_turn = 0 if human_first else 1
    turn = 0
    last_moves: list = [None, None]

    while True:
        if turn == human_turn:
            # Human move
            print("Click on the board to make your move.")
            x, y = vis.get_human_move()
        else:
            # Bot move
            input_lines = []
            if last_moves[turn]:
                x_prev, y_prev, p_prev = last_moves[turn]
                input_lines.append(f"{x_prev} {y_prev} {p_prev}")
            send_to_bot(bot, input_lines)

            move_str, elapsed = read_from_bot(bot)
            if move_str is None:
                print("Bot timed out!")
                print("You win!")
                break
            try:
                x, y = map(int, move_str.strip().split())
            except:
                print(f"Bot returned invalid move: {move_str}")
                print("You win!")
                break

            mem_used = bot_ps.memory_info().rss / (1024**2)
            if mem_used > MEMORY_LIMIT_MB:
                print(f"Bot exceeded memory limit: {mem_used:.1f} MB")
                print("You win!")
                break

        result = validate_move(engine, x, y, players[turn])
        if result.startswith("ERR"):
            if turn == human_turn:
                print("You made an illegal move!")
                print("Try Again!")
                continue
            else:
                print("Bot made an illegal move!")
                print("You win!")
            break

        print(f"{players[turn]} -> {x} {y}")
        vis.update_move(x, y, players[turn])
        vis.run_once()

        last_moves[1 - turn] = (x, y, players[turn])

        if result.endswith("WIN"):
            if turn == human_turn:
                print("You win!")
            else:
                print("Bot wins!")
            break

        turn = 1 - turn

    bot.kill()
    engine.kill()

    vis.wait_utill_quit()


import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a bot tournament match or play against one."
    )
    parser.add_argument("--recompile", action="store_true", help="Recompile each bot")
    parser.add_argument("--bots_path", default='bots', help="Path to folder with bots")
    parser.add_argument("--engine_path", default='engine.cpp', help="Path to engine")
    parser.add_argument("--render", action="store_true", help="Render games")

    return parser.parse_args()


def compile_bots(bot_paths):
    for name, _ in bot_paths.items():
        bot_paths[name] = _ + ".cpp"
    for name, path in bot_paths.items():
        if path.endswith(".cpp"):
            print(f"Compiling {name} from {path}...")
            out_path = path.replace(".cpp", "")
            result = subprocess.run(["g++", "-O3", "-std=c++20", "-o", out_path, path])
            if result.returncode != 0:
                print(f"Failed to compile {name} ({path})")
    for name, _ in bot_paths.items():
        bot_paths[name] = _.replace(".cpp", "")


if __name__ == "__main__":
    args = parse_args()

    bots = {}
    if args.bots_path:
        for fname in os.listdir(args.bots_path):
            fpath = os.path.join(args.bots_path, fname)
            print(fpath)
            if fpath[-4:] == '.cpp':
                bots[fname[:-4]] = fpath[:-4]
    
    if args.recompile:
        to_compile = bots.copy()
        to_compile["engine"] = args.engine_path[:-4]
        compile_bots(to_compile)
        print("Bots succesfully compiled!")

    mode = input("Choose mode: (1) Tournament  (2) Play vs Bot: ").strip()

    if mode == "1":
        run_tournament(bots, render=args.render)
    elif mode == "2":
        print("Available bots:")
        for name in bots:
            print(f"- {name}")
        selected = input("Enter bot name to play against: ").strip()
        human_first = input("Do you want to go first? (y/n): ").strip().lower() == "y"
        if selected not in bots:
            print("Invalid bot name.")
        else:
            play_vs_bot(bots[selected], human_first=human_first)
    else:
        print("Invalid mode.")
