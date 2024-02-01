ARG FROM_PLATFORM
ARG IMAGE_BASIC_NGINX_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-nginx:${IMAGE_BASIC_NGINX_VERSION}

ARG NGINX_APK_CHINA_SOURCE=false
RUN if [ ${NGINX_APK_CHINA_SOURCE} = true ]; then \
    # this source may cause some errors.
    # sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    # so use this source.
    sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
;fi

RUN apk update \
    && apk upgrade \
    && apk --update add logrotate \
    && apk add --no-cache openssl \
    && apk add --no-cache bash

RUN apk add --no-cache curl

RUN set -x ; \
    addgroup -g 82 -S www-data ; \
    adduser -u 82 -D -S -G www-data www-data && exit 0 ; exit 1

# Create 'messages' file used from 'logrotate'
RUN touch /var/log/messages

# Copy 'logrotate' config file
COPY ./templates/logrotate/nginx /etc/logrotate.d/

# Set upstream conf and remove the default conf
ARG NGINX_PHPFPM_UPSTREAM_CONTAINER
ARG NGINX_PHPFPM_UPSTREAM_PORT
RUN echo "upstream php-upstream { server ${NGINX_PHPFPM_UPSTREAM_CONTAINER}:${NGINX_PHPFPM_UPSTREAM_PORT}; }" > /etc/nginx/conf.d/upstream.conf \
    && rm /etc/nginx/conf.d/default.conf

ARG NGINX_CONTAINER_HTTP_PORT
ENV NGINX_PORT ${NGINX_CONTAINER_HTTP_PORT}

COPY ./templates/startup.sh /opt/startup.sh
RUN sed -i 's/\r//g' /opt/startup.sh

CMD ["/bin/bash", "/opt/startup.sh"]
