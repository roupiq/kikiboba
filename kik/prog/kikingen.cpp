#include "oi.h"
#include <bits/stdc++.h>
using namespace std;

const string task_id = "kik";
using ll = long long;

struct RandomTestCase
{
    int n;
};

struct TestCase
{
    inline static int next_seed = 0xC0FFEE;
    int seed = next_seed++;
    vector<pair<char, pair<int, int>>> ruchy;

    TestCase(vector<pair<char, pair<int, int>>> p_ruchy) : ruchy(p_ruchy) {}
    TestCase(const RandomTestCase &args)
    {
        oi::Random ran(seed);
        set<pair<int, int>> moves;
        for (int i = 0; i < args.n; i++)
        {
            int range = ((int)moves.size() + 1) * 2;
            int x = 0, y = 0;
            do
            {
                x = ran.rand_range(-range, range);
                y = ran.rand_range(-range, range);
            } while (moves.count({x, y}));
            moves.insert({x, y});
            ruchy.push_back({(i % 2 ? 'X' : 'O'), {x, y}});
        }
    }

    friend ostream &operator<<(ostream &os, const TestCase &test)
    {
        for (auto [c, p] : test.ruchy)
        {
            os << p.first << " " << p.second << " " << c << "\n";
        }
        os << "END\n";
        return os;
    }
};

int main()
{
    // pozostałe testy pochodzą z Olimpiady Informatycznej
    vector<vector<TestCase>> test_groups = {
        {
            TestCase{{{'X', {0, 0}}, {'O', {1, 0}}, {'X', {0, 1}}}},
            TestCase{{{'O', {0, 0}}, {'X', {1, 0}}, {'O', {0, 1}}}},
            TestCase{{{'X', {0, 0}}, {'O', {1, 0}}, {'X', {0, -1}}, {'O', {0, -2}}, {'X', {2, 2}}}},
            RandomTestCase{10},
            RandomTestCase{100},
        },
    };

    for (int i = 0; i < ssize(test_groups); ++i)
    {
        const vector<TestCase> &group = test_groups[i];
        const string group_name = to_string(i);

        for (int j = 0; j < ssize(group); ++j)
        {
            const TestCase &test = group[j];
            const string test_name = {(char)('a' + j)};

            const string file_name = task_id + group_name + test_name + ".in";
            fprintf(stderr, "writing %s (seed=%d)\n", file_name.c_str(), test.seed);
            ofstream{file_name} << test;
        }
    }

    return 0;
}