#!/bin/sh

# enter difylocal docker
docker exec -it sparrow_container_test_difylocal /bin/sh

# start api ==============================

# 1. enter directory
cd /var/data/difylocal/dify/api
# 2. copy a env file
cp .env.example .env
# 3. make SECRET_KEY
openssl rand -base64 42
sed -i 's/SECRET_KEY=.*/SECRET_KEY=<your_value>/' .env
# 4. pip install
pip install -r requirements.txt
# 5. database migration
flask db upgrade

# daemon: start server
flask run --host 0.0.0.0 --port=5001 --debug
# daemon: start worker
celery -A app.celery worker -P gevent -c 1 -Q dataset,generation,mail --loglevel INFO

# start web ==============================
cd /var/data/difylocal/dify/web

# 1. enter directory
cd /var/data/difylocal/dify/web
# 2. npm install
npm install
# 3. copy a env file
cp .env.example .env.local
# 4. build your project
npm run build

# daemon: start server
npm run start
