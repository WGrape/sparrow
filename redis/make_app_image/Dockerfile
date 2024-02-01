ARG FROM_PLATFORM
ARG IMAGE_BASIC_REDIS_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-redis:${IMAGE_BASIC_REDIS_VERSION}

VOLUME /data

CMD ["redis-server", "/etc/redis.conf"]
