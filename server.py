#!/usr/bin/env python
"""本地 OJ 后端：把 oj.html 的提交编译运行并判题。

启动：双击 start.bat，或 `python -X utf8 oj/server.py`
浏览器打开后即可做题、提交、看每个测试点的结果。
"""
import argparse
import json
import os
import socket
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine  # noqa: E402
import judge    # noqa: E402

HTML_PATH = os.path.join(HERE, "oj.html")
STATS_PATH = os.path.join(HERE, "submissions.jsonl")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def record_submission(pid, verdict, passed, total, code):
    """把提交记录追加到 submissions.jsonl（不含源码，只留存根）。"""
    try:
        with open(STATS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "id": pid,
                "verdict": verdict,
                "passed": passed,
                "total": total,
                "codeLen": len(code),
            }, ensure_ascii=False) + "\n")
    except OSError:
        pass


class Handler(BaseHTTPRequestHandler):
    server_version = "LocalOJ/1.0"

    def log_message(self, fmt, *args):  # 精简访问日志
        if "/api/" in (self.path or ""):
            log(f"{self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")

    # ------------------------------------------------------------ 工具
    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _err(self, msg, code=400):
        self._json({"error": msg}, code)

    def _body_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return {}
        raw = self.rfile.read(n)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"请求体不是合法 JSON：{e}")

    # ------------------------------------------------------------ GET
    def do_GET(self):
        u = urlparse(self.path)
        path = u.path
        try:
            if path in ("/", "/index.html", "/oj.html"):
                return self._serve_html()
            if path == "/api/problems":
                items = engine.load_all(include_tests=False)
                return self._json({
                    "problems": items,
                    "toolchain": judge.toolchain(),
                })
            if path.startswith("/api/problem/"):
                pid = path[len("/api/problem/"):].strip("/")
                p = engine.load_problem(pid)
                p.pop("tests", None)
                return self._json(p)
            if path.startswith("/api/solution/"):
                pid = path[len("/api/solution/"):].strip("/")
                src = engine.solution_source(pid)
                if src is None:
                    return self._err("该题没有参考解", 404)
                return self._json({"id": pid, "code": src})
            if path == "/api/health":
                return self._json({"ok": True, "toolchain": judge.toolchain(),
                                   "problems": engine.problem_ids()})
            return self._err("Not Found", 404)
        except FileNotFoundError:
            return self._err("题目不存在", 404)
        except Exception as e:
            log(f"ERROR GET {path}: {e!r}")
            return self._err(f"{type(e).__name__}: {e}", 500)

    def _serve_html(self):
        if not os.path.isfile(HTML_PATH):
            return self._send(500, "oj.html 不存在".encode("utf-8"), "text/plain; charset=utf-8")
        with open(HTML_PATH, "rb") as f:
            data = f.read()
        self._send(200, data, "text/html; charset=utf-8")

    # ------------------------------------------------------------ POST
    def do_POST(self):
        u = urlparse(self.path)
        try:
            if u.path == "/api/submit":
                return self._submit()
            if u.path == "/api/run":
                return self._run()
            if u.path == "/api/check":
                return self._check()
            return self._err("Not Found", 404)
        except ValueError as e:
            return self._err(str(e))
        except Exception as e:
            log(f"ERROR POST {u.path}: {e!r}")
            return self._err(f"{type(e).__name__}: {e}", 500)

    def _submit(self):
        data = self._body_json()
        pid = (data.get("id") or "").strip()
        code = data.get("code") or ""
        if not pid:
            return self._err("缺少题目 id")
        if len(code.strip()) < 10:
            return self._err("代码太短了，先写点东西吧")
        if not os.path.isfile(os.path.join(engine.PROBLEMS_DIR, pid + ".json")):
            return self._err(f"没有这道题：{pid}", 404)
        t0 = time.time()
        log(f"判题开始 {pid}（{len(code)} 字节）")
        res = engine.judge_code(pid, code)
        res["elapsedMs"] = int((time.time() - t0) * 1000)
        record_submission(pid, res["verdict"], res["passed"], res["total"], code)
        log(f"判题结束 {pid}: {res['verdict']} {res['passed']}/{res['total']} "
            f"{res['elapsedMs']}ms")
        return self._json(res)

    def _run(self):
        """自测：用自定义输入跑一遍，不判分。"""
        data = self._body_json()
        code = data.get("code") or ""
        stdin_text = data.get("input") or ""
        if not code.strip():
            return self._err("代码为空")
        import shutil
        import tempfile
        work = tempfile.mkdtemp(prefix="oj_selfrun_")
        try:
            src = os.path.join(work, "main.cpp")
            with open(src, "w", encoding="utf-8", newline="\n") as f:
                f.write(code)
            exe = os.path.join(work, "main.exe" if os.name == "nt" else "main")
            ok, logtext = judge.compile_cpp(src, exe, workdir=work)
            if not ok:
                return self._json({"ok": False, "ce": True, "compileLog": logtext[-4000:]})
            rc, out, err, el = judge.run_exe(exe, stdin_text, 5.0)
            return self._json({
                "ok": rc == 0, "ce": False, "rc": rc,
                "output": out[-8000:], "stderr": (err or "")[-2000:],
                "timeMs": int(el * 1000), "timeout": rc is None,
            })
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def _check(self):
        """只跑静态检查（硬性实现要求），不编译。"""
        data = self._body_json()
        pid = (data.get("id") or "").strip()
        code = data.get("code") or ""
        p = engine.load_problem(pid)
        return self._json({"checks": engine.run_checks(p, code)})


def pick_port(start=18080, tries=60):
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit("找不到可用端口")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    tc = judge.toolchain()
    if not tc["ok"]:
        print("!! 没有找到 C++ 编译器，判题会失败：", tc["detail"])
        print("   装个 MinGW-w64 并确保 g++ 在 PATH 上，或用 OJ_VCVARS 环境变量指定 vcvars64.bat。")
    else:
        print(f"编译器: {tc['kind']}  {tc['detail']}")

    ids = engine.problem_ids()
    print(f"题目数: {len(ids)}  {ids if ids else '（还没有题目数据）'}")

    port = args.port or pick_port()
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError as e:
        print(f"端口 {port} 用不了（{e}），换一个…")
        port = pick_port()
        srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    srv.daemon_threads = True
    print(f"\n  本地 OJ 已启动 → {url}\n  （关掉这个黑窗口即停止服务）\n", flush=True)
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
