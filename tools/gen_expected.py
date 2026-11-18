#!/usr/bin/env python
"""用参考解生成某题全部 .out（期望输出）。

用法：
  python -X utf8 oj/tools/gen_expected.py 2024-1
  python -X utf8 oj/tools/gen_expected.py --all
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine  # noqa: E402
import judge  # noqa: E402


def gen_one(pid, force=False):
    sol = os.path.join(engine.SOLUTIONS_DIR, pid + ".cpp")
    tdir = os.path.join(engine.TESTDATA_DIR, pid)
    if not os.path.isfile(sol):
        print(f"[{pid}] 缺少参考解 {sol}")
        return False
    if not os.path.isdir(tdir):
        print(f"[{pid}] 缺少测试目录 {tdir}")
        return False
    ins = sorted([f for f in os.listdir(tdir) if f.endswith(".in")],
                 key=lambda s: int(s[:-3]) if s[:-3].isdigit() else 0)
    if not ins:
        print(f"[{pid}] 没有 .in 文件")
        return False

    prob = engine.load_problem(pid)
    tlimit = max(0.5, prob.get("timeLimitMs", 2000) / 1000.0)
    work = os.path.join(tdir, ".build")
    os.makedirs(work, exist_ok=True)
    exe = os.path.join(work, "ref.exe" if os.name == "nt" else "ref")
    ok, log = judge.compile_cpp(sol, exe, workdir=work)
    if not ok:
        print(f"[{pid}] 参考解编译失败：\n{log}")
        return False

    all_ok = True
    for fn in ins:
        base = fn[:-3]
        inp = os.path.join(tdir, fn)
        outp = os.path.join(tdir, base + ".out")
        with open(inp, "r", encoding="utf-8", newline="") as f:
            data = f.read()
        rc, out, err, el = judge.run_exe(exe, data, tlimit)
        if rc is None or rc != 0:
            print(f"[{pid}] {base}.in 运行失败 rc={rc} {err[:200]}")
            all_ok = False
            continue
        if not out.strip():
            print(f"[{pid}] {base}.in 输出为空（检查输入格式与参考解）")
            all_ok = False
        with open(outp, "w", encoding="utf-8", newline="\n") as f:
            f.write(out if out.endswith("\n") else out + "\n")
        print(f"[{pid}] {base}.out  OK  {el * 1000:.0f}ms  输出 {len(out.splitlines())} 行")
    return all_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if args.all:
        ids = engine.problem_ids()
        bad = [pid for pid in ids if not gen_one(pid)]
        print("全部生成失败：" if bad else "全部生成完成。", bad or "")
        return 0 if not bad else 1
    if not args.pid:
        ap.error("需要题号，或 --all")
    return 0 if gen_one(args.pid) else 1


if __name__ == "__main__":
    sys.exit(main())
