FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["python3", "scripts/webui.py"]
