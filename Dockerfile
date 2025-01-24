FROM debian:11-slim AS build
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
RUN poetry config virtualenvs.create false && poetry install
COPY src ./

FROM gcr.io/distroless/python3-debian11 AS runtime
ENV POETRY_VENV=/opt/poetry-venv
COPY --from=build ${POETRY_VENV} ${POETRY_VENV}
WORKDIR /app
COPY --from=build /app /app

ENV PYTHONPATH=/app
ENV PATH="${POETRY_VENV}/bin:${PATH}"

ENTRYPOINT ["python", "src/scp_loc"]
