ARG FROM_PLATFORM
ARG IMAGE_BASIC_SSDB_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-ssdb:${IMAGE_BASIC_SSDB_VERSION}

# Not Found File Error: RUN cp ./templates/ssdb.conf /ssdb/conf/ssdb.conf
COPY ./templates/ssdb.conf /ssdb/conf/ssdb.conf

CMD ["/bin/sh", "-c", "/ssdb/ssdb-server /ssdb/conf/ssdb.conf"]
