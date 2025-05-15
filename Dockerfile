FROM python:3.10
WORKDIR /app
ENV PYTHONPATH=/app
COPY requirements.txt /app/requirements.txt
COPY entrypoint.sh /entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install psycopg2-binary
COPY . /app
EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]

