FROM python:3.10-slim

WORKDIR /app

COPY src /app/src

WORKDIR /app/src

CMD ["python", "-m", "chat_server", "0.0.0.0"]