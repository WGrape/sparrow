ARG FROM_PLATFORM
ARG IMAGE_OFFICIAL_SSDB_NAME
ARG IMAGE_OFFICIAL_SSDB_VERSION
FROM --platform=${FROM_PLATFORM} ${IMAGE_OFFICIAL_SSDB_NAME}:${IMAGE_OFFICIAL_SSDB_VERSION} AS builder

# Not Found File Error: RUN cp ./templates/ssdb.conf /ssdb/conf/ssdb.conf
COPY ./templates/ssdb.conf /ssdb/conf/ssdb.conf

CMD ["/bin/sh", "-c", "/ssdb/ssdb-server /ssdb/conf/ssdb.conf"]
