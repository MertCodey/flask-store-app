FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app:create_app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

# Run migrations, then start gunicorn (Render sets $PORT)
CMD sh -c "flask db upgrade && gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 120 --factory app:create_app"