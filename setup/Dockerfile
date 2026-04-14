# Full TrustWise stack: Python pipeline + Node/Express UI.
# Example: docker build -t trustwise . && docker run -p 5000:5000 -e HOST=0.0.0.0 trustwise

FROM python:3.11-slim-bookworm

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY setup/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crawl4AI uses Playwright for headless browsing. Download the Chromium
# browser + required OS deps at build time so runtime crawling works.
RUN python -m playwright install --with-deps chromium

COPY web/package.json web/package-lock.json ./web/
RUN cd web && npm ci

COPY . .

RUN cd web && npm run build

ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

EXPOSE 5000

CMD ["sh", "-c", "cd /app/web && node dist/server.js"]
