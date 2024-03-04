#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="mysql"

print_stage "try to pull/build sparrow-basic-${service_name} $IMAGE_BASIC_MYSQL_VERSION"
if pull basic $service_name $IMAGE_BASIC_MYSQL_VERSION; then
    print_info "pull success"
elif . "./${service_name}/make_basic_image/run.sh"; then
    print_info "build success"
else
    print_error "pull/build failed"
    exit 1
fi

cd $service_name/
if ! docker build \
  --build-arg FROM_PLATFORM=${FROM_PLATFORM} \
  --build-arg IMAGE_BASIC_MYSQL_VERSION=${IMAGE_BASIC_MYSQL_VERSION} \
  \
  --build-arg MYSQL_USER=${MYSQL_USER} \
  --build-arg MYSQL_PASSWORD=${MYSQL_PASSWORD} \
  --build-arg MYSQL_ROOT_USER=${MYSQL_ROOT_USER} \
  --build-arg MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
  --build-arg MYSQL_DATABASE=${MYSQL_DATABASE} \
  --build-arg MYSQL_CONTAINER_PORT=${MYSQL_CONTAINER_PORT} \
  \
  -f ./make_app_image/Dockerfile \
  -t sparrow-app-$service_name:${IMAGE_APP_MYSQL_VERSION} . ; then
    print_error "build image failed"
    exit 1
fi

cd ../
