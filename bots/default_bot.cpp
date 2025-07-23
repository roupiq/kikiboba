#include <bits/stdc++.h>
#include "../wypisywanie.h"
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

    void printBoard() const
    {
        // Find board bounds
        int min_x = INT_MAX, max_x = INT_MIN, min_y = INT_MAX, max_y = INT_MIN;
        for (const auto &[p, c] : board)
        {
            min_x = min(min_x, p.first);
            max_x = max(max_x, p.first);
            min_y = min(min_y, p.second);
            max_y = max(max_y, p.second);
        }
        if (board.empty())
        {
            cerr << "Board is empty.\n";
            return;
        }

        // Add border of two
        min_x -= 2, max_x += 2, min_y -= 2, max_y += 2;

        // Print column indexes (hex, only last char)
        cerr << "  ";
        for (int x = min_x; x <= max_x; ++x)
            cerr << " " << hex << (x & 0xf);
        cerr << dec << "\n";

        // Print top border
        cerr << "  ";
        for (int x = min_x; x <= max_x; ++x)
            cerr << " \033[1;37m#\033[0m";
        cerr << "\n";

        for (int y = min_y; y <= max_y; ++y)
        {
            // Row index (hex, only last char)
            cerr << " " << hex << (y & 0xf) << dec << " ";

            // Left border
            cerr << "\033[1;37m#\033[0m";

            for (int x = min_x + 1; x < max_x; ++x)
            {
                auto it = board.find({x, y});
                if (it == board.end())
                {
                    cerr << " .";
                }
                else
                {
                    char c = it->second;
                    if (c == 'X')
                        cerr << " \033[1;31mX\033[0m";
                    else if (c == 'O')
                        cerr << " \033[1;34mO\033[0m";
                    else
                        cerr << " " << c;
                }
            }

            // Right border
            cerr << " \033[1;37m#\033[0m";
            cerr << "\n";
        }

        // Print bottom border
        cerr << "  ";
        for (int x = min_x; x <= max_x; ++x)
            cerr << " \033[1;37m#\033[0m";
        cerr << "\n";
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

    
    game.printBoard();
    while (true)
    {
        // choose next move
        auto [mx, my] = nextMove();
        submitMove(mx, my);

        game.move({mx, my}, player);
        game.printBoard();

        game.move(readOpponentMove(), opponent);
        game.printBoard();
    }
}
