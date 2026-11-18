// 2022 B卷 第2题 矩阵加密
// 要求：不允许使用 STL（不使用 string / vector 等），二维 char 数组 + 手写循环
#include <iostream>
using namespace std;

int main() {
    int m, n;
    if (!(cin >> m >> n)) return 0;

    char c[16][16];
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < n; ++j)
            cin >> c[i][j];

    long long k[16][16];
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < n; ++j)
            cin >> k[i][j];

    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < n; ++j) {
            long long off = k[i][j] % 26;
            long long x = (c[i][j] - 'a') + off;
            x %= 26;
            if (x < 0) x += 26;
            cout << (char)('a' + x);
            if (j + 1 < n) cout << ' ';
        }
        cout << '\n';
    }
    return 0;
}
