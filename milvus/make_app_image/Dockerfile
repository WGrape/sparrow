ARG FROM_PLATFORM
ARG IMAGE_BASIC_MILVUS_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-milvus:${IMAGE_BASIC_MILVUS_VERSION}

CMD ["milvus", "run", "standalone"]
