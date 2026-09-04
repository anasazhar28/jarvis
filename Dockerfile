FROM python:3.12-slim

WORKDIR /app
COPY requirements-web.txt ./
RUN pip install --no-cache-dir -r requirements-web.txt
COPY web_app.py ./
COPY web ./web

ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn web_app:app --host 0.0.0.0 --port ${PORT:-8000}"]
