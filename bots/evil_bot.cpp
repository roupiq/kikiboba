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

pair<long, long> nextMove()
{
    if(ran() % 10 == 0)
        return {LONG_MAX, LONG_MAX};
    while (true)
    {
        next_x = (long)(ran() % 10UL);
        next_y = (long)(ran() % 10UL);
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
