FROM node:22-bookworm-slim AS frontend
WORKDIR /app/quantum-checkers-ui
COPY quantum-checkers-ui/package*.json ./
RUN npm ci --no-audit --no-fund
COPY quantum-checkers-ui/ ./
RUN npm run build

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY qgame/ ./qgame/
COPY --from=frontend /app/quantum-checkers-ui/build ./quantum-checkers-ui/build
RUN python qgame/manage.py collectstatic --noinput
COPY scripts/start.sh ./scripts/start.sh
RUN chmod +x scripts/start.sh
EXPOSE 8000
CMD ["./scripts/start.sh"]
