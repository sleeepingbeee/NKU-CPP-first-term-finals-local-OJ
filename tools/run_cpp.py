#!/usr/bin/env python
"""编译并运行一个 .cpp 文件（命令行小工具）。

用法：
  python oj/tools/run_cpp.py a.cpp                # 从标准输入读取程序输入
  python oj/tools/run_cpp.py a.cpp --stdin t.in   # 从文件读取程序输入
  python oj/tools/run_cpp.py a.cpp --input "1 2"  # 直接给输入字符串
  可选：--timeout 5

典型用途：出题时用「参考解 + 输入文件」生成期望输出（.out）。
"""
import argparse
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import judge  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--stdin", dest="stdin_file")
    ap.add_argument("--input", dest="input_text")
    ap.add_argument("--timeout", type=float, default=5.0)
    ap.add_argument("--out", dest="out_file", help="把程序输出写到该文件（LF 换行）")
    ap.add_argument("--show-compile-log", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.src):
        print(f"源文件不存在: {args.src}", file=sys.stderr)
        return 2

    if args.stdin_file:
        with open(args.stdin_file, "r", encoding="utf-8", errors="replace") as f:
            data = f.read()
    elif args.input_text is not None:
        data = args.input_text
    else:
        data = sys.stdin.read()

    tmp = tempfile.mkdtemp(prefix="ojrun_")
    try:
        exe = os.path.join(tmp, "a.exe" if os.name == "nt" else "a.out")
        ok, log = judge.compile_cpp(args.src, exe, workdir=tmp)
        if not ok:
            print("编译失败：", file=sys.stderr)
            print(log, file=sys.stderr)
            return 1
        if args.show_compile_log and log:
            print(log, file=sys.stderr)
        rc, out, err, el = judge.run_exe(exe, data, args.timeout)
        if args.out_file:
            with open(args.out_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(out if out.endswith("\n") else out + "\n")
        sys.stdout.write(out)
        sys.stdout.flush()
        if rc is None:
            print(f"\n[超时 >{args.timeout}s]", file=sys.stderr)
            return 3
        if err and err.strip():
            print(f"\n[stderr] {err}", file=sys.stderr)
        if rc != 0:
            print(f"\n[退出码 {rc}]", file=sys.stderr)
            return 4
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
