FROM redis/redis-stack:latest

WORKDIR /redis

EXPOSE 6379

COPY . .