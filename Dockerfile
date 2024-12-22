# frontend build

ARG BUILDPLATFORM=${BUILDPLATFORM:-amd64}
FROM --platform=${BUILDPLATFORM} node:18-bullseye-slim AS frontend

LABEL author="dmitriyvasil@gmail.com"

WORKDIR /app/frontend
RUN --mount=type=bind,target=/app/frontend/package.json,src=./frontend/package.json \
    --mount=type=bind,target=/app/frontend/package-lock.json,src=./frontend/package-lock.json \
    npm ci

COPY ./frontend /app/frontend
RUN npm run build

# backend build

FROM python:3.10-slim-bookworm AS backend

LABEL author="dmitriyvasil@gmail.com"

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONPATH="/app/pythonpath" \
    HOME_FOLDER="/app/ecounter" \
    DJANGO_SETTINGS_MODULE=expense_counter.settings

WORKDIR /app
RUN mkdir -p ${PYTHONPATH} static requirements frontend requirements \
    && useradd --user-group -d ${HOME_FOLDER} -m --no-log-init --shell /bin/bash ecounter \
    && apt-get update -qq \
    && chown -R ecounter:ecounter ./* \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=ecounter:ecounter ./LICENSE /app
COPY --chown=ecounter:ecounter ./README.md /app
COPY --chown=ecounter:ecounter ./pyproject.toml /app
COPY --chown=ecounter:ecounter ./frontend/package.json /app/frontend
COPY --chown=ecounter:ecounter ./requirements/base.txt /app/requirements

COPY --chown=ecounter:ecounter ./backend /app/backend
RUN --mount=type=cache,target=/root/.cache/pip \
pip install --upgrade pip \
&& pip install -r requirements/base.txt

COPY --chown=ecounter:ecounter --from=frontend /app/frontend/dist /app/backend/static/js

EXPOSE 3000

COPY --chown=ecounter:ecounter --chmod=755 ./backend/runserver.py /app/backend

CMD ["python", "/app/backend/runserver.py"]
