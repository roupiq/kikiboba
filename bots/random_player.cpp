#include <iostream>
#include <string>
#include <set>
#include <utility>
#include <random>
#include "interface.h"

using namespace std;

set<pair<int, int>> taken;
int next_x = 0, next_y = 0;
mt19937 ran;

void reset()
{
    taken.clear();
    next_x = 0;
    next_y = 0;
}

pair<int, int> nextMove()
{
    while (true)
    {
        next_x = (int)(ran() % 10UL);
        next_y = (int)(ran() % 10UL);
        pair<int, int> move = {next_x, next_y};
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
