#Step 1 (Builder)
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

#Step 2 (Final)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--graceful-timeout", "10", "app:app"]
