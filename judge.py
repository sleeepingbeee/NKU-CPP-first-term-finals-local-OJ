"""本地评测核心：找编译器 → 编译 → 运行 → 比对。

支持两种工具链：
  1) g++（在 PATH 上，MinGW / MSYS2 等）
  2) MSVC cl.exe（通过 vcvars64.bat 初始化环境），Windows 上最省事的方案

对外接口：
  toolchain()                      -> dict，含 kind / 描述
  compile_cpp(src, exe, workdir)   -> (ok: bool, log: str)
  run_exe(exe, input_text, timeout)-> (rc: int|None, out: str, err: str, elapsed: float)
  normalize(s)                     -> 行尾空白归一化，用于比对
"""
import os
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_BAT = os.path.join(HERE, "build.bat")

# 常见的 vcvars64.bat 位置（找不到自动探测时兜底）
_FALLBACK_VCVARS = [
    r"D:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat",
    r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat",
    r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat",
    r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
]
_VSWHERE = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"

_cache = {}


def _decode(data: bytes) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def _find_vcvars() -> str | None:
    if os.environ.get("OJ_VCVARS") and os.path.isfile(os.environ["OJ_VCVARS"]):
        return os.environ["OJ_VCVARS"]
    if os.path.isfile(_VSWHERE):
        try:
            r = subprocess.run(
                [_VSWHERE, "-latest", "-products", "*",
                 "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                 "-property", "installationPath"],
                capture_output=True, timeout=20,
            )
            for line in _decode(r.stdout).splitlines():
                line = line.strip()
                if not line:
                    continue
                cand = os.path.join(line, "VC", "Auxiliary", "Build", "vcvars64.bat")
                if os.path.isfile(cand):
                    return cand
        except Exception:
            pass
    for cand in _FALLBACK_VCVARS:
        if os.path.isfile(cand):
            return cand
    return None


def toolchain() -> dict:
    """探测可用工具链，结果缓存。"""
    if "tc" in _cache:
        return _cache["tc"]
    tc = {"kind": None, "detail": "", "ok": False}
    gpp = shutil.which("g++") or shutil.which("clang++")
    if gpp:
        tc = {"kind": "gcc", "detail": gpp, "ok": True}
    else:
        vcvars = _find_vcvars()
        if vcvars and os.path.isfile(BUILD_BAT):
            tc = {"kind": "msvc", "detail": vcvars, "ok": True}
        else:
            tc = {"kind": None, "detail": "未找到 g++ 或 MSVC(vcvars64.bat)", "ok": False}
    _cache["tc"] = tc
    return tc


CACHE_DIR = os.path.join(HERE, ".cache")
CACHE_FILE = os.path.join(CACHE_DIR, "toolchain.json")


def _capture_msvc_env(vcvars):
    """用临时 .bat 捕获 vcvars64.bat 设置后的环境变量（vcvars 本身要跑 10 秒，只跑一次）。"""
    tmpdir = tempfile.mkdtemp(prefix="oj_vc_")
    try:
        bat = os.path.join(tmpdir, "capture.bat")
        with open(bat, "w", encoding="ascii", newline="\r\n") as f:
            f.write('@echo off\r\n')
            f.write('call "%s" >nul 2>&1\r\n' % vcvars)
            f.write('set\r\n')
        r = subprocess.run(["cmd", "/c", bat], capture_output=True, timeout=300, cwd=tmpdir)
        env = {}
        for line in _decode(r.stdout).splitlines():
            if not line or line.startswith("=") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k:
                env[k.upper()] = v
        return env
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _msvc_setup():
    """返回 {cl, env}。vcvars 的环境变量缓存到磁盘，之后每次编译只要 ~2 秒。"""
    if "msvc" in _cache:
        return _cache["msvc"]
    vcvars = _find_vcvars()
    setup = None
    if vcvars:
        stamp = str(os.path.getmtime(vcvars))
        try:
            if os.path.isfile(CACHE_FILE):
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if saved.get("stamp") == stamp and os.path.isfile(saved.get("cl", "")):
                    setup = {"cl": saved["cl"], "env": saved["env"]}
        except Exception:
            setup = None
        if setup is None:
            env = _capture_msvc_env(vcvars)
            path = env.get("PATH", "")
            cl = shutil.which("cl.exe", path=path) if path else None
            if cl:
                setup = {"cl": cl, "env": env}
                try:
                    os.makedirs(CACHE_DIR, exist_ok=True)
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump({"stamp": stamp, "cl": cl, "env": env}, f, ensure_ascii=False)
                except Exception:
                    pass
    _cache["msvc"] = setup
    return setup


def compile_cpp(src: str, exe: str, workdir: str | None = None) -> tuple[bool, str]:
    """把 src 编译成 exe。返回 (是否成功, 编译日志)。"""
    tc = toolchain()
    if not tc["ok"]:
        return False, "【环境错误】" + tc["detail"]
    src = os.path.abspath(src)
    exe = os.path.abspath(exe)
    cwd = workdir or os.path.dirname(exe) or HERE
    os.makedirs(cwd, exist_ok=True)
    if tc["kind"] == "gcc":
        cmd = [tc["detail"], "-O2", "-std=c++17", "-o", exe, src, "-lm"]
        try:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            return False, "【编译超时】编译器 120 秒未返回"
        log = _decode(r.stdout) + _decode(r.stderr)
        return (r.returncode == 0 and os.path.isfile(exe)), log.strip()
    else:
        setup = _msvc_setup()
        if setup:
            cmd = [setup["cl"], "/nologo", "/EHsc", "/O2", "/std:c++17",
                   "/utf-8", f"/Fe:{exe}", src]
            try:
                r = subprocess.run(cmd, cwd=cwd, capture_output=True,
                                   timeout=180, env=setup["env"])
            except subprocess.TimeoutExpired:
                return False, "【编译超时】编译器 180 秒未返回"
            log = _decode(r.stdout) + _decode(r.stderr)
            if r.returncode == 0 and os.path.isfile(exe):
                return True, log.strip()
            if "fatal error" not in log and "error" not in log and not os.path.isfile(exe):
                pass  # 落到 build.bat 再试一次
            else:
                return False, log.strip()
        # 兜底：build.bat 内部 call vcvars64.bat 再 cl
        try:
            r = subprocess.run(
                ["cmd", "/c", BUILD_BAT, src, exe],
                cwd=cwd, capture_output=True, timeout=180,
            )
        except subprocess.TimeoutExpired:
            return False, "【编译超时】编译器 180 秒未返回"
        log = _decode(r.stdout) + _decode(r.stderr)
        ok = r.returncode == 0 and os.path.isfile(exe)
        return ok, log.strip()


def run_exe(exe: str, input_text: str, timeout: float = 2.0):
    """运行可执行文件，喂入 input_text。返回 (rc, stdout, stderr, 耗时秒)。"""
    t0 = time.time()
    try:
        r = subprocess.run(
            [os.path.abspath(exe)],
            input=input_text.encode("utf-8"),
            capture_output=True,
            timeout=max(0.2, timeout),
        )
    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - t0
        out = _decode(e.stdout or b"")
        return None, out, "TLE", elapsed
    except OSError as e:
        return -1, "", f"【运行失败】{e}", time.time() - t0
    return r.returncode, _decode(r.stdout), _decode(r.stderr), time.time() - t0


def normalize(s: str) -> str:
    """比对用归一化：统一换行、去掉每行行尾空白、去掉末尾多余空行。"""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in s.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def diff_first(expected: str, actual: str, context: int = 2) -> str:
    """给出第一处差异的可读描述。"""
    e = normalize(expected).split("\n")
    a = normalize(actual).split("\n")
    for i in range(max(len(e), len(a))):
        le = e[i] if i < len(e) else "<缺少该行>"
        la = a[i] if i < len(a) else "<多余行>"
        if le != la:
            start = max(0, i - context)
            seg = []
            for j in range(start, min(max(len(e), len(a)), i + context + 1)):
                mark = ">>" if j == i else "  "
                seg.append(f"{mark} 第{j + 1}行  期望: {e[j] if j < len(e) else '<无>'}"
                           f"   实际: {a[j] if j < len(a) else '<无>'}")
            return "\n".join(seg)
    return ""


if __name__ == "__main__":
    print(toolchain())
