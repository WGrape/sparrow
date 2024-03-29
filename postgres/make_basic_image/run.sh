#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="postgres"

cd $service_name/
docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_OFFICIAL_POSTGRES_NAME=${IMAGE_OFFICIAL_POSTGRES_NAME} \
  --build-arg IMAGE_OFFICIAL_POSTGRES_VERSION=${IMAGE_OFFICIAL_POSTGRES_VERSION} \
  \
  -f ./make_basic_image/Dockerfile \
  -t sparrow-basic-$service_name:${IMAGE_BASIC_POSTGRES_VERSION} .

cd ../
