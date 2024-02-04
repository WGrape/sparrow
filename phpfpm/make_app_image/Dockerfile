#
#--------------------------------------------------------------------------
# Image Setup
#--------------------------------------------------------------------------
#
# To edit the 'php-fpm' base Image, visit its repository on Github
#    https://github.com/Laradock/php-fpm
#
# To change its version, see the available Tags on the Docker Hub:
#    https://hub.docker.com/r/laradock/php-fpm/tags/
#
# Note: Base Image name format {image-tag}-{php-version}
# 20210904 means php 7.3.30, https://hub.docker.com/layers/laradock/php-fpm/20210904-7.3/images/sha256-47c6a2c02cce261d0ddc7762ef2d55239389c4a663e1fbf01fa1bcef91538892?context=explore, you can also assign latest
#

ARG FROM_PLATFORM
ARG IMAGE_BASIC_PHPFPM_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-phpfpm:${IMAGE_BASIC_PHPFPM_VERSION} as base
# ========================================================================>

# Set Environment Variables
ENV DEBIAN_FRONTEND noninteractive

# if you're in China, or you need to change sources, will be set PHPFPM_APT_CHINA_SOURCE to true in /env.
ARG PHPFPM_APT_CHINA_SOURCE
RUN if [ ${PHPFPM_APT_CHINA_SOURCE} = true ]; then \
    # change application source from deb.debian.org to aliyun source
    cp /etc/apt/sources.list /etc/apt/sources.list.bk && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye main\ndeb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye-updates main" > /etc/apt/sources.list \
;fi

# always run apt update when start and after add new source list, then clean up at end.
ARG PHPFPM_VERSION_MIDLEN
RUN set -xe; \
    apt-get update -yqq && \
    pecl channel-update pecl.php.net && \
    apt-get install -yqq \
      apt-utils \
      gnupg2 \
      git \
      #
      #--------------------------------------------------------------------------
      # Mandatory Software's Installation
      #--------------------------------------------------------------------------
      #
      # Mandatory Software's such as ("mcrypt", "pdo_mysql", "libssl-dev", ....)
      # are installed on the base image 'laradock/php-fpm' image. If you want
      # to add more Software's or remove existing one, you need to edit the
      # base image (https://github.com/Laradock/php-fpm).
      #
      # next lines are here because there is no auto build on dockerhub see https://github.com/laradock/laradock/pull/1903#issuecomment-463142846
      libzip-dev zip unzip && \
      if [ ${PHPFPM_VERSION_MIDLEN} = "7.3" ] || [ ${PHPFPM_VERSION_MIDLEN} = "7.4" ] || [ $(php -r "echo PHP_MAJOR_VERSION;") = "8" ]; then \
        docker-php-ext-configure zip; \
      else \
        docker-php-ext-configure zip --with-libzip; \
      fi && \
      # Install the zip extension
      docker-php-ext-install zip && \
      php -m | grep -q 'zip'

#
#--------------------------------------------------------------------------
# Optional Software's Installation
#--------------------------------------------------------------------------
#
# Optional Software's will only be installed if you set them to `true`
# in the `docker-compose.yml` before the build.
# Example:
#   - PHPFPM_INSTALL_SOAP=true
#

# Extension Part 1.
FROM base as extensions_part1
# ========================================================================>

# default install and enable
RUN docker-php-ext-install -j$(nproc) bcmath calendar exif gettext sockets dba mysqli pcntl pdo_mysql shmop sysvmsg sysvsem sysvshm

# Extension Part 2.
FROM extensions_part1 as extensions_part2
# ========================================================================>

