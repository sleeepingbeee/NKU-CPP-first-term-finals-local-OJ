// 2023 problem 5: binary search on answer + interval coverage (ASCII only for MSVC cp936)
#include <cstdio>
#include <algorithm>
#include <cmath>
using namespace std;

int t;
double n, p1, v1, p2, v2;
double s1, s2, rg, lf;

// Can the whole street [0, n] be swept within T seconds?
bool check(double T) {
    s1 = T * v1;   // max distance person 1 can walk within T
    s2 = T * v2;   // max distance person 2 can walk within T

    // person 1 alone covers the whole street
    if (s1 >= p1 + n || s1 >= n * 2 - p1) return true;
    // person 2 alone covers the whole street
    if (s2 >= p2 + n || s2 >= n * 2 - p2) return true;
    // they walk towards each other and cross: p1 reaches n and p2 reaches 0
    if (s1 >= n - p1 && s2 >= p2) return true;

    // otherwise person 1 takes the left part [0, x] and person 2 the right part [x, n]
    // so person 1 must reach 0 and person 2 must reach n
    if (s1 < p1 || s2 < n - p2) return false;

    // farthest point to the right person 1 can cover after sweeping up to 0
    rg = max(p1 + max(0.0, s1 - 2 * p1), p1 + (s1 - p1) / 2.0);
    // leftmost point person 2 can cover after sweeping up to n (mirror the street)
    lf = min(p2 - max(0.0, s2 - 2 * (n - p2)), p2 - (s2 - (n - p2)) / 2.0);
    return rg >= lf;
}

int main() {
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        scanf("%lf %lf %lf %lf %lf", &n, &p1, &v1, &p2, &v2);
        if (p1 > p2) {          // keep p1 <= p2 for the case analysis
            swap(p1, p2);
            swap(v1, v2);
        }
        double l = 0.0;
        double r = (p1 + n) / v1;  // rough feasible upper bound
        for (int it = 0; it < 100; ++it) {
            double mid = (l + r) / 2.0;
            if (check(mid)) r = mid;
            else l = mid;
        }
        printf("%.10f\n", r);
    }
    return 0;
}
