// 2023 problem 3 (A): overloaded Color2Hex, hand written base conversion
#include <iostream>
#include <cctype>
using namespace std;

// print one byte (0..255) as two lowercase hex digits, hand written
void PrintByte(int x) {
    const char *digits = "0123456789abcdef";
    cout << digits[(x >> 4) & 15] << digits[x & 15];
}

// RGB version: each component is an integer in [0, 255]
void Color2Hex(int r, int g, int b) {
    cout << "#";
    PrintByte(r);
    PrintByte(g);
    PrintByte(b);
    cout << "\n";
}

// CMYK version: each component is a float in [0, 1]
void Color2Hex(float c, float m, float y, float k) {
    int r = (int)(255.0 * (1.0 - c) * (1.0 - k));
    int g = (int)(255.0 * (1.0 - m) * (1.0 - k));
    int b = (int)(255.0 * (1.0 - y) * (1.0 - k));
    Color2Hex(r, g, b);
}

int main() {
    char ch;
    if (!(cin >> ch)) return 0;
    ch = (char)toupper((unsigned char)ch);
    if (ch == 'R') {
        int r, g, b;
        cin >> r >> g >> b;
        if (r < 0 || r > 255 || g < 0 || g > 255 || b < 0 || b > 255) {
            cout << "Wrong Input!\n";
            return 0;
        }
        Color2Hex(r, g, b);
    } else if (ch == 'C') {
        float c, m, y, k;
        cin >> c >> m >> y >> k;
        if (c < 0.0f || c > 1.0f || m < 0.0f || m > 1.0f ||
            y < 0.0f || y > 1.0f || k < 0.0f || k > 1.0f) {
            cout << "Wrong Input!\n";
            return 0;
        }
        Color2Hex(c, m, y, k);
    } else {
        cout << "Wrong Input!\n";
    }
    return 0;
}
