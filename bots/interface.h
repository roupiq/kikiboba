#pragma once
#include <iostream>
#include <string>
#include <utility>

// Submit your move to the game engine
inline void submitMove(int x, int y) {
    std::cout << x << " " << y << std::endl;
}

// Reads previous moves and applies them to the game
pair<char, vector<pair<pair<int, int>, char>>> loadInitialState() {
    static char player = 'X'; // X moves first

    std::string line;
    vector<pair<pair<int, int>, char>> moves;
    while (std::getline(std::cin, line)) {
        if (line == "END") break;

        int x, y;
        char p;
        if (sscanf(line.c_str(), "%d %d %c", &x, &y, &p) == 3) {
            moves.push_back({{x, y}, p});
            player = p ^ 'X' ^ 'O'; // toggle between 'X' and 'O'
        }
    }
    return {player, moves};
}

// Waits for the opponent's move from stdin
inline std::pair<int, int> readOpponentMove() {
    std::string line;
    while (std::getline(std::cin, line)) {
        int x, y;
        if (sscanf(line.c_str(), "%d %d", &x, &y) == 2) {
            return {x, y};
        }
    }
    throw std::runtime_error("Opponent move not received.");
}


/*
Egzample game between you and your bot:
// Initial State
<< 0 0 X
<< 1 0 O
<< END
// Bots turn, you play as O.
// Bot plays (0, 1) 
>> 0 1
// You play (2, 0) 
<< 2 0
// Bot plays (0, 2) 
>> 0 2
// You play (4, 6) 
<< 4 6
// Bot plays (0, 3) 
>> 0 3
// You play (2, 1) 
<< 2 1
// Bot plays (0, 4) 
>> 0 4
// Bot won

*/