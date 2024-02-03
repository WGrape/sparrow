ARG FROM_PLATFORM
ARG IMAGE_BASIC_REDIS_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-redis:${IMAGE_BASIC_REDIS_VERSION}

ARG REDIS_PASSWORD
COPY ./templates/redis.conf /etc/redis.conf
RUN sed -i "s/REDIS_PASSWORD/${REDIS_PASSWORD}/g" /etc/redis.conf

VOLUME /data

CMD ["redis-server", "/etc/redis.conf"]
