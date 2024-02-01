ARG FROM_PLATFORM
ARG IMAGE_BASIC_MYSQL_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-mysql:${IMAGE_BASIC_MYSQL_VERSION}

# ARG TZ
# ENV TZ ${TZ}
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && chown -R mysql:root /var/lib/mysql/
RUN chown -R mysql:root /var/lib/mysql/

EXPOSE 3306
CMD ["mysqld"]
