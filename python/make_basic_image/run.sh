#!/bin/sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH && cd ../../
BATH_PATH=$(pwd)

# define this service.
service_name="python"

cd $service_name/
docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_OFFICIAL_PYTHON_NAME=${IMAGE_OFFICIAL_PYTHON_NAME} \
  --build-arg IMAGE_OFFICIAL_PYTHON_VERSION=${IMAGE_OFFICIAL_PYTHON_VERSION} \
  \
  -f ./make_basic_image/Dockerfile \
  -t sparrow-basic-$service_name:${IMAGE_BASIC_PYTHON_VERSION} .

cd ../
