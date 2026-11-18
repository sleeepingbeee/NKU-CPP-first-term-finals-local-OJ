// 2025-4 encoding conversion (A version)
// Rules:
//  1. Split a positive integer into a sum of distinct powers of 2 and write
//     (exponent) concatenated, exponents from large to small.
//  2. Repeatedly apply the same splitting to every non-zero digit-run still
//     present in the string (a multi-digit number counts as ONE number),
//     until no non-zero digit remains.
//  3. Replace every '0' in the final string by '-'.
// Function overloading is mandatory: the three encoders share one name.
#include <iostream>
#include <string>
#include <cctype>
using namespace std;

// "(e1)(e2)..." with exponents descending
static string binarySplit(long long v) {
    string r;
    for (int i = 62; i >= 0; --i) {
        if ((v >> i) & 1LL) {
            r += '(';
            r += to_string(i);
            r += ')';
        }
    }
    return r;
}

// Replace every non-zero digit-run by its binary split (0 stays as "0")
static string oneStep(const string &s) {
    string r;
    size_t i = 0;
    while (i < s.size()) {
        if (isdigit((unsigned char)s[i])) {
            size_t j = i;
            while (j < s.size() && isdigit((unsigned char)s[j])) ++j;
            string tok = s.substr(i, j - i);
            long long v = 0;
            for (char ch : tok) v = v * 10 + (ch - '0');
            if (v == 0) r += tok;
            else r += binarySplit(v);
            i = j;
        } else {
            r += s[i];
            ++i;
        }
    }
    return r;
}

// Encode: repeat until stable, then map '0' to '-'
static string encodeNumber(long long v) {
    string s = binarySplit(v);
    while (true) {
        string t = oneStep(s);
        if (t == s) break;
        s = t;
    }
    for (char &ch : s) {
        if (ch == '0') ch = '-';
    }
    return s;
}

// Three overloads with the same name
string encode(int n)    { return encodeNumber((long long)n); }
string encode(char c)   { return encodeNumber((long long)(unsigned char)c); }
string encode(double x) { return encodeNumber((long long)x); }

int main() {
    int n;
    char ch;
    double x;
    cin >> n >> ch >> x;

    cout << "Integer encoding result:" << encode(n) << '\n';
    cout << "Character encoding result:" << encode(ch) << '\n';
    cout << "Floating encoding result:" << encode(x) << '\n';
    return 0;
}
