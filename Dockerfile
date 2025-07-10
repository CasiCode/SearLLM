FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY . ./

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD [ "uvicorn", "backend.api.app:app", "--host", "127.0.0.1", "--port", "8000" ]