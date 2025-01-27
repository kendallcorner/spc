FROM python:3.12-slim AS build
ARG POETRY_VERSION=1.3.2
ENV POETRY_VENV=/opt/poetry-venv

RUN apt-get update && \
  apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  python3 -m venv "${POETRY_VENV}" \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install "poetry==${POETRY_VERSION}"

ENV PATH="${PATH}:${POETRY_VENV}/bin"
WORKDIR /app
COPY poetry.lock pyproject.toml ./
COPY src /app/src
RUN poetry config virtualenvs.create false && poetry install

# FROM python:3.12-alpine3.21 AS runtime
# COPY --from=build /usr/local/lib/python3.12 /usr/local/lib/python3.12
# COPY --from=build /usr/local/bin/python3 /usr/local/bin/python3
# COPY --from=build ${POETRY_VENV} ${POETRY_VENV}
# WORKDIR /app
# COPY --from=build /app /app

ENV PYTHONPATH=/app
ENV PATH="${POETRY_VENV}/bin:${PATH}"

CMD ["python", "src/spc_loc"]
