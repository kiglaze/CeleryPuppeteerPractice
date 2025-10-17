#

## Steps
install puppeteer with npm install
```bash
npm install puppeteer
```
install requirements.txt file
```bash
pip install -r requirements.txt
```

## Commands to run Celery
Run redis server (make sure redis-server is installed)
```bash
redis-server
```
To run the Celery worker, use the following command:
```bash
celery -A celery_app worker -l info --concurrency=4 --pool=prefork
```

Run all urls:
```bash
python enqueue.py
```
