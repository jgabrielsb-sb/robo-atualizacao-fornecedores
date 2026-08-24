FROM python:3.10

ENV TZ=America/Sao_Paulo
ENV WORKING_DIR=/app
WORKDIR ${WORKING_DIR}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tzdata wget unzip ca-certificates curl \
        fonts-liberation libasound2 libnss3 libxss1 libgbm1 xvfb && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb && \
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
