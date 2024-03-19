ARG FROM_PLATFORM
ARG IMAGE_BASIC_KIBANA_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-kibana:${IMAGE_BASIC_KIBANA_VERSION}

COPY ./templates/kibana.yml /usr/share/kibana/config/kibana.yml

ARG DOCKER_HOST_IP
ARG ELASTICSEARCH_HOST_HTTP_PORT
RUN sed -i "s/DOCKER_HOST_IP/${DOCKER_HOST_IP}/g" /usr/share/kibana/config/kibana.yml
RUN sed -i "s/ELASTICSEARCH_HOST_HTTP_PORT/${ELASTICSEARCH_HOST_HTTP_PORT}/g" /usr/share/kibana/config/kibana.yml

CMD ["/usr/local/bin/kibana-docker"]
