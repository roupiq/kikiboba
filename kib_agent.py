import subprocess
import time
import psutil
from collections import defaultdict
import threading
from visualizer import TicTacToeVisualizer

TIME_LIMIT = 4.0  # seconds
MEMORY_LIMIT_MB = 100

# Generate starting positions for infinite tic tac toe (3x3 board, empty or with one move)
STARTING_POSITIONS = [
    "0 0 X\n1 0 O",
    "0 0 X\n1 1 O",
    "0 0 X\n2 2 O",
    "0 0 X\n2 0 O",
    "0 0 X\n1 0 O\n-1 -1 X",
    "0 0 X\n1 0 O\n-1 0 X",
    "0 0 X\n1 0 O\n0 -1 X",
    "0 0 X\n1 0 O\n1 -1 X",
]  # Empty board


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
        # print('move')
        if render:
            time.sleep(0.001)
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

    # vis.close()
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a bot tournament match or play against one."
    )
    parser.add_argument("--recompile", action="store_true", help="Recompile each bot")
    parser.add_argument("--render", action="store_true", help="Recompile each bot")
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
            else:
                print(f"Compiled {name} -> {out_path}")
    for name, _ in bot_paths.items():
        bot_paths[name] = _.replace(".cpp", "")


if __name__ == "__main__":
    args = parse_args()

    bots = {
        "default": "./bots/default_bot",
        # "better": "./bots/better_bot",
        "o1": "./my_bots/o1",
        # "mcts": "./my_bots/mcts",z
        # "mcts10": "./bots/mcts_bot10",
        # "mcts_clean": "./bots/mcts_clean",
        # "weird": "./bots/weird",

        # "clean mcts": "./bots/mcts_clean",
        # "O(1)": "./bots/o1",
        # Add more if needed
    }

    if args.recompile:
        to_compile = bots.copy()
        to_compile["engine"] = "engine"
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
