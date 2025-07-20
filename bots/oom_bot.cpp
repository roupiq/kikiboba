#include <iostream>
#include <string>
#include <set>
#include <utility>
#include <random>
#include <limits.h>
#include "interface.h"

using namespace std;

set<pair<long, long>> taken;
long next_x = 0, next_y = 0;
mt19937 ran;

void reset()
{
    taken.clear();
    next_x = 0;
    next_y = 0;
}

vector<vector<long>> LARGE_VECTORS;

pair<long, long> nextMove()
{
    vector<long> LARGE_VECTOR(10'000'000);
    for (int i = 0; i < (int)LARGE_VECTOR.size(); i++)
        LARGE_VECTOR[ran() % LARGE_VECTOR.size()]++;
    LARGE_VECTORS.push_back(LARGE_VECTOR);
        
    while (true)
    {
        next_x = (long)((ran() + LARGE_VECTORS[ran() % LARGE_VECTORS.size()][ran() % LARGE_VECTOR.size()]) % 12UL);
        next_y = (long)(ran() % 12UL);
        pair<long, long> move = {next_x, next_y};
        if (!taken.count(move))
            return move;
    }

}

int main()
{
    string line;

    reset();

    {
        vector<Move> moves = readMoves();
        for (auto m : moves)
        {
            taken.insert({m.x, m.y});
        }
        ran = mt19937(moves.size());
    }

    while (true)
    {
        // choose next move
        auto [mx, my] = nextMove();
        taken.insert({mx, my});
        submitMove(mx, my);
        cout.flush();

        vector<Move> moves = readMoves();
        for (auto m : moves)
        {
            taken.insert({m.x, m.y});
        }
    }
}
