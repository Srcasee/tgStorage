FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY docker-entrypoint.sh /usr/local/bin/tgstorage-entrypoint.sh

RUN chmod +x /usr/local/bin/tgstorage-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/tgstorage-entrypoint.sh"]
