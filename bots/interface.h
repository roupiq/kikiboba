#pragma once
#include <iostream>
#include <string>
#include <utility>

// Submit your move to the game engine
inline void submitMove(int x, int y) {
    std::cout << x << " " << y << std::endl;
}

// Reads previous moves and applies them to the game
// T must implement: `bool move(std::pair<int, int>, char)`
template <typename T>
char loadInitialState(T& game) {
    char player = 'X'; // X moves first

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line == "END") break;

        int x, y;
        char p;
        if (sscanf(line.c_str(), "%d %d %c", &x, &y, &p) == 3) {
            game.move({x, y}, p);
            player = p ^ 'X' ^ 'O'; // toggle between 'X' and 'O'
        }
    }
    return player;
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
