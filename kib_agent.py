import subprocess
import time
import psutil
from collections import defaultdict
import threading
from visualizer import TicTacToeVisualizer

TIME_LIMIT = 1.0  # seconds
MEMORY_LIMIT_MB = 100

def start_bot(path):
    proc = subprocess.Popen(
        [path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )
    return proc, psutil.Process(proc.pid)

def start_engine():
    return subprocess.Popen(
        ["./infinite_ttt"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

def send_to_bot(bot, msg_lines):
    for line in msg_lines:
        bot.stdin.write(line + '\n')
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

def run_match(bot1_path, bot2_path, verbose=True):

    vis = TicTacToeVisualizer()

    bots = [start_bot(bot1_path), start_bot(bot2_path)]
    engine = start_engine()

    players = ['X', 'O']
    last_moves = [None, None]
    turn = 0
    move_history = []

    while True:
        # print('move')
        time.sleep(0.05)
        bot_proc, bot_ps = bots[turn]
        opponent_move = last_moves[turn]

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

        mem_used = bot_ps.memory_info().rss / (1024 ** 2)
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
        vis.update_move(x, y, players[turn])
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

    return winner

def run_tournament(bot_paths):
    results = defaultdict(int)
    bots = list(bot_paths.items())

    for i in range(len(bots)):
        for j in range(i + 1, len(bots)):
            name1, path1 = bots[i]
            name2, path2 = bots[j]

            print(f"\n=== {name1} vs {name2} ===")
            winner = run_match(path1, path2)
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

    players = ['X', 'O']
    human_turn = 0 if human_first else 1
    turn = 0
    last_moves = [None, None]

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

            mem_used = bot_ps.memory_info().rss / (1024 ** 2)
            if mem_used > MEMORY_LIMIT_MB:
                print(f"Bot exceeded memory limit: {mem_used:.1f} MB")
                print("You win!")
                break

        result = validate_move(engine, x, y, players[turn])
        if result.startswith("ERR"):
            if turn == human_turn:
                print("You made an illegal move!")
                print("Bot wins!")
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
    # while vis.
    # vis.close()

if __name__ == "__main__":
    bots = {
        "random": "./bots/random_player",
        "better": "./bots/better_bot",
        "slow": "./bots/slow_bot",
        "oom": "./bots/oom_bot",
        "evil": "./bots/evil_bot",
        # Add more if needed
    }

    mode = input("Choose mode: (1) Tournament  (2) Play vs Bot: ").strip()

    if mode == "1":
        run_tournament(bots)
    elif mode == "2":
        print("Available bots:")
        for name in bots:
            print(f"- {name}")
        selected = input("Enter bot name to play against: ").strip()
        human_first = input("Do you want to go first? (y/n): ").strip().lower() == 'y'
        if selected not in bots:
            print("Invalid bot name.")
        else:
            play_vs_bot(bots[selected], human_first=human_first)
    else:
        print("Invalid mode.")
