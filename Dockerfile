# JIM-mini (Guardian) as one container: the console built and served by the API.
#
# Two stages so the Node toolchain never ships in the runtime image — only the
# built console does. The result serves the UI at /app and the API on the same
# origin, which is what lets a phone use it with nothing to configure.
#
#   docker build -t jim-mini .
#   docker run -p 8200:8200 -v jim-data:/data \
#     -e JIM_PUBLIC_URL=https://guardian.example.com \
#     -e JIM_SIGNUP_KEY=... jim-mini
#
# See docs/hosting.md before publishing one — this is health data.
#
# The suite end-to-end harness (docker/docker-compose.yml in the qrme repo)
# builds this image and overrides the command, so changes here have to keep
# working there too.

# --- stage 1: build the console ------------------------------------------
FROM node:20-slim AS console
WORKDIR /src
# Copy manifests first so dependency install caches independently of source.
COPY app/package.json app/package-lock.json ./app/
RUN npm --prefix app ci
COPY app/ ./app/
RUN npm --prefix app run build

# --- stage 2: the service ------------------------------------------------
FROM python:3.12-slim AS runtime

# Predictable, unbuffered logs; no .pyc clutter in the layer.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    JIM_DB=/data/jim.db \
    JIM_CONSOLE_DIR=/srv/app/dist \
    JIM_SOURCE_DIR=/srv

WORKDIR /srv
COPY pyproject.toml README.md ./
COPY jim/ ./jim/
# The dev extra is pytest, and it ships on purpose: the assistant's box
# (jim/workroom.py) runs the tests a drafted edit names inside the container,
# on a copy of the tree at /srv — which is why JIM_SOURCE_DIR names it above.
# The package the server runs from is the installed one; the tree at /srv is
# what the box copies.
RUN pip install --no-cache-dir ".[dev]"

# The built console, mounted by the API at /app. JIM_CONSOLE_DIR points at it
# explicitly: the installed package lives in site-packages, so the relative
# path the source tree uses would not find this copy.
COPY --from=console /src/app/dist ./app/dist

# The database lives on a volume, not in the image: a container restart must
# never be a data-loss event, and here that data is someone's health history.
RUN useradd --system --uid 10001 jim \
 && mkdir -p /data && chown -R jim:jim /data /srv
USER jim
VOLUME ["/data"]

EXPOSE 8200
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8200/health').status==200 else 1)"

# PORT is honoured for platforms that assign one (Fly, Render, Railway…).
CMD ["sh", "-c", "uvicorn jim.api:app --host 0.0.0.0 --port ${PORT:-8200}"]
