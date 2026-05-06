FROM python:3.10

ENV TZ=America/Sao_Paulo
ENV WORKING_DIR=/app
WORKDIR ${WORKING_DIR}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tzdata curl ca-certificates && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock* README.md ./
ENV UV_PROJECT_ENVIRONMENT=/venv
RUN uv sync --no-dev --frozen

COPY . ${WORKING_DIR}
ENV PYTHONPATH=src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

COPY docker/script/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/venv/bin/python", "src/main.py"]
