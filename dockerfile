FROM python:3.13-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.13-slim

RUN useradd -m appuser \
 && mkdir /app \
 && chown -R appuser:appuser /app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --chown=appuser:appuser . .

RUN mkdir -p /app/logs \
 && chown -R appuser:appuser /app/logs \
 && mkdir -p /var/log/django \
 && chown -R appuser:appuser /var/log/django

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "natour.wsgi:application"]
