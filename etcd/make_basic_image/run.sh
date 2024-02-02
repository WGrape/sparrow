#!/bin/sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH && cd ../../
BATH_PATH=$(pwd)

# define this service.
service_name="etcd"

cd $service_name/
if ! docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_OFFICIAL_ETCD_NAME=${IMAGE_OFFICIAL_ETCD_NAME} \
  --build-arg IMAGE_OFFICIAL_ETCD_VERSION=${IMAGE_OFFICIAL_ETCD_VERSION} \
  \
  -f ./make_basic_image/Dockerfile \
  -t sparrow-basic-$service_name:${IMAGE_BASIC_ETCD_VERSION} . ; then
    print_error "build image failed"
    exit 1
fi

cd ../