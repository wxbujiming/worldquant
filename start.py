"""
启动前后端开发服务器。

用法:
  python start.py          # 启动前后端（前端 hot-reload）
  python start.py --prod   # 仅启动后端（需先 npm run build）
"""

import subprocess
import sys
import os
import signal
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
BACKEND_DIR = WEB_DIR
FRONTEND_DIR = os.path.join(WEB_DIR, "frontend")

# 检测虚拟环境中的 Python
_VENV_PYTHON = None
for _venv_path in [
    os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe"),
    os.path.join(BASE_DIR, ".venv", "bin", "python"),
    os.path.join(BASE_DIR, "venv", "Scripts", "python.exe"),
    os.path.join(BASE_DIR, "venv", "bin", "python"),
]:
    if os.path.isfile(_venv_path):
        _VENV_PYTHON = _venv_path
        break
PYTHON = _VENV_PYTHON or sys.executable


def start_dev():
    procs = []

    # 启动后端 (FastAPI + reload)
    backend = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR,
    )
    procs.append(backend)
    print(f"[后端] 启动 http://localhost:8000 (PID={backend.pid})")

    # 启动前端 (Vite dev server)
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True,
    )
    procs.append(frontend)
    print(f"[前端] 启动 http://localhost:5173 (PID={frontend.pid})")
    print("按 Ctrl+C 停止所有服务")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        for p in procs:
            p.terminate()
        for p in procs:
            p.wait()
        print("已停止")


def start_prod():
    print("启动生产模式（仅后端，需先 npm run build）...")
    proc = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8000"],
        cwd=BACKEND_DIR,
    )
    print(f"[后端] 启动 http://localhost:8000 (PID={proc.pid})")
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
        print("已停止")


if __name__ == "__main__":
    if "--prod" in sys.argv:
        start_prod()
    else:
        start_dev()
