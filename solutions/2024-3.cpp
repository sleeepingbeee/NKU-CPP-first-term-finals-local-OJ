// 2024-3 black/white grid (A version) reference solution.
// 0 = white, 1 = black. Enumerate all 4x4 sub-rectangles.
#include <iostream>
#include <vector>

using namespace std;

int main() {
    int n, m;
    if (!(cin >> n >> m)) {
        return 0;
    }
    vector<vector<int> > a(n, vector<int>(m));
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            cin >> a[i][j];
        }
    }
    for (int i = 0; i + 3 < n; ++i) {
        for (int j = 0; j + 3 < m; ++j) {
            bool ok = true;
            // Row 1 and row 4 of the sub-rectangle: all white (0).
            for (int c = 0; c < 4 && ok; ++c) {
                if (a[i][j + c] != 0 || a[i + 3][j + c] != 0) {
                    ok = false;
                }
            }
            // Rows 2 and 3: only columns 1 and 4 are white,
            // the two middle cells are black (1).
            for (int r = 1; r <= 2 && ok; ++r) {
                if (a[i + r][j] != 0 || a[i + r][j + 3] != 0) {
                    ok = false;
                }
                if (a[i + r][j + 1] != 1 || a[i + r][j + 2] != 1) {
                    ok = false;
                }
            }
            if (ok) {
                cout << "Yes" << endl;
                return 0;
            }
        }
    }
    cout << "No" << endl;
    return 0;
}
