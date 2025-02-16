FROM python:3.9-slim AS dev

WORKDIR /app

COPY ./bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "watcher.py"]

FROM dev AS final

COPY ./bot/ ./

CMD ["python", "main.py"]
