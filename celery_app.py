# celery_app.py
from celery import Celery
import subprocess
import os
import shlex

app = Celery(
    "puppeteer_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

NODE_BIN = "/usr/local/bin/node"  # or: shutil.which("node")
CRAWLER = os.path.join(os.path.dirname(__file__), "crawler.js")

@app.task(acks_late=True, soft_time_limit=180, time_limit=210)
def run_puppeteer(url, uid):
    try:
        # Stream stdout as it runs to avoid large buffers; capture only on error
        proc = subprocess.run(
            [NODE_BIN, CRAWLER, url, str(uid)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=180,                 # hard cap per task
            start_new_session=True,      # isolates the child process group
        )
        return proc.stdout
    except subprocess.CalledProcessError as e:
        return f"[node error] code={e.returncode} stderr={e.stderr.strip()}"
    except subprocess.TimeoutExpired as e:
        return f"[timeout] took>{e.timeout}s; partial_out={e.stdout or ''} partial_err={e.stderr or ''}"
