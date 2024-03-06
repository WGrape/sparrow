#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="mongodb"

print_stage "try to pull/build sparrow-basic-${service_name} $IMAGE_BASIC_MONGODB_VERSION"
if pull basic $service_name $IMAGE_BASIC_MONGODB_VERSION; then
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
  --build-arg IMAGE_BASIC_MONGODB_VERSION=${IMAGE_BASIC_MONGODB_VERSION} \
  \
  --build-arg MONGODB_INITDB_ROOT_USERNAME=${MONGODB_INITDB_ROOT_USERNAME} \
  --build-arg MONGODB_INITDB_ROOT_PASSWORD=${MONGODB_INITDB_ROOT_PASSWORD} \
  -f ./make_app_image/Dockerfile \
  -t sparrow-app-$service_name:${IMAGE_APP_MONGODB_VERSION} . ; then
    print_error "build image failed"
    exit 1
fi

cd ../
