#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="etcdkeeper"

cd $service_name/
if ! docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_OFFICIAL_ETCDKEEPER_NAME=${IMAGE_OFFICIAL_ETCDKEEPER_NAME} \
  --build-arg IMAGE_OFFICIAL_ETCDKEEPER_VERSION=${IMAGE_OFFICIAL_ETCDKEEPER_VERSION} \
  \
  -f ./make_basic_image/Dockerfile \
  -t sparrow-basic-$service_name:${IMAGE_BASIC_ETCDKEEPER_VERSION} . ; then
    print_error "build image failed"
    exit 1
fi

cd ../
