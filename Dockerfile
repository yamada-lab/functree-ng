FROM python:3.11-slim

# System deps for CairoSVG and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libcairo2-dev \
        libffi-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Node.js 20 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Enable corepack for yarn
RUN corepack enable

ADD . /app/
WORKDIR /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
