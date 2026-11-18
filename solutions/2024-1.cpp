// 2024-1 radix conversion (A version) reference solution.
// Required: two overloaded radixConvert functions, plus hand-written
// positional-weight expansion (binary -> decimal) and division-remainder
// (decimal -> binary) algorithms.
#include <iostream>
#include <cstring>

using namespace std;

// Positional weight expansion: binary string -> decimal integer.
int radixConvert(char binaryString[], int len) {
    int value = 0;
    for (int i = 0; i < len; ++i) {
        value = value * 2 + (binaryString[i] - '0');
    }
    return value;
}

// Division-remainder method: decimal integer -> binary string, printed here.
void radixConvert(int n) {
    if (n == 0) {
        cout << 0 << endl;
        return;
    }
    char digits[32];
    int cnt = 0;
    while (n > 0) {
        digits[cnt++] = char('0' + n % 2);
        n /= 2;
    }
    for (int i = cnt - 1; i >= 0; --i) {
        cout << digits[i];
    }
    cout << endl;
}

int main() {
    int M;
    if (!(cin >> M)) {
        return 0;
    }
    for (int i = 0; i < M; ++i) {
        char c;
        if (!(cin >> c)) {
            break;
        }
        if (c == 'B' || c == 'b') {
            char binaryString[64];
            cin >> binaryString;
            int len = (int)strlen(binaryString);
            cout << radixConvert(binaryString, len) << endl;
        } else if (c == 'D' || c == 'd') {
            int n;
            cin >> n;
            radixConvert(n);
        } else {
            // Illegal selector: print the message and exit immediately.
            cout << "Wrong input" << endl;
            return 0;
        }
    }
    return 0;
}
