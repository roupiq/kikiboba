#include <bits/stdc++.h>
#include "../wypisywanie.h"
#include "interface.h"

using namespace std;
using pii = pair<int, int>;
#define all(x) x.begin(), x.end()
#define len(x) (int)x.size()
#define LOG(x) cerr << #x << ": " << x << "\n";

pii operator+(const pii &a, const pii &b)
{
    return {a.first + b.first, a.second + b.second};
}
pii operator*(const pii &a, int b)
{
    return {a.first * b, a.second * b};
}
pii operator-(const pii &a)
{
    return {-a.first, -a.second};
}

const int WIN_LENGTH = 5;
const pii DIRECTIONS[4] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}}; // horiz, vert, diag1, diag2
const pii NEIGHBOURS[8] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}, {0, -1}, {-1, 0}, {-1, -1}, {-1, 1}};

template <typename T1, typename T2>
struct MapWithRerolls
{
    map<T1, T2> mapa;
    vector<pair<T1, T2>> updates;
    vector<int> snapshots;

    T2 get(T1 idx)
    {
        return mapa[idx];
    }
    void update(T1 idx, T2 value)
    {
        updates.push_back({idx, mapa[idx]});
        return mapa[idx] = value;
    }
    void snapshot()
    {
        snapshots.push_back(updates.size());
    }
    void reroll_last()
    {
        while (snapshots.back() < updates.size())
        {
            auto [idx, value] = updates.back();
            mapa[idx] = value;
        }
    }
};

struct Game
{
    map<pii, char> chboard;
    map<pii, int> lengths[2][4];

    size_t size() const
    {
        return chboard.size();
    }
    bool move(pii pos, char player)
    {
        chboard[pos] = player;
        int player_idx = (player == 'X' ? 0 : 1);

        for (int d = 0; d < 4; ++d)
        {
            pii dir = DIRECTIONS[d];
            int len1 = lengths[player_idx][d][pos + dir];
            int len2 = lengths[player_idx][d][pos + -dir];
            int total = len1 + 1 + len2;

            lengths[player_idx][d][pos + dir * len1] = total;
            lengths[player_idx][d][pos + -dir * len2] = total;
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
        for (const auto &[p, c] : chboard)
        {
            min_x = min(min_x, p.first);
            max_x = max(max_x, p.first);
            min_y = min(min_y, p.second);
            max_y = max(max_y, p.second);
        }
        if (chboard.empty())
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
                auto it = chboard.find({x, y});
                if (it == chboard.end())
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
        chboard.clear();
        for (int i = 0; i < 2; i++)
            for (int d = 0; d < 4; d++)
                lengths[i][d].clear();
    }
} game;

mt19937 ran;

pair<int, int> nextMove()
{
    if (game.size() == 0UL)
        return {0, 0};

    set<pii> dist1moves;
    for (auto [p, c] : game.chboard)
    {
        for (auto d : NEIGHBOURS)
        {
            if (!game.chboard.count(p + d))
                dist1moves.insert(p + d);
        }
    }

    vector<pair<array<int, 8>, pii>> pozycje;
    for (auto pos : dist1moves)
    {
        array<int, 8> lengths;
        for (int i = 0; i < 4; i++)
        {
            lengths[i] = game.lengths[0][i][pos + DIRECTIONS[i]] + game.lengths[0][i][pos + -DIRECTIONS[i]];
            lengths[4 + i] = game.lengths[1][i][pos + DIRECTIONS[i]] + game.lengths[1][i][pos + -DIRECTIONS[i]];
        }
        sort(all(lengths));
        reverse(all(lengths));
        pozycje.push_back({lengths, pos});
    }
    sort(all(pozycje));

    // cerr << pozycje << "\n";
    return pozycje[len(pozycje) - 1].second;
}

int main()
{
    string line;

    char player = loadInitialState(game),
         opponent = player ^ 'X' ^ 'O';

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
