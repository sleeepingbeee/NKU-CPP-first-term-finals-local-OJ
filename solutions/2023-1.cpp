// 2023 problem 1 (A): max / min / sum of 10 integers, then lowercase the letters
#include <iostream>
#include <string>
#include <climits>
using namespace std;

int main() {
    long long sum = 0;
    int mx = INT_MIN, mn = INT_MAX;
    for (int i = 0; i < 10; ++i) {
        int x;
        if (!(cin >> x)) return 0;
        if (x > mx) mx = x;
        if (x < mn) mn = x;
        sum += x;
    }
    string s;
    cin >> s;
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] >= 'A' && s[i] <= 'Z') s[i] = char(s[i] - 'A' + 'a');
    }
    cout << mx << " " << mn << " " << sum << "\n";
    cout << s << "\n";
    return 0;
}
