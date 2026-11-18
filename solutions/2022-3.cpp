// 2022 B卷 第3题 比赛评分
// Requirement: create a struct for each contestant; no STL (no sort/vector), write selection sort by hand.
#include <iostream>
using namespace std;

struct Student {
    char name[32];
    int score;
};

int main() {
    int n;
    if (!(cin >> n)) return 0;

    Student stu[105];
    for (int i = 0; i < n; ++i) {
        cin >> stu[i].name;
        int sum = 0, mx = -1, mn = 101;
        for (int j = 0; j < 7; ++j) {
            int x;
            cin >> x;
            sum += x;
            if (x > mx) mx = x;
            if (x < mn) mn = x;
        }
        stu[i].score = sum - mx - mn;
    }

    // Selection sort: ascending by score, swap the whole struct (name included).
    for (int i = 0; i < n; ++i) {
        int p = i;
        for (int j = i + 1; j < n; ++j) {
            if (stu[j].score < stu[p].score) p = j;
        }
        if (p != i) {
            Student tmp = stu[i];
            stu[i] = stu[p];
            stu[p] = tmp;
        }
    }

    for (int i = 0; i < n; ++i) {
        cout << stu[i].name << ' ' << stu[i].score << '\n';
    }
    return 0;
}
