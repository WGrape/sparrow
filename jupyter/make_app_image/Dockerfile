ARG FROM_PLATFORM
ARG IMAGE_BASIC_JUPYTER_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-jupyter:${IMAGE_BASIC_JUPYTER_VERSION}

ARG JUPYTER_CONTAINER_PORT
ENV JUPYTER_PORT ${JUPYTER_CONTAINER_PORT}

ARG JUPYTER_TOKEN
ENV JUPYTER_TOKEN ${JUPYTER_TOKEN}
# https://stackoverflow.com/questions/48875436/jupyter-password-and-docker

# CMD ["start-notebook.sh", "--NotebookApp.token=''", "--NotebookApp.password=''", "--NotebookApp.allow_origin='*'", "--NotebookApp.notebook_dir='/var/data/jupyter/'"]
CMD ["start-notebook.sh", "--NotebookApp.allow_origin='*'", "--NotebookApp.notebook_dir='/var/data/jupyter/'"]
