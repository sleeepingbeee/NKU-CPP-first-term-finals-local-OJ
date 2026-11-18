// 2023 problem 4 (A): structs point / line / rect, parallel lines, rect overlap area
#include <iostream>
#include <algorithm>
using namespace std;
typedef long long ll;

struct point {
    ll x, y;
};

struct line {
    point a, b;
};

struct rect {
    point a, b;   // a = lower-left corner, b = upper-right corner
};

int main() {
    line l1, l2;
    rect r1, r2;
    cin >> l1.a.x >> l1.a.y >> l1.b.x >> l1.b.y;
    cin >> l2.a.x >> l2.a.y >> l2.b.x >> l2.b.y;
    cin >> r1.a.x >> r1.a.y >> r1.b.x >> r1.b.y;
    cin >> r2.a.x >> r2.a.y >> r2.b.x >> r2.b.y;

    // cross product == 0  <=>  the two lines are parallel
    ll dx1 = l1.a.x - l1.b.x, dy1 = l1.a.y - l1.b.y;
    ll dx2 = l2.a.x - l2.b.x, dy2 = l2.a.y - l2.b.y;
    if (dx1 * dy2 - dy1 * dx2 == 0) cout << "True\n";
    else cout << "False\n";

    // strict overlap on both axes; touching by a corner or an edge is not overlapping
    ll lx = max(min(r1.a.x, r1.b.x), min(r2.a.x, r2.b.x));
    ll rx = min(max(r1.a.x, r1.b.x), max(r2.a.x, r2.b.x));
    ll ly = max(min(r1.a.y, r1.b.y), min(r2.a.y, r2.b.y));
    ll ry = min(max(r1.a.y, r1.b.y), max(r2.a.y, r2.b.y));
    if (rx > lx && ry > ly) cout << (rx - lx) * (ry - ly) << "\n";
    else cout << "False\n";
    return 0;
}
