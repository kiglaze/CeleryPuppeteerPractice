# enqueue.py
from celery import group
from celery_app import run_puppeteer

if __name__ == "__main__":
    urls = ["https://google.com", "https://facebook.com", "https://youtube.com", "https://ncsu.edu", "https://github.com"]

    # Option A: fire-and-forget
    for i, u in enumerate(urls):
        run_puppeteer.delay(u)

    # Option B: parallel group (and optionally wait)
    # job = group(run_puppeteer.s(u, i) for i, u in enumerate(urls))()
    # results = job.get(disable_sync_subtasks=False)  # blocks until all finish
    # print(results)
