ARG FROM_PLATFORM
ARG IMAGE_BASIC_PYTHON_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-python:${IMAGE_BASIC_PYTHON_VERSION}

# change source
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
# download dependences
RUN pip install openai && pip install mysql-connector-python && pip install pyyaml && pip install pytz && pip install flask && pip install pandas && pip install requests
