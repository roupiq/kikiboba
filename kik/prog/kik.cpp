#include <bits/stdc++.h>
#include "interface.h"

using namespace std;
using pii = pair<int, int>;

pii operator+(const pii &a, const pii &b) { return {a.first + b.first, a.second + b.second}; }
pii operator*(const pii &a, int b) { return {a.first * b, a.second * b}; }
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
            if (lengths[player_idx][d][pos] == WIN_LENGTH)
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

pair<int, int> nextMove()
{
    // If none of the tiles are placed return {0, 0}
    if (game.size() == 0UL)
        return {0, 0};

    // Find candidates
    set<pii> candidates;
    for (auto [p, c] : game.board)
    {
        for (auto d : NEIGHBOURS)
        {
            if (!game.board.count(p + d))
                candidates.insert(p + d);
        }
    }

    // return random candidate
    return vector<pii>(candidates.begin(), candidates.end())[ran() % candidates.size()];
}

int main()
{
    string line;

    // Load initial state of the game
    auto [player, moves] = loadInitialState();
    char opponent = player ^ 'X' ^ 'O';

    for(auto [move, p] : moves)
        game.move(move, p);

    
    while (true)
    {
        // choose next move
        auto [mx, my] = nextMove();
        submitMove(mx, my);

        game.move({mx, my}, player);

        game.move(readOpponentMove(), opponent);
    }
}
