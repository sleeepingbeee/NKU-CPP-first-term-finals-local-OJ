#!/usr/bin/env python
"""校验一道题的出题数据是否合规，并用参考解跑一遍。

用法：
  python -X utf8 oj/tools/check_problem.py 2024-1
  python -X utf8 oj/tools/check_problem.py --all
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine  # noqa: E402

REQUIRED = ["id", "year", "no", "title", "difficulty", "tags", "source",
            "timeLimitMs", "checker", "statement", "samples"]


def check(pid):
    errs, warns = [], []
    path = os.path.join(engine.PROBLEMS_DIR, pid + ".json")
    if not os.path.isfile(path):
        return [f"缺少 {path}"], []
    try:
        raw = json.loads(open(path, encoding="utf-8").read())
    except Exception as e:
        return [f"JSON 解析失败：{e}"], []

    for k in REQUIRED:
        if k not in raw:
            errs.append(f"缺少必填字段 {k}")
    if raw.get("id") != pid:
        errs.append(f"id 字段({raw.get('id')}) 与文件名({pid}) 不一致")

    st = raw.get("statement") or ""
    for sec in ("### 题目描述", "### 输入格式", "### 输出格式"):
        if sec not in st:
            warns.append(f"题面里没找到「{sec}」（建议补齐）")
    if len(st) < 200:
        errs.append(f"题面太短（{len(st)} 字符），可能没写完")

    tdir = os.path.join(engine.TESTDATA_DIR, pid)
    ins = []
    if not os.path.isdir(tdir):
        errs.append(f"缺少测试目录 {tdir}")
    else:
        ins = sorted([f for f in os.listdir(tdir) if f.endswith(".in")],
                     key=lambda s: int(s[:-3]) if s[:-3].isdigit() else 0)
        nums = [int(f[:-3]) for f in ins if f[:-3].isdigit()]
        if len(ins) < 6:
            errs.append(f"测试点只有 {len(ins)} 组，要求 >= 6")
        if nums != list(range(1, len(nums) + 1)):
            errs.append(f"测试点编号不连续：{nums}")
        for f in ins:
            outp = os.path.join(tdir, f[:-3] + ".out")
            if not os.path.isfile(outp):
                errs.append(f"缺少 {f[:-3]}.out")
            elif not open(outp, encoding="utf-8").read().strip():
                errs.append(f"{f[:-3]}.out 是空的")

    samples = raw.get("samples") or []
    if not samples:
        errs.append("samples 为空")
    elif ins:
        s0 = samples[0]
        try:
            in0 = open(os.path.join(tdir, "1.in"), encoding="utf-8", newline="").read()
            out0 = open(os.path.join(tdir, "1.out"), encoding="utf-8", newline="").read()
            if engine.judge.normalize(s0.get("input", "")) != engine.judge.normalize(in0):
                errs.append("samples[0].input 与 testdata/1.in 不一致")
            if engine.judge.normalize(s0.get("output", "")) != engine.judge.normalize(out0):
                errs.append("samples[0].output 与 testdata/1.out 不一致")
        except OSError as e:
            errs.append(f"读取样例失败：{e}")

    sol = os.path.join(engine.SOLUTIONS_DIR, pid + ".cpp")
    if not os.path.isfile(sol):
        errs.append(f"缺少参考解 {sol}")
    else:
        res = engine.judge_code(pid, open(sol, encoding="utf-8").read())
        if res["verdict"] == "CE":
            errs.append("参考解编译失败：\n" + res["compileLog"][:1500])
        elif not res["ok"]:
            errs.append(f"参考解没能通过自己的数据：{res['verdict']} "
                        f"（{res['passed']}/{res['total']}），首个失败点 {res.get('firstFail', {}).get('no')}\n"
                        + (res.get("firstFail", {}).get("detail") or "")[:800])
        for c in res["checks"]:
            if c["fatal"] and not c["ok"]:
                warns.append(f"参考解自己没通过硬性检查「{c['name']}」（正则可能写得不对）")
    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", nargs="?")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    ids = engine.problem_ids() if args.all else [args.pid]
    if not ids or ids == [None]:
        ap.error("需要题号或 --all")
    bad = 0
    for pid in ids:
        errs, warns = check(pid)
        if errs:
            bad += 1
            print(f"❌ {pid}")
            for e in errs:
                print("   - " + str(e).replace("\n", "\n     "))
        else:
            print(f"✅ {pid}")
        for w in warns:
            print("   ⚠ " + w)
    if args.all:
        print(f"\n合计 {len(ids)} 题，{bad} 题有问题。")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
