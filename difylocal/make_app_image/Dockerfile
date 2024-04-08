ARG FROM_PLATFORM
ARG IMAGE_BASIC_DIFYLOCAL_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-difylocal:${IMAGE_BASIC_DIFYLOCAL_VERSION} AS builder

# change pip source
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# RUN sed -i 's#https://deb.nodesource.com/node_12.x/#https://mirrors.tuna.tsinghua.edu.cn/nodesource/deb_12.x/#' /etc/apt/sources.list.d/nodesource.list

# RUN apt-get update && apt-get install nodejs=18.19.0 && node -v
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get update && apt-get install -y nodejs && node -v

RUN npm config set registry https://registry.npmmirror.com
RUN npm config get registry

WORKDIR /var/data/difylocal
