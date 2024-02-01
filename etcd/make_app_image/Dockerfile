ARG FROM_PLATFORM
ARG IMAGE_BASIC_ETCD_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-etcd:${IMAGE_BASIC_ETCD_VERSION}

ENV ETCD_NAME "SparrowEtcd"
ENV ALLOW_NONE_AUTHENTICATION yes
ENV ETCD_INITIAL_ADVERTISE_PEER_URLS "http://etcd:${ETCD_CONTAINER_SERVER_PORT}"
ENV ETCD_CONTAINER_SERVER_PORT "http://etcd:${ETCD_CONTAINER_CLIENT_PORT}"
CMD ["/opt/bitnami/scripts/etcd/run.sh"]
# CMD ["etcd", "--name=etcd", "--initial-advertise-peer-urls=http://etcd:2380", "--advertise-client-urls=http://etcd:2379", "--listen-client-urls=http://0.0.0.0:2379", "--listen-peer-urls=http://0.0.0.0:2380", "--initial-cluster=etcd=http://etcd:2380", "--initial-cluster-token=etcd", "--initial-cluster-state=new"]
# CMD ["etcd", "--name=etcd", "--initial-advertise-peer-urls=http://0.0.0.0:2380", "--advertise-client-urls=http://0.0.0.0:2379", "--listen-client-urls=http://0.0.0.0:2379", "--listen-peer-urls=http://0.0.0.0:2380", "--initial-cluster=etcd=http://0.0.0.0:2380", "--initial-cluster-token=etcd", "--initial-cluster-state=new"]
