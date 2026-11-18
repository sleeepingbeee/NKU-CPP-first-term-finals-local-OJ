// 2023 problem 2 (A): matrix add / subtract / multiply after element rules
#include <iostream>
using namespace std;
typedef long long ll;

const int MAXM = 12;
int m;
ll a[MAXM][MAXM], b[MAXM][MAXM];

bool isPrime(ll x) {
    if (x < 2) return false;
    for (ll i = 2; i * i <= x; ++i)
        if (x % i == 0) return false;
    return true;
}

int main() {
    cin >> m;
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < m; ++j) cin >> a[i][j];
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < m; ++j) cin >> b[i][j];

    // C1 = A + B, every prime element of A and B is increased by 1
    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < m; ++j) {
            ll v = a[i][j] + b[i][j];
            if (isPrime(a[i][j])) ++v;
            if (isPrime(b[i][j])) ++v;
            cout << v << (j + 1 == m ? '\n' : ' ');
        }
    }

    // C2 = A - B, every odd element of A and B is decreased by 1
    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < m; ++j) {
            ll v = a[i][j] - b[i][j] - (a[i][j] & 1) + (b[i][j] & 1);
            cout << v << (j + 1 == m ? '\n' : ' ');
        }
    }

    // C3 = A * B, every even element of A and B is doubled first
    ll A[MAXM][MAXM], B[MAXM][MAXM];
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < m; ++j) {
            A[i][j] = (a[i][j] % 2 == 0) ? a[i][j] * 2 : a[i][j];
            B[i][j] = (b[i][j] % 2 == 0) ? b[i][j] * 2 : b[i][j];
        }
    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < m; ++j) {
            ll v = 0;
            for (int k = 0; k < m; ++k) v += A[i][k] * B[k][j];
            cout << v << (j + 1 == m ? '\n' : ' ');
        }
    }
    return 0;
}
