FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

EXPOSE 5000

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
