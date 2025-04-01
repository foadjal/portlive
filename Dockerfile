FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "run:app", "-b", "0.0.0.0:8000", "--workers=4", "--worker-class", "eventlet"]
