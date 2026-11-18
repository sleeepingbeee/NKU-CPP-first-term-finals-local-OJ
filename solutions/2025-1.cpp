// 2025-1 simple calculation (A version)
// Line 1: 10 integers -> print max then min.
// Line 2: 10 letters -> convert lowercase to uppercase.
#include <iostream>
using namespace std;

int main() {
    int a[10];
    for (int i = 0; i < 10; ++i) cin >> a[i];

    int mx = a[0], mn = a[0];
    for (int i = 1; i < 10; ++i) {
        if (a[i] > mx) mx = a[i];
        if (a[i] < mn) mn = a[i];
    }
    cout << mx << ' ' << mn << '\n';

    char c[10];
    for (int i = 0; i < 10; ++i) cin >> c[i];
    for (int i = 0; i < 10; ++i) {
        if (c[i] >= 'a' && c[i] <= 'z') c[i] = char(c[i] - 'a' + 'A');
        if (i) cout << ' ';
        cout << c[i];
    }
    cout << '\n';
    return 0;
}
