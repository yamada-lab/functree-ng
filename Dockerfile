FROM python:3.11-slim

# System deps for CairoSVG and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
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

WORKDIR /app/

# Copy requirements first so this layer is only rebuilt when deps change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package files and install frontend deps + build assets
COPY package.json yarn.lock* .babelrc ./
RUN yarn run install-depends \
    && yarn run install-devDepends \
    && true  # deps installed; build happens after app code is copied

# Copy application code after deps are installed
COPY . .

# Build frontend assets (CSS + JS) into functree/static/dist/
RUN yarn run build

EXPOSE 8080

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
