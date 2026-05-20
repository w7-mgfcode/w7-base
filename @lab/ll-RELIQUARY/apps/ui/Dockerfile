# Multi-stage build: vite → nginx
FROM node:22-alpine AS build

ARG VITE_API_BASE_URL=http://localhost:8282
ARG VITE_GAME_TITLE=Reliquary
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_GAME_TITLE=${VITE_GAME_TITLE}

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY . .
RUN npm run build

# ── Runtime ──────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Run as non-root: nginx-unprivileged user (uid 101 in nginx:alpine)
RUN sed -i 's|listen       80;|listen       8080;|' /etc/nginx/conf.d/default.conf || true

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Allow non-root to write to runtime dirs
RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /usr/share/nginx/html \
 && touch /var/run/nginx.pid \
 && chown nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --retries=4 --start-period=10s \
  CMD wget -qO- http://localhost:8080/ >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
