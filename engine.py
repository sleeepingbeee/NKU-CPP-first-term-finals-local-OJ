"""题目加载 + 判题引擎（server.py 与 tools/*.py 共用）。"""
import json
import os
import re
import shutil
import tempfile

import judge

HERE = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_DIR = os.path.join(HERE, "problems")
TESTDATA_DIR = os.path.join(HERE, "testdata")
SOLUTIONS_DIR = os.path.join(HERE, "solutions")

VERDICT_LABEL = {
    "AC": "通过",
    "WA": "答案错误",
    "TLE": "运行超时",
    "RE": "运行时错误",
    "CE": "编译错误",
    "OK": "通过",
}


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def problem_ids():
    if not os.path.isdir(PROBLEMS_DIR):
        return []
    ids = [fn[:-5] for fn in os.listdir(PROBLEMS_DIR) if fn.endswith(".json")]
    return sorted(ids, key=_id_sort_key)


def _id_sort_key(pid):
    m = re.match(r"(\d+)-(\d+)$", pid)
    return (int(m.group(1)), int(m.group(2))) if m else (9999, pid)


def load_problem(pid):
    path = os.path.join(PROBLEMS_DIR, pid + ".json")
    data = json.loads(_read(path))
    data.setdefault("id", pid)
    data.setdefault("timeLimitMs", 2000)
    data.setdefault("checker", "default")
    data.setdefault("checks", [])
    data.setdefault("samples", [])
    data.setdefault("tags", [])
    # 挂上测试点
    tdir = os.path.join(TESTDATA_DIR, pid)
    tests = []
    if os.path.isdir(tdir):
        ins = sorted(
            [fn for fn in os.listdir(tdir) if fn.endswith(".in")],
            key=lambda s: int(s[:-3]) if s[:-3].isdigit() else 0,
        )
        for fn in ins:
            base = fn[:-3]
            out_path = os.path.join(tdir, base + ".out")
            if not os.path.isfile(out_path):
                continue
            tests.append({
                "no": int(base) if base.isdigit() else base,
                "in": _read(os.path.join(tdir, fn)),
                "out": _read(out_path),
            })
    data["tests"] = tests
    data["testCount"] = len(tests)
    sol = os.path.join(SOLUTIONS_DIR, pid + ".cpp")
    data["hasSolution"] = os.path.isfile(sol)
    return data


def load_all(include_tests=False):
    out = []
    for pid in problem_ids():
        try:
            p = load_problem(pid)
        except Exception as e:  # 单题坏了不影响其它题
            out.append({"id": pid, "error": f"{type(e).__name__}: {e}", "title": pid})
            continue
        if not include_tests:
            p = {k: v for k, v in p.items() if k != "tests"}
        out.append(p)
    return out


# ---------------------------------------------------------------- 比对
def _as_float(tok):
    try:
        return float(tok)
    except ValueError:
        return None


def compare(problem, expected, actual):
    """返回 (是否一致, 差异说明)。"""
    if problem.get("checker") == "float":
        eps = float(problem.get("eps", 1e-5))
        e_toks = expected.split()
        a_toks = actual.split()
        if len(e_toks) != len(a_toks):
            return False, f"输出数字个数不一致：期望 {len(e_toks)} 个，实际 {len(a_toks)} 个"
        for i, (et, at) in enumerate(zip(e_toks, a_toks)):
            ev, av = _as_float(et), _as_float(at)
            if ev is None or av is None:
                if et != at:
                    return False, f"第 {i + 1} 个输出不是数字：期望 {et!r}，实际 {at!r}"
                continue
            if abs(ev - av) > eps and abs(ev - av) > eps * max(abs(ev), 1.0):
                return False, f"第 {i + 1} 个数字超出误差：期望 {et}，实际 {at}（允许误差 {eps}）"
        return True, ""
    ne, na = judge.normalize(expected), judge.normalize(actual)
    if ne == na:
        return True, ""
    return False, judge.diff_first(expected, actual)


