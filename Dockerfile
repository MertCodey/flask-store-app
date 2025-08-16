FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Don’t rely on .flaskenv; set it here so Flask always sees it.
ENV FLASK_APP=app:create_app
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

CMD ["flask", "run"]

