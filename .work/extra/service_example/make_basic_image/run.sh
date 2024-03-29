#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="{{SERVICE}}"

cd $service_name/
if ! docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_OFFICIAL_{{SERVICE_UPPER}}_NAME=${IMAGE_OFFICIAL_{{SERVICE_UPPER}}_NAME} \
  --build-arg IMAGE_OFFICIAL_{{SERVICE_UPPER}}_VERSION=${IMAGE_OFFICIAL_{{SERVICE_UPPER}}_VERSION} \
  \
  -f ./make_basic_image/Dockerfile \
  -t sparrow-basic-$service_name:${IMAGE_BASIC_{{SERVICE_UPPER}}_VERSION} . ; then
    print_error "build image failed"
    exit 1
fi

cd ../
