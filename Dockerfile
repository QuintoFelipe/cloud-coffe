# ——— Builder stage ———
FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ——— Final stage ———
FROM python:3.10-slim
WORKDIR /app

# copy dependencies
COPY --from=builder /install /usr/local

# copy source
COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
