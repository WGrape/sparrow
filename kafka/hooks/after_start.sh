#!/bin/sh

# not need to include sdk of sparrow.
# because the execution of hook scripts must be within the sparrow script, sdk.sh has already been imported at this point.
# source .work/include/sdk.sh

back_kafka_broker_container="sparrow_container_${CONTAINER_NAMESPACE}_kafka1"
output=$(docker container ps -a | grep "$back_kafka_broker_container")
if [ -n "$output" ]; then
    print_info "stop and remove $back_kafka_broker_container ..."
    docker stop $back_kafka_broker_container && docker rm $back_kafka_broker_container
fi

print_info "restart $back_kafka_broker_container ..."
docker run -d --name $back_kafka_broker_container -p $((KAFKA_CONTAINER_PORT+1)):$((KAFKA_CONTAINER_PORT+1)) \
  -e KAFKA_BROKER_ID=1 \
  -e KAFKA_ZOOKEEPER_CONNECT=${DOCKER_HOST_IP}:${ZOOKEEPER_CONTAINER_PORT} \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://${DOCKER_HOST_IP}:$((KAFKA_CONTAINER_PORT+1)) \
  -e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:$((KAFKA_CONTAINER_PORT+1)) \
  --platform ${FROM_PLATFORM} \
  -t sparrow-basic-kafka:${IMAGE_BASIC_KAFKA_VERSION}
