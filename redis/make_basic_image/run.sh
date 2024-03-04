#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="redis"

cd $service_name/
docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_OFFICIAL_REDIS_NAME=${IMAGE_OFFICIAL_REDIS_NAME} \
  --build-arg IMAGE_OFFICIAL_REDIS_VERSION=${IMAGE_OFFICIAL_REDIS_VERSION} \
  \
  -f ./make_basic_image/Dockerfile \
  -t sparrow-basic-$service_name:${IMAGE_BASIC_REDIS_VERSION} .

cd ../
