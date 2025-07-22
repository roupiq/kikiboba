#include <iostream>
#include <unordered_map>
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include "wypisywanie.h"

using namespace std;
using pii = pair<int, int>;

pii operator+(const pii &a, const pii &b) { return {a.first + b.first, a.second + b.second}; }
pii operator*(const pii &a, int &b) { return {a.first * b, a.second * b}; }
pii operator-(const pii &a) { return {-a.first, -a.second}; }
pii operator-(const pii &a, const pii &b) { return a + -b; }

const int WIN_LENGTH = 5;
const pii DIRECTIONS[4] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}}; // horiz, vert, diag1, diag2
const pii NEIGHBOURS[8] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}, {0, -1}, {-1, 0}, {-1, -1}, {-1, 1}};

struct Game
{
    map<pii, char> board;
    map<pii, int> lengths[2][4];

    size_t size() const
    {
        return board.size();
    }
    bool move(pii pos, char player)
    {
        board[pos] = player;
        int player_idx = (player == 'X' ? 0 : 1);

        for (int d = 0; d < 4; ++d)
        {
            pii dir = DIRECTIONS[d];
            int len1 = lengths[player_idx][d][pos + dir];
            int len2 = lengths[player_idx][d][pos - dir];
            int total = len1 + 1 + len2;

            lengths[player_idx][d][pos + dir * len1] = total;
            lengths[player_idx][d][pos - dir * len2] = total;
            lengths[player_idx][d][pos] = total;
        }

        for (int d = 0; d < 4; ++d)
        {
            if (lengths[player_idx][d][pos] >= WIN_LENGTH)
                return true;
        }
        return false;
    }

    void reset()
    {
        board.clear();
        for (int i = 0; i < 2; i++)
            for (int d = 0; d < 4; d++)
                lengths[i][d].clear();
    }
} game;

mt19937 ran;

bool apply_move(int x, int y, char player, bool &win) {
    if (game.board.contains({x, y})) return false;

    win = game.move({x, y}, player);
    return true;
}

int main() {
    string line;
    while (getline(cin, line)) {
        if (line == "RESET") {
            game.reset();
            cout << "OK RESET\n" << flush;
            continue;
        }

        int x, y;
        char player;
        istringstream iss(line);
        if (!(iss >> x >> y >> player)) {
            cout << "ERR\n" << flush;
            cerr << "Invalid format, got: " << line << ", expected <x> <y> <player>" << flush;
            continue;
        }

        bool win = false;
        bool success = apply_move(x, y, player, win);
        if (!success) {
            cout << "ERR\n" << flush;
            cerr << "Invalid move\n" << flush;
        } else {
            cout << "OK " << (win ? "WIN" : "CONTINUE") << "\n" << flush;
        }
        // cout << board << "\n";
    }

    return 0;
}