###########################################################################
# MCRYPT:
###########################################################################
ARG PHPFPM_INSTALL_MCRYPT
RUN if [ ${PHPFPM_INSTALL_MCRYPT} = true ]; then \
    apt-get update && \
    apt-get install -y --no-install-recommends libmcrypt-dev && \
    rm -r /var/lib/apt/lists/* && \
    pecl install mcrypt-1.0.2 && \
    docker-php-ext-enable mcrypt \
;fi

###########################################################################
# BZ2:
###########################################################################

ARG PHPFPM_INSTALL_BZ2
RUN if [ ${PHPFPM_INSTALL_BZ2} = true ]; then \
  apt-get update && \
  apt-get -yqq install libbz2-dev; \
  docker-php-ext-install bz2 \
;fi

###########################################################################
# GMP (GNU Multiple Precision):
###########################################################################

ARG PHPFPM_INSTALL_GMP
RUN if [ ${PHPFPM_INSTALL_GMP} = true ]; then \
    # Install the GMP extension
	  apt-get install -yqq libgmp-dev && \
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
      ln -s /usr/include/x86_64-linux-gnu/gmp.h /usr/include/gmp.h \
    ;fi && \
    docker-php-ext-install gmp \
;fi

###########################################################################
# SSH2:
###########################################################################

ARG PHPFPM_INSTALL_SSH2
RUN if [ ${PHPFPM_INSTALL_SSH2} = true ]; then \
    # Install the ssh2 extension
    apt-get -y install libssh2-1-dev && \
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
        pecl install -a ssh2-0.13; \
    else \
        pecl install -a ssh2-1.3.1; \
    fi && \
    docker-php-ext-enable ssh2 \
;fi

###########################################################################
# libfaketime:
###########################################################################

USER root
ARG PHPFPM_INSTALL_FAKETIME
RUN if [ ${PHPFPM_INSTALL_FAKETIME} = true ]; then \
    apt-get update && \
    apt-get install -yqq libfaketime \
;fi

# Extension Part 3.
FROM extensions_part2 as extensions_part3
# ========================================================================>

###########################################################################
# SOAP:
###########################################################################

ARG PHPFPM_INSTALL_SOAP
RUN if [ ${PHPFPM_INSTALL_SOAP} = true ]; then \
    # Install the soap extension
    rm /etc/apt/preferences.d/no-debian-php && \
    apt-get -y install libxml2-dev php-soap && \
    docker-php-ext-install soap \
;fi

###########################################################################
# XSL:
###########################################################################

ARG PHPFPM_INSTALL_XSL
RUN if [ ${PHPFPM_INSTALL_XSL} = true ]; then \
    # Install the xsl extension
    apt-get -y install libxslt-dev && \
    docker-php-ext-install xsl \
;fi

###########################################################################
# pgsql
###########################################################################

ARG PHPFPM_INSTALL_PGSQL
RUN if [ ${PHPFPM_INSTALL_PGSQL} = true ]; then \
    # Install the pgsql extension
    docker-php-ext-install pgsql pdo_pgsql \
;fi

###########################################################################
# xDebug:
###########################################################################

ARG PHPFPM_INSTALL_XDEBUG
ARG PHPFPM_CONTAINER_XDEBUG_PORT
RUN if [ ${PHPFPM_INSTALL_XDEBUG} = true ]; then \
  # Install the xdebug extension
  # https://xdebug.org/docs/compat
  if [ $(php -r "echo PHP_MAJOR_VERSION;") = "8" ] || { [ $(php -r "echo PHP_MAJOR_VERSION;") = "7" ] && { [ $(php -r "echo PHP_MINOR_VERSION;") = "4" ] || [ $(php -r "echo PHP_MINOR_VERSION;") = "3" ] ;} ;}; then \
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "8" ]; then \
      pecl install xdebug-3.2.1; \
    else \
      pecl install xdebug-3.1.6; \
    fi; \
  else \
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
      pecl install xdebug-2.5.5; \
    else \
      if [ $(php -r "echo PHP_MINOR_VERSION;") = "0" ]; then \
        pecl install xdebug-2.9.0; \
      else \
        pecl install xdebug-2.9.8; \
      fi \
    fi \
  fi && \
  docker-php-ext-enable xdebug \
;fi

# Copy xdebug configuration for remote debugging
RUN if [ -f /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini ]; then \
    mv /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini /usr/local/etc/php/conf.d/xdebug.ini; \
fi
COPY ./templates/xdebug.ini /usr/local/etc/php/conf.d/xdebug.ini

ARG PHPFPM_CONTAINER_PORT
ARG PHPFPM_CONTAINER_XDEBUG_PORT
RUN if [ $(php -r "echo PHP_MAJOR_VERSION;") = "8" ] || { [ $(php -r "echo PHP_MAJOR_VERSION;") = "7" ] && { [ $(php -r "echo PHP_MINOR_VERSION;") = "4" ] || [ $(php -r "echo PHP_MINOR_VERSION;") = "3" ] ;} ;}; then \
  sed -i "s/xdebug.remote_host=/xdebug.client_host=/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.remote_connect_back=0/xdebug.discover_client_host=false/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.remote_port=${PHPFPM_CONTAINER_PORT}/xdebug.client_port=${PHPFPM_CONTAINER_XDEBUG_PORT}/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.profiler_enable=0/; xdebug.profiler_enable=0/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.profiler_output_dir=/xdebug.output_dir=/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.remote_mode=req/; xdebug.remote_mode=req/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.remote_autostart=0/xdebug.start_with_request=yes/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.remote_enable=0/xdebug.mode=debug/" /usr/local/etc/php/conf.d/xdebug.ini \
;else \
  sed -i "s/xdebug.remote_autostart=0/xdebug.remote_autostart=1/" /usr/local/etc/php/conf.d/xdebug.ini && \
  sed -i "s/xdebug.remote_enable=0/xdebug.remote_enable=1/" /usr/local/etc/php/conf.d/xdebug.ini \
;fi
RUN sed -i "s/xdebug.cli_color=0/xdebug.cli_color=1/" /usr/local/etc/php/conf.d/xdebug.ini

# Extension Part 4.
FROM extensions_part3 as extensions_part4
# ========================================================================>

###########################################################################
# pcov:
###########################################################################

USER root
ARG PHPFPM_INSTALL_PCOV
RUN if [ ${PHPFPM_INSTALL_PCOV} = true ]; then \
  if [ $(php -r "echo PHP_MAJOR_VERSION;") = "8" ]  || { [ $(php -r "echo PHP_MAJOR_VERSION;") = "7" ] && [ $(php -r "echo PHP_MINOR_VERSION;") != "0" ]; }; then \
    pecl install pcov && \
    docker-php-ext-enable pcov \
  ;fi \
;fi

###########################################################################
# PHP REDIS EXTENSION
###########################################################################

ARG PHPFPM_INSTALL_PHPREDIS
RUN if [ ${PHPFPM_INSTALL_PHPREDIS} = true ]; then \
    # Install Php Redis Extension
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
      pecl install -o -f redis-4.3.0; \
    else \
      pecl install -o -f redis; \
    fi \
    && rm -rf /tmp/pear \
    && docker-php-ext-enable redis \
;fi

RUN if [ -f /usr/local/etc/php/conf.d/docker-php-ext-redis.ini ]; then \
    mv /usr/local/etc/php/conf.d/docker-php-ext-redis.ini /usr/local/etc/php/conf.d/05-redis.ini; \
fi

###########################################################################
# Xhprof:
###########################################################################

ARG PHPFPM_INSTALL_XHPROF
RUN set -eux; \
    if [ ${PHPFPM_INSTALL_XHPROF} = true ]; then \
      # Install the php xhprof extension
      if   [ $(php -r "echo PHP_MAJOR_VERSION;") != 5 ]; then \
        pecl install xhprof; \
      else \
        curl -L -o /tmp/xhprof.tar.gz "https://codeload.github.com/phacility/xhprof/tar.gz/master"; \
        mkdir -p /tmp/xhprof; \
        tar -C /tmp/xhprof -zxvf /tmp/xhprof.tar.gz --strip 1; \
        ( \
            cd /tmp/xhprof/extension; \
            phpize; \
            ./configure; \
            make; \
            make install; \
        ); \
        rm -r /tmp/xhprof; \
        rm /tmp/xhprof.tar.gz; \
      fi; \
      docker-php-ext-enable xhprof; \
      php -m | grep -q 'xhprof'; \
    fi

RUN mv /usr/local/etc/php/conf.d/docker-php-ext-xhprof.ini /usr/local/etc/php/conf.d/xhprof.ini
COPY ./templates/xhprof.ini /usr/local/etc/php/conf.d/xhprof.ini

###########################################################################
# AMQP:
###########################################################################

ARG PHPFPM_INSTALL_AMQP
RUN set -eux; \
    if [ ${PHPFPM_INSTALL_AMQP} = true ]; then \
      # # Install the amqp extension
      apt-get -yqq install librabbitmq-dev; \
      if [ $(php -r "echo PHP_MAJOR_VERSION;") = "8" ]; then \
        pecl install amqp-1.11.0beta; \
      else \
        pecl install amqp; \
      fi; \
      docker-php-ext-enable amqp; \
      php -m | grep -oiE '^amqp$'; \
    fi

# Extension Part 5.
FROM extensions_part4 as extensions_part5
# ========================================================================>

###########################################################################
# xlswriter:
###########################################################################

ARG PHPFPM_INSTALL_XLSWRITER
RUN set -eux; \
    if [ ${PHPFPM_INSTALL_XLSWRITER} = true ]; then \
      # Install Php xlswriter Extension \
      if [ $(php -r "echo PHP_MAJOR_VERSION;") != "5" ]; then \
          pecl install xlswriter  &&\
          docker-php-ext-enable xlswriter &&\
          php -m | grep -q 'xlswriter'; \
      else \
          echo "PHP Extension for xlswriter is not supported for PHP 5.0";\
      fi \
    ;fi

###########################################################################
# pcntl
###########################################################################

ARG PHPFPM_INSTALL_PCNTL
RUN if [ ${PHPFPM_INSTALL_PCNTL} = true ]; then \
    # Installs pcntl, helpful for running Horizon
    docker-php-ext-install pcntl \
;fi

###########################################################################
# bcmath:
###########################################################################

ARG PHPFPM_INSTALL_BCMATH
RUN if [ ${PHPFPM_INSTALL_BCMATH} = true ]; then \
    # Install the bcmath extension
    docker-php-ext-install bcmath \
;fi

###########################################################################
# PHP Memcached:
###########################################################################

ARG PHPFPM_INSTALL_MEMCACHED
RUN if [ ${PHPFPM_INSTALL_MEMCACHED} = true ]; then \
    # Install the php memcached extension
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
      echo '' | pecl -q install memcached-2.2.0; \
    else \
      echo '' | pecl -q install memcached; \
    fi \
    && docker-php-ext-enable memcached \
;fi

###########################################################################
# Exif:
###########################################################################

ARG PHPFPM_INSTALL_EXIF
RUN if [ ${PHPFPM_INSTALL_EXIF} = true ]; then \
    # Enable Exif PHP extensions requirements
    docker-php-ext-install exif \
;fi

# Extension Part 6.
FROM extensions_part5 as extensions_part6
# ========================================================================>

###########################################################################
# Opcache:
###########################################################################

ARG PHPFPM_INSTALL_OPCACHE
RUN if [ ${PHPFPM_INSTALL_OPCACHE} = true ]; then \
    docker-php-ext-install opcache \
;fi

# Copy opcache configration
RUN mv /usr/local/etc/php/conf.d/docker-php-ext-opcache.ini /usr/local/etc/php/conf.d/02-opcache.ini

###########################################################################
# Mysqli Modifications:
###########################################################################

ARG PHPFPM_INSTALL_MYSQLI
RUN if [ ${PHPFPM_INSTALL_MYSQLI} = true ]; then \
    docker-php-ext-install mysqli \
;fi

###########################################################################
# Human Language and Character Encoding Support:
###########################################################################

ARG PHPFPM_INSTALL_INTL
RUN if [ ${PHPFPM_INSTALL_INTL} = true ]; then \
    # Install intl and requirements
    apt-get install -yqq zlib1g-dev libicu-dev g++ && \
    docker-php-ext-configure intl && \
    docker-php-ext-install intl \
;fi

###########################################################################
# IMAP:
###########################################################################

ARG PHPFPM_INSTALL_IMAP
RUN if [ ${PHPFPM_INSTALL_IMAP} = true ]; then \
    apt-get install -yqq libc-client-dev libkrb5-dev && \
    docker-php-ext-configure imap --with-kerberos --with-imap-ssl && \
    docker-php-ext-install imap \
;fi

RUN mv /usr/local/etc/php/conf.d/docker-php-ext-imap.ini /usr/local/etc/php/conf.d/04-imap.ini

###########################################################################
# Calendar:
###########################################################################

USER root
ARG PHPFPM_INSTALL_CALENDAR
RUN if [ ${PHPFPM_INSTALL_CALENDAR} = true ]; then \
    docker-php-ext-configure calendar && \
    docker-php-ext-install calendar \
;fi

# Extension Part 7.
FROM extensions_part6 as extensions_part7
# ========================================================================>

###########################################################################
# APCU:
###########################################################################

ARG PHPFPM_INSTALL_APCU
RUN if [ ${PHPFPM_INSTALL_APCU} = true ]; then \
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
        pecl install -a apcu-4.0.11; \
    else \
        pecl install apcu; \
    fi && \
    docker-php-ext-enable apcu \
;fi

###########################################################################
# YAML:
###########################################################################

USER root
ARG PHPFPM_INSTALL_YAML
RUN if [ ${PHPFPM_INSTALL_YAML} = true ]; then \
    apt-get install -yqq libyaml-dev; \
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
        echo '' | pecl install -a yaml-1.3.2; \
    elif [ $(php -r "echo PHP_MAJOR_VERSION;") = "7" ] && [ $(php -r "echo PHP_MINOR_VERSION;") = "0" ]; then \
        echo '' | pecl install yaml-2.0.4; \
    else \
        echo '' | pecl install yaml; \
    fi \
    && docker-php-ext-enable yaml \
;fi

###########################################################################
# RDKAFKA:
###########################################################################

ARG PHPFPM_INSTALL_RDKAFKA
RUN if [ ${PHPFPM_INSTALL_RDKAFKA} = true ]; then \
    apt-get install -yqq librdkafka-dev && \
    pecl install rdkafka && \
    docker-php-ext-enable rdkafka \
;fi

###########################################################################
# GETTEXT:
###########################################################################

ARG PHPFPM_INSTALL_GETTEXT
RUN if [ ${PHPFPM_INSTALL_GETTEXT} = true ]; then \
    apt-get install -yqq zlib1g-dev libicu-dev g++ libpq-dev libssl-dev gettext && \
    docker-php-ext-install gettext \
;fi

###########################################################################
# MySQL Client:
###########################################################################

USER root
ARG PHPFPM_INSTALL_MYSQL_CLIENT
RUN if [ ${PHPFPM_INSTALL_MYSQL_CLIENT} = true ]; then \
      apt-get -y install default-mysql-client \
;fi

# Extension Part 8.
FROM extensions_part7 as extensions_part8
# ========================================================================>

###########################################################################
# XMLRPC:
###########################################################################

ARG PHPFPM_INSTALL_XMLRPC
RUN if [ ${PHPFPM_INSTALL_XMLRPC} = true ]; then \
  apt-get -yq install libxml2-dev; \
  if [ $(php -r "echo PHP_MAJOR_VERSION;") = "8" ]; then \
    pecl install xmlrpc-1.0.0RC3; \
    docker-php-ext-enable xmlrpc; \
  else \
    docker-php-ext-install xmlrpc; \
  fi \
;fi

###########################################################################
# PHP DECIMAL:
###########################################################################

USER root
ARG PHPFPM_INSTALL_PHPDECIMAL
RUN if [ ${PHPFPM_INSTALL_PHPDECIMAL} = true ]; then \
    if [ $(php -r "echo PHP_MAJOR_VERSION;") = "5" ]; then \
      echo 'decimal not support PHP 5.6'; \
    else \
      apt-get install -yqq libmpdec-dev \
      && pecl install decimal \
      && docker-php-ext-enable decimal \
      && php -m | grep -q 'decimal' \
    ;fi \
;fi

###########################################################################
# Fileinfo:
###########################################################################

# COPY ./04-fileinfo.ini /usr/local/etc/php/conf.d/04-fileinfo.ini

# Final Install.
FROM extensions_part8 as final_install
# ========================================================================>

###########################################################################
# Check PHP version:
###########################################################################

ARG PHPFPM_PHP_VERSION
RUN set -xe; php -v | grep -q "PHP ${PHPFPM_PHP_VERSION}."

###########################################################################
# Install composer:
###########################################################################

# RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
COPY . /home/sparrow/phpfpm/
RUN php /home/sparrow/phpfpm/templates/composer-installer.php --install-dir=/usr/local/bin --filename=composer \
  && apt update && apt install -y inetutils-ping netcat \
  && echo "------phpfpm dockerfile end------"

# curl.cainfo="/path/to/downloaded/cacert.pem"
# fix error(https://github.com/guzzle/guzzle/issues/1935#issuecomment-371756738): "cURL error 77: error setting certificate verify locations:  CAfile: /usr/local/openssl/cert.pem CApath: /etc/ssl/certs (see https://curl.haxx.se/libcurl/c/libcurl-errors.html)" 
RUN apt-get install -yqq wget && wget https://curl.haxx.se/ca/cacert.pem && mv cacert.pem /home/cacert.pem

# Final Config.
FROM final_install as final_config
# ========================================================================>

# Clean up
USER root
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    rm /var/log/lastlog /var/log/faillog

# Configure non-root user.
ARG PHPFPM_PUID
ENV PUID ${PHPFPM_PUID}
ARG PHPFPM_PGID
ENV PGID ${PHPFPM_PGID}
RUN groupmod -o -g ${PHPFPM_PGID} www-data && \
    usermod -o -u ${PHPFPM_PUID} -g www-data www-data

COPY ./templates/php${PHPFPM_VERSION_MIDLEN}.ini /usr/local/etc/php/php.ini

# Configure locale.
ARG LOCALE=POSIX
ENV LC_ALL ${LOCALE}
WORKDIR /var/www

# End Stage
FROM final_config as endstage
# ========================================================================>

CMD ["php-fpm"]
