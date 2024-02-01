ARG FROM_PLATFORM
ARG IMAGE_BASIC_ETCDKEEPER_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-etcdkeeper:${IMAGE_BASIC_ETCDKEEPER_VERSION}

RUN sed -i -e 's/http:/https:/' /etc/apk/repositories \
    && apk update \
    && apk add curl \
    && apk add bash
