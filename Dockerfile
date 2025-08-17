FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

# Listen on Render’s PORT and use the app factory
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 120 --log-level info --factory app:create_app

