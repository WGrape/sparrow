ARG FROM_PLATFORM
ARG IMAGE_BASIC_DJANGO_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-django:${IMAGE_BASIC_DJANGO_VERSION}

# change source
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# install Django
RUN python -m pip install Django && python -m django --version

WORKDIR /var/data/django

# start project
# RUN django-admin startproject demo && cd demo
# default listen 127.0.0.1, it may cause error: cannot access Django server in docker container via ip:port
# so must listen 0.0.0.0
# RUN nohup python manage.py runserver 0.0.0.0:8000 &
