# JIM-mini (Guardian) backend image — `uvicorn jim.api:app`.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
COPY jim ./jim
RUN pip install .

EXPOSE 8200
CMD ["uvicorn", "jim.api:app", "--host", "0.0.0.0", "--port", "8200"]
