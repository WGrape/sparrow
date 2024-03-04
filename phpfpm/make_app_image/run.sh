#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# define this service.
service_name="phpfpm"

print_stage "try to pull/build sparrow-basic-${service_name} $IMAGE_BASIC_PHPFPM_VERSION"
if pull basic $service_name $IMAGE_BASIC_PHPFPM_VERSION; then
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
  --build-arg IMAGE_BASIC_PHPFPM_VERSION=${IMAGE_BASIC_PHPFPM_VERSION} \
  \
  --build-arg PHPFPM_VERSION_MIDLEN=${PHPFPM_VERSION_MIDLEN} \
  --build-arg PHPFPM_VERSION_SMALL=${PHPFPM_VERSION_SMALL} \
  --build-arg PHPFPM_PHP_VERSION=${PHPFPM_PHP_VERSION} \
  \
  --build-arg PHPFPM_PUID=${PHPFPM_PUID} \
  --build-arg PHPFPM_PGID=${PHPFPM_PGID} \
  --build-arg PHPFPM_CONTAINER_PORT=${PHPFPM_CONTAINER_PORT} \
  \
  --build-arg PHPFPM_APT_CHINA_SOURCE=${PHPFPM_APT_CHINA_SOURCE} \
  \
  --build-arg PHPFPM_INSTALL_MCRYPT=${PHPFPM_INSTALL_MCRYPT} \
  --build-arg PHPFPM_INSTALL_BZ2=${PHPFPM_INSTALL_BZ2} \
  --build-arg PHPFPM_INSTALL_GMP=${PHPFPM_INSTALL_GMP} \
  --build-arg PHPFPM_INSTALL_SSH2=${PHPFPM_INSTALL_SSH2} \
  --build-arg PHPFPM_INSTALL_FAKETIME=${PHPFPM_INSTALL_FAKETIME} \
  \
  --build-arg PHPFPM_INSTALL_SOAP=${PHPFPM_INSTALL_SOAP} \
  --build-arg PHPFPM_INSTALL_XSL=${PHPFPM_INSTALL_XSL} \
  --build-arg PHPFPM_INSTALL_PGSQL=${PHPFPM_INSTALL_PGSQL} \
  --build-arg PHPFPM_INSTALL_XDEBUG=${PHPFPM_INSTALL_XDEBUG} \
  --build-arg PHPFPM_CONTAINER_XDEBUG_PORT=${PHPFPM_CONTAINER_XDEBUG_PORT} \
  \
  --build-arg PHPFPM_INSTALL_PCOV=${PHPFPM_INSTALL_PCOV} \
  --build-arg PHPFPM_INSTALL_PHPREDIS=${PHPFPM_INSTALL_PHPREDIS} \
  --build-arg PHPFPM_INSTALL_XHPROF=${PHPFPM_INSTALL_XHPROF} \
  --build-arg PHPFPM_INSTALL_AMQP=${PHPFPM_INSTALL_AMQP} \
  \
  --build-arg PHPFPM_INSTALL_XLSWRITER=${PHPFPM_INSTALL_XLSWRITER} \
  --build-arg PHPFPM_INSTALL_PCNTL=${PHPFPM_INSTALL_PCNTL} \
  --build-arg PHPFPM_INSTALL_BCMATH=${PHPFPM_INSTALL_BCMATH} \
  --build-arg PHPFPM_INSTALL_MEMCACHED=${PHPFPM_INSTALL_MEMCACHED} \
  --build-arg PHPFPM_INSTALL_EXIF=${PHPFPM_INSTALL_EXIF} \
  \
  --build-arg PHPFPM_INSTALL_OPCACHE=${PHPFPM_INSTALL_OPCACHE} \
  --build-arg PHPFPM_INSTALL_MYSQLI=${PHPFPM_INSTALL_MYSQLI} \
  --build-arg PHPFPM_INSTALL_INTL=${PHPFPM_INSTALL_INTL} \
  --build-arg PHPFPM_INSTALL_IMAP=${PHPFPM_INSTALL_IMAP} \
  --build-arg PHPFPM_INSTALL_CALENDAR=${PHPFPM_INSTALL_CALENDAR} \
  \
  --build-arg PHPFPM_INSTALL_APCU=${PHPFPM_INSTALL_APCU} \
  --build-arg PHPFPM_INSTALL_YAML=${PHPFPM_INSTALL_YAML} \
  --build-arg PHPFPM_INSTALL_RDKAFKA=${PHPFPM_INSTALL_RDKAFKA} \
  --build-arg PHPFPM_INSTALL_GETTEXT=${PHPFPM_INSTALL_GETTEXT} \
  --build-arg PHPFPM_INSTALL_MYSQL_CLIENT=${PHPFPM_INSTALL_MYSQL_CLIENT} \
  \
  --build-arg PHPFPM_INSTALL_XMLRPC=${PHPFPM_INSTALL_XMLRPC} \
  --build-arg PHPFPM_INSTALL_PHPDECIMAL=${PHPFPM_INSTALL_PHPDECIMAL} \
  \
  -f ./make_app_image/Dockerfile \
  -t sparrow-app-$service_name:${IMAGE_APP_PHPFPM_VERSION} . ; then
    print_error "build image failed"
    exit 1
fi

cd ../
