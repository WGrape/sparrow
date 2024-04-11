ARG FROM_PLATFORM
ARG IMAGE_BASIC_AZKABAN_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-azkaban:${IMAGE_BASIC_AZKABAN_VERSION}

# change source
# fix error: https://stackoverflow.com/questions/70963985/error-failed-to-download-metadata-for-repo-appstream-cannot-prepare-internal
RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
RUN yum install wget -y

# change yum source
RUN cd /etc/yum.repos.d/ && ls -alh && cp CentOS-Linux-BaseOS.repo CentOS-Linux-BaseOS.repo.bk && wget http://mirrors.aliyun.com/repo/Centos-8.repo
RUN yum clean all && cd /etc/yum.repos.d/ && ls -alh && mv Centos-8.repo CentOS-Linux-BaseOS.repo && yum makecache

# install git
RUN yum update -y && yum install git -y && git --version

# install java
RUN yum -y list java* && yum install java-1.8.0-openjdk.x86_64 -y

# install nodejs
RUN curl --silent --location https://rpm.nodesource.com/setup_18.x | bash
RUN yum install -y nodejs && node -v

# change npm source
# you don't need yum install -y npm, because npm has already installed after nodejs is installed.
# if you yum install -y npm, may cause long-time wait and error
RUN npm config set registry https://registry.npmmirror.com
RUN npm config get registry

# clone azkaban
RUN cd /home && git clone https://github.com/azkaban/azkaban.git

# modify azkaban
# error: Execution failed for task ':azkaban-web-server:nodeSetup'. https://blog.csdn.net/liuandefeng/article/details/130983335 | https://www.cnblogs.com/wuzhiblog/p/13620906.html | https://github.com/azkaban/azkaban/issues/3310
RUN sed -i 's/download = true/download = false/g' /home/azkaban/azkaban-web-server/build.gradle

# build azkaban
RUN cd /home/azkaban/ && ./gradlew build installDist -x test

# run azkaban
# Since it will start a process in the background and exit directly, resulting in no program running in the foreground, you can enable a command like tail -f to ensure that it will not exit.
# RUN cd /home/azkaban/azkaban-solo-server/build/install/azkaban-solo-server && ./bin/start-solo.sh
WORKDIR /home/azkaban/azkaban-solo-server/build/install/azkaban-solo-server

# after start, you need start ./bin/start-solo.sh
# There will be problems if you start it directly here. The current implementation plan is to execute the startup command in the after_start hook.
# ./hooks/after_start.sh
