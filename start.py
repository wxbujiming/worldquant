"""
启动前后端开发服务器。

用法:
  python start.py          # 启动前后端（前端 hot-reload）
  python start.py --prod   # 仅启动后端（需先 npm run build）
"""

import logging
import subprocess
import sys
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("start")

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
BACKEND_PORT = 8987


def _read_vite_port() -> int:
    """从 vite.config.ts 中读取端口号。"""
    config_path = os.path.join(FRONTEND_DIR, "vite.config.ts")
    if not os.path.isfile(config_path):
        return 5173  # 默认端口
    try:
        with open(config_path, encoding="utf-8") as f:
            content = f.read()
        m = __import__("re").search(r"port:\s*(\d+)", content)
        return int(m.group(1)) if m else 5173
    except Exception:
        return 5173


FRONTEND_PORT = _read_vite_port()


def free_port(port: int):
    """杀掉占用指定端口的进程（Windows 下用 PowerShell 查杀更可靠）。"""
    try:
        ps_cmd = (
            f"Get-NetTCPConnection -LocalPort {port} -State Listen "
            "| Select-Object -ExpandProperty OwningProcess"
        )
        output = subprocess.check_output(
            ["powershell", "-Command", ps_cmd],
            text=True, timeout=10,
        )
        for line in output.strip().splitlines():
            pid = line.strip()
            if pid.isdigit():
                subprocess.run(
                    ["taskkill", "/F", "/PID", pid],
                    capture_output=True, text=True,
                    timeout=5,
                )
                logger.info(f"已杀掉端口 {port} 上的旧进程 (PID={pid})")
    except subprocess.TimeoutExpired:
        logger.warning(f"释放端口 {port} 超时")
    except subprocess.CalledProcessError:
        pass  # 没有进程占用端口是正常情况
    except Exception as e:
        logger.warning(f"释放端口 {port} 时出错: {e}")


def kill_vite_processes():
    """杀掉残留的 Vite / Node 进程。"""
    try:
        output = subprocess.check_output(
            ["powershell", "-Command",
             "Get-Process node | Select-Object -ExpandProperty Id"],
            text=True, timeout=10,
        )
        for line in output.strip().splitlines():
            pid = line.strip()
            if pid.isdigit():
                subprocess.run(
                    ["taskkill", "/F", "/PID", pid],
                    capture_output=True, text=True, timeout=5,
                )
                logger.info(f"已杀掉残留 Vite/Node 进程 (PID={pid})")
    except subprocess.TimeoutExpired:
        logger.warning("杀 Vite 进程超时")
    except subprocess.CalledProcessError:
        pass  # 没有 Node 进程在跑
    except Exception as e:
        logger.warning(f"杀 Vite 进程时出错: {e}")


def _elapsed(t0: float) -> str:
    return f"{time.time() - t0:.1f}s"


def start_dev():
    procs = []
    t0 = time.time()

    free_port(BACKEND_PORT)
    logger.info(f"启动后端 (FastAPI + reload) ... (已耗时 {_elapsed(t0)})")
    backend = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", str(BACKEND_PORT), "--reload"],
        cwd=BACKEND_DIR,
    )
    procs.append(backend)
    logger.info(f"后端已启动 http://localhost:{BACKEND_PORT} (PID={backend.pid}, 耗时 {_elapsed(t0)})")

    logger.info(f"启动前端 (Vite dev server) ... (已耗时 {_elapsed(t0)})")
    free_port(FRONTEND_PORT)
    kill_vite_processes()
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True,
    )
    procs.append(frontend)
    logger.info(f"前端已启动 http://localhost:{FRONTEND_PORT} (PID={frontend.pid}, 耗时 {_elapsed(t0)})")
    logger.info(f"启动完成，总耗时 {_elapsed(t0)}，按 Ctrl+C 停止所有服务")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("正在关闭服务...")
        for p in procs:
            p.terminate()
        for p in procs:
            p.wait()
        logger.info("已停止")


def start_prod():
    logger.info("启动生产模式（仅后端，需先 npm run build）...")
    t0 = time.time()
    free_port(BACKEND_PORT)
    proc = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
        cwd=BACKEND_DIR,
    )
    logger.info(f"后端已启动 http://localhost:{BACKEND_PORT} (PID={proc.pid}, 耗时 {_elapsed(t0)})")
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
        logger.info("已停止")


if __name__ == "__main__":
    if "--prod" in sys.argv:
        start_prod()
    else:
        start_dev()
