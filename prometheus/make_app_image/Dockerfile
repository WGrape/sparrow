ARG FROM_PLATFORM
ARG IMAGE_BASIC_PROMETHEUS_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-prometheus:${IMAGE_BASIC_PROMETHEUS_VERSION}

# https://hub.docker.com/r/prom/prometheus

COPY ./templates/prometheus.yml /etc/prometheus/prometheus.yml
