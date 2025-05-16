FROM python:3.10-slim

WORKDIR /app

COPY src/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src/ /app/

CMD ["python", "/app/server.py"]
