#include <iostream>
#include <unordered_map>
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include "wypisywanie.h"

using namespace std;

const int WIN_LENGTH = 5;
const int DIRS[4][2] = {{0,1},{1,0},{1,1},{1,-1}}; // horiz, vert, diag1, diag2

struct pair_hash {
    template <class T1, class T2>
    size_t operator()(const pair<T1, T2>& p) const {
        return p.second + 0x9e3779b9 + (p.first << 6) + (p.first >> 2);
    }
};

struct DSU {
    unordered_map<int, int> parent, size;

    int find(int x) {
        if (!parent.count(x)) {
            parent[x] = x;
            size[x] = 1;
        }
        if (parent[x] != x)
            parent[x] = find(parent[x]);
        return parent[x];
    }

    void unite(int x, int y) {
        int rx = find(x);
        int ry = find(y);
        if (rx == ry) return;
        parent[ry] = rx;
        size[rx] += size[ry];
    }

    int getSize(int x) {
        return size[find(x)];
    }

    void reset() {
        parent.clear();
        size.clear();
    }
};

// unordered_map<pair<int, int>, char, pair_hash> board;
map<pair<int, int>, char> board;
DSU dsuX[4], dsuO[4];

int pos_hash(int x, int y) {
    return ((uint(x) + 1000000) * 2000001 + (uint(y) + 1000000));
}

void reset_game() {
    board.clear();
    for (int d = 0; d < 4; ++d) {
        dsuX[d].reset();
        dsuO[d].reset();
    }
}

bool apply_move(int x, int y, char player, bool &win) {
    if (board[{x, y}]) return false;

    board[{x, y}] = player;
    DSU* dsu_arr = (player == 'X') ? dsuX : dsuO;

    for (int d = 0; d < 4; ++d) {
        int root = pos_hash(x, y);
        dsu_arr[d].find(root);

        for (int dx = -1; dx <= 1; dx += 2) {
            int nx = x + dx * DIRS[d][0];
            int ny = y + dx * DIRS[d][1];
            if (board[{nx, ny}] == player) {
                int neighbor = pos_hash(nx, ny);
                dsu_arr[d].unite(root, neighbor);
            }
        }

        if (dsu_arr[d].getSize(root) >= WIN_LENGTH) {
            win = true;
        }
    }

    return true;
}

int main() {
    string line;
    while (getline(cin, line)) {
        if (line == "RESET") {
            reset_game();
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
