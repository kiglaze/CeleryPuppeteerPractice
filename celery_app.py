# celery_app.py
from celery import Celery
import subprocess
import os
import shlex
import re
import time
import threading
import socket

port_lock = threading.Lock()

app = Celery(
    "puppeteer_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

NODE_BIN = "/usr/local/bin/node"  # or: shutil.which("node")
CRAWLER = os.path.join(os.path.dirname(__file__), "crawler.js")

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

def get_dumpfile(website):
    sanitized_website = sanitize_filename(website)
    return f"{sanitized_website}.dump"

def activate_proxy(website, dumpfile, port_num):
    print(f"Activating proxy for: {website}")
    mitmdump_command = [
        "mitmdump",
        "--listen-port", str(port_num),
        "-w", f"./mitmdumps/{dumpfile}"
    ]

    process = subprocess.Popen(
        mitmdump_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return process

def deactivate_proxy(instance_port):
    print('De-activating proxy...')
    r = subprocess.Popen("kill -9 $(lsof -ti:{})".format(instance_port), shell =True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = r.communicate()

@app.task(acks_late=True, soft_time_limit=180, time_limit=210)
def run_puppeteer(url):
    try:
        with port_lock:
            port_num = get_free_port()
            dumpfile = get_dumpfile(url)
            proxy_process = activate_proxy(url, dumpfile, port_num)

        time.sleep(3)

        # Stream stdout as it runs to avoid large buffers; capture only on error
        proc = subprocess.run(
            [NODE_BIN, CRAWLER, url, str(port_num)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=180,                 # hard cap per task
            start_new_session=True,      # isolates the child process group
        )

        time.sleep(3)

        # Deactivate the proxy
        deactivate_proxy(port_num)
        return proc.stdout
    except subprocess.CalledProcessError as e:
        return f"[node error] code={e.returncode} stderr={e.stderr.strip()}"
    except subprocess.TimeoutExpired as e:
        return f"[timeout] took>{e.timeout}s; partial_out={e.stdout or ''} partial_err={e.stderr or ''}"
    except Exception as e:
        return f"[exception] {str(e)}"
    finally:
        # Ensure the proxy is deactivated in case of any exception
        deactivate_proxy(port_num)
