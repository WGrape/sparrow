#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="prompthub"

cd $service_name/
if ! docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_OFFICIAL_PROMPTHUB_NAME=${IMAGE_OFFICIAL_PROMPTHUB_NAME} \
  --build-arg IMAGE_OFFICIAL_PROMPTHUB_VERSION=${IMAGE_OFFICIAL_PROMPTHUB_VERSION} \
  \
  -f ./make_basic_image/Dockerfile \
  -t sparrow-basic-$service_name:${IMAGE_BASIC_PROMPTHUB_VERSION} . ; then
    print_error "build image failed"
    exit 1
fi

cd ../
