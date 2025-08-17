#include "oi.h"
#include <bits/stdc++.h>
using namespace std;

void endf(const char *msg, int line, int)
{
    cout << "WRONG" << endl;
    cout << "Wiersz " << line << ": " << msg << endl;
    exit(1);
}

int main(int argc, char **argv)
{
    if (argc != 4)
    {
        cerr << "Uruchomienie: " << argv[0] << " in out wzo" << endl;
        return 1;
    }

    ifstream fin(argv[1]);

    std::string line;
    std::set<std::pair<int, int>> moves;
    while (std::getline(fin, line))
    {
        if (line == "END")
            break;

        int x, y;
        char p;
        if (sscanf(line.c_str(), "%d %d %c", &x, &y, &p) == 3)
        {
            moves.insert({x, y});
        }
    }

    oi::Scanner zaw(argv[2], endf, oi::PL);
    const int X = zaw.readInt(INT_MIN, INT_MAX);
    zaw.skipWhitespaces();
    const int Y = zaw.readInt(INT_MIN, INT_MAX);
    zaw.skipWhitespaces();
    zaw.readEof();

    if (moves.count({X, Y}))
    {
        cout << "WRONG\n";
        cout << "Podany ruch nakłada się na poprzednio zaznaczone pola\n";
        exit(1);
    }
    
    long range = (moves.size() + 1) * 100;
    if(abs(X) > range || abs(Y) > range)
    {
        cout << "WRONG\n";
        cout << "Ruch poza zakresem: {" << X << ", " << Y << "}" << "\n";
        exit(1);
    }

    cout << "OK\n";
    // cout << "comment\n";
    // cout << "100\n";  // % of points
    return 0;
}
