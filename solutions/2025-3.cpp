// 2025-3 memory allocation (A version)
// One-dimensional array simulates memory: 0 = free, 1 = allocated (first-fit).
#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    int size;
    if (!(cin >> size)) return 0;
    int n;
    cin >> n;

    vector<int> mem(size, 0);  // 0 = free, 1 = allocated

    for (int k = 0; k < n; ++k) {
        string cmd;
        cin >> cmd;
        if (cmd == "ALLOCATE") {
            int req;
            cin >> req;
            int start = -1;
            int run = 0;
            for (int i = 0; i < size; ++i) {
                if (mem[i] == 0) {
                    ++run;
                    if (run >= req) {
                        start = i - req + 1;
                        break;
                    }
                } else {
                    run = 0;
                }
            }
            if (start < 0) {
                cout << "Allocation failed" << '\n';
            } else {
                for (int i = start; i < start + req; ++i) mem[i] = 1;
                cout << "Allocated at index " << start << '\n';
            }
        } else {  // FREE start length
            int start, len;
            cin >> start >> len;
            bool ok = (start >= 0 && len > 0 && start + len <= size);
            if (ok) {
                for (int i = start; i < start + len; ++i) {
                    if (mem[i] == 0) { ok = false; break; }
                }
            }
            if (!ok) {
                cout << "Invalid free operation" << '\n';
            } else {
                for (int i = start; i < start + len; ++i) mem[i] = 0;
                cout << "Freed " << len << " blocks from index " << start << '\n';
            }
        }
    }
    return 0;
}
