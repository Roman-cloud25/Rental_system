FROM python:3.13-slim

# Set environment variables to disable .pyc generation and force unbuffered console logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# Install system dependencies: GCC compiler, MySQL client libs (libmysqlclient-dev), pkg-config, and cron for backups.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    cron \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY backup.sh /backup.sh
RUN chmod +x /backup.sh

RUN echo "0 2 * * 0 /backup.sh >> /var/log/cron.log 2>&1" | crontab -

ENTRYPOINT ["/entrypoint.sh"]