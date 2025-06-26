FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY . ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8888

CMD ["/bin/sh", "-c", \
    "uvicorn backend.src.app:app --host 0.0.0.0 --port 8080"]