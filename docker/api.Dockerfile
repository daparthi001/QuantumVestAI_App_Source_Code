FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
CMD ["uvicorn", "ai_stock_platform.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
