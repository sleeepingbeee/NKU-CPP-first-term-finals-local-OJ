// 2025-2 distance between two points (A version)
// Point struct is mandatory. Output the pair of points with MINIMUM distance.
// Special cases: M==1 -> "No Distance!"; repeated points -> "Repeated Points!".
// Ties: print every pair, ordered by index ascending.
#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

struct Point {
    int id;      // 1-based index in input order
    double x;    // horizontal coordinate
    double y;    // vertical coordinate
};

int main() {
    int M;
    if (!(cin >> M)) return 0;

    vector<Point> p(M);
    for (int i = 0; i < M; ++i) {
        p[i].id = i + 1;
        cin >> p[i].x >> p[i].y;
    }

    if (M == 1) {
        cout << "No Distance!" << endl;
        return 0;
    }

    // Repeated points first (distance 0)
    for (int i = 0; i < M; ++i) {
        for (int j = i + 1; j < M; ++j) {
            if (p[i].x == p[j].x && p[i].y == p[j].y) {
                cout << "Repeated Points!" << endl;
                return 0;
            }
        }
    }

    // Compare squared distances to avoid sqrt error
    double best = -1.0;
    for (int i = 0; i < M; ++i) {
        for (int j = i + 1; j < M; ++j) {
            double dx = p[i].x - p[j].x;
            double dy = p[i].y - p[j].y;
            double d = dx * dx + dy * dy;
            if (best < 0 || d < best) best = d;
        }
    }

    const double EPS = 1e-9;
    for (int i = 0; i < M; ++i) {
        for (int j = i + 1; j < M; ++j) {
            double dx = p[i].x - p[j].x;
            double dy = p[i].y - p[j].y;
            double d = dx * dx + dy * dy;
            if (fabs(d - best) <= EPS * (best > 1.0 ? best : 1.0)) {
                cout << p[i].id << ' ' << p[j].id << '\n';
            }
        }
    }
    return 0;
}
