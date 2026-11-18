// 2024-2 employee statistics (A version) reference solution.
// Required: implement a struct (otherwise score is zero).
// Filter out grade D; sort by net salary desc, then id asc.
#include <iostream>
#include <cstring>
#include <algorithm>
#include <vector>

using namespace std;

struct Employee {
    char id[16];        // 10-digit id, may have leading zeros: keep as string
    char name[40];      // name, at most 30 characters
    char gender;        // F / M
    char grade;         // A / B / C / D
    int baseSalary;     // base salary
    int floatSalary;    // floating salary
};

int netSalary(const Employee &e) {
    return e.baseSalary + e.floatSalary;
}

bool cmp(const Employee &a, const Employee &b) {
    int pa = netSalary(a);
    int pb = netSalary(b);
    if (pa != pb) {
        return pa > pb;                 // higher net salary first
    }
    return strcmp(a.id, b.id) < 0;      // tie: smaller id first
}

int main() {
    int n;
    if (!(cin >> n)) {
        return 0;
    }
    vector<Employee> employees;
    employees.reserve(n > 0 ? n : 1);
    for (int i = 0; i < n; ++i) {
        Employee e;
        cin >> e.id >> e.name >> e.gender >> e.grade
            >> e.baseSalary >> e.floatSalary;
        if (e.grade != 'D') {
            employees.push_back(e);
        }
    }
    sort(employees.begin(), employees.end(), cmp);
    for (size_t i = 0; i < employees.size(); ++i) {
        cout << employees[i].id << ' ' << employees[i].name << ' '
             << employees[i].gender << ' ' << netSalary(employees[i]) << endl;
    }
    return 0;
}