def run_checks(problem, source):
    """静态检查（硬性实现要求）。"""
    results = []
    for chk in problem.get("checks") or []:
        pattern = chk.get("pattern", "")
        try:
            matched = re.search(pattern, source) is not None
        except re.error as e:
            results.append({
                "name": chk.get("name", "检查项"), "ok": False, "fatal": bool(chk.get("fatal")),
                "hint": f"检查项正则写错了：{e}",
            })
            continue
        ok = matched if chk.get("kind", "require") == "require" else not matched
        results.append({
            "name": chk.get("name", "检查项"),
            "ok": ok,
            "fatal": bool(chk.get("fatal")),
            "hint": chk.get("hint", ""),
        })
    return results


# ---------------------------------------------------------------- 判题
def judge_code(pid, source, keep_workdir=False):
    problem = load_problem(pid)
    checks = run_checks(problem, source)
    fatal_failed = [c for c in checks if c["fatal"] and not c["ok"]]
    tests = problem["tests"]
    tlimit = max(0.5, problem.get("timeLimitMs", 2000) / 1000.0)

    result = {
        "id": pid,
        "verdict": "",
        "verdictLabel": "",
        "ok": False,
        "passed": 0,
        "total": len(tests),
        "cases": [],
        "compileLog": "",
        "checks": checks,
        "fatalFailed": [c["name"] for c in fatal_failed],
        "elapsedMs": 0,
    }
    if not tests:
        result["verdict"] = "NO_DATA"
        result["verdictLabel"] = "该题还没有测试数据"
        return result

    work = tempfile.mkdtemp(prefix=f"oj_{pid}_")
    try:
        src = os.path.join(work, "main.cpp")
        with open(src, "w", encoding="utf-8", newline="\n") as f:
            f.write(source)
        exe = os.path.join(work, "main.exe" if os.name == "nt" else "main")
        ok, log = judge.compile_cpp(src, exe, workdir=work)
        if not ok:
            result["verdict"] = "CE"
            result["verdictLabel"] = VERDICT_LABEL["CE"]
            result["compileLog"] = log[-4000:]
            return result

        worst = None          # AC < WA < RE < TLE < CE(不参与)
        order = {"AC": 0, "WA": 1, "RE": 2, "TLE": 3}
        first_fail = None
        for t in tests:
            if len(result["cases"]) - result["passed"] >= 5:
                result["earlyStop"] = True
                break
            rc, out, err, el = judge.run_exe(exe, t["in"], tlimit)
            if rc is None:
                st = "TLE"
            elif rc != 0:
                st = "RE"
            else:
                same, _ = compare(problem, t["out"], out)
                st = "AC" if same else "WA"
            if st == "AC":
                result["passed"] += 1
            else:
                if first_fail is None:
                    first_fail = (t, out, err)
                if worst is None or order[st] > order[worst]:
                    worst = st
            result["cases"].append({
                "no": t["no"], "status": st, "timeMs": int(el * 1000),
            })
        result["verdict"] = worst or "AC"
        result["verdictLabel"] = VERDICT_LABEL[result["verdict"]]
        result["ok"] = worst is None
        if first_fail:
            t, out, err = first_fail
            same, detail = compare(problem, t["out"], out)
            result["firstFail"] = {
                "no": t["no"],
                "input": t["in"][:1500],
                "expected": t["out"][:1500],
                "actual": out[:1500],
                "detail": detail[:1500],
                "stderr": (err or "")[:600],
            }
        # 硬性要求未通过时，考场记 0 分
        if fatal_failed:
            result["examScoreZero"] = True
        return result
    finally:
        if keep_workdir:
            print("[workdir]", work)
        else:
            shutil.rmtree(work, ignore_errors=True)


def solution_source(pid):
    path = os.path.join(SOLUTIONS_DIR, pid + ".cpp")
    return _read(path) if os.path.isfile(path) else None


if __name__ == "__main__":
    print("toolchain:", judge.toolchain())
    print("problems:", problem_ids())
    for p in load_all():
        print(f"  {p['id']:<8} {p.get('title', '?'):<20} tests={p.get('testCount')} "
              f"checks={len(p.get('checks') or [])} sol={p.get('hasSolution')}")
