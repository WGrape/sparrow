ARG FROM_PLATFORM
ARG IMAGE_BASIC_MONGODB_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-mongodb:${IMAGE_BASIC_MONGODB_VERSION}

# https://hub.docker.com/_/mongo
ARG MONGODB_INITDB_ROOT_USERNAME
ARG MONGODB_INITDB_ROOT_PASSWORD
ENV MONGO_INITDB_ROOT_USERNAME ${MONGODB_INITDB_ROOT_USERNAME}
ENV MONGO_INITDB_ROOT_PASSWORD ${MONGODB_INITDB_ROOT_PASSWORD}

# https://stackoverflow.com/questions/59274734/where-is-mongodb-config-file-located-when-running-not-as-an-ubuntu-service
# https://stackoverflow.com/questions/34559557/how-to-enable-authentication-on-mongodb-through-docker
# https://stackoverflow.com/questions/4881208/how-to-secure-mongodb-with-username-and-password
# https://stackoverflow.com/questions/37372684/mongodb-3-2-authentication-failed
# https://stackoverflow.com/questions/60394290/mongo-db-docker-image-authentication-failed
# CMD ["mongod"]
CMD ["mongod", "--config", "/etc/mongod.conf"]
