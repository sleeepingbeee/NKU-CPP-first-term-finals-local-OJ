// 2022 B卷 第1题 提取字母字符串
// 要求：不允许使用 STL（不使用 string / vector / sort），char 数组 + 手写循环
#include <iostream>
using namespace std;

int main() {
    char s[64];
    if (!(cin >> s)) return 0;

    int n = 0;
    while (s[n] != '\0') ++n;

    bool first = true;
    int i = 0;
    while (i < n) {
        bool alpha = (s[i] >= 'a' && s[i] <= 'z') || (s[i] >= 'A' && s[i] <= 'Z');
        if (!alpha) {
            ++i;
            continue;
        }
        int j = i;
        while (j < n && (((s[j] >= 'a') && (s[j] <= 'z')) || ((s[j] >= 'A') && (s[j] <= 'Z')))) ++j;
        if (!first) cout << ' ';
        first = false;
        for (int k = i; k < j; ++k) {
            char c = s[k];
            if (c >= 'A' && c <= 'Z') c = (char)(c - 'A' + 'a');
            cout << c;
        }
        i = j;
    }
    cout << '\n';
    return 0;
}
