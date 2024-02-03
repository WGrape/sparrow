#!/bin/sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH && cd ../../
BATH_PATH=$(pwd)

# define this service.
service_name="redis"

print_stage "try to pull/build sparrow-basic-${service_name} $IMAGE_BASIC_REDIS_VERSION"
if pull basic $service_name $IMAGE_BASIC_REDIS_VERSION; then
    print_info "pull success"
elif source "./${service_name}/make_basic_image/run.sh"; then
    print_info "build success"
else
    print_error "pull/build failed"
    exit 1
fi

cd $service_name/
docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_BASIC_REDIS_VERSION=${IMAGE_BASIC_REDIS_VERSION} \
  \
  --build-arg REDIS_PORT=${REDIS_PORT} \
  --build-arg REDIS_CONTAINER_PORT=${REDIS_CONTAINER_PORT} \
  --build-arg REDIS_PASSWORD=${REDIS_PASSWORD} \
  \
  -f ./make_app_image/Dockerfile \
  -t sparrow-app-$service_name:${IMAGE_APP_REDIS_VERSION} .

cd ../
