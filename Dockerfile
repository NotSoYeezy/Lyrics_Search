FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt /app/
COPY sshd_config /etc/ssh/
COPY entrypoint.sh /entrypoint.sh


RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    gcc \
    build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && echo "root:Docker!" | chpasswd \
    && ssh-keygen -A \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && chmod +x /entrypoint.sh


COPY web_app/ /app/web_app/
COPY search_engine/ /app/search_engine/

EXPOSE 5000 2222

ENTRYPOINT ["/entrypoint.sh"]