#!/bin/sh

# not need to include sdk of sparrow.
# because the execution of hook scripts must be within the sparrow script, sdk.sh has already been imported at this point.
# . .work/include/sdk.sh

# Due to the dependency of the Kafka service on the ZooKeeper service, it is necessary to start ZooKeeper first.
if docker container inspect -f '{{.State.Running}}' "sparrow_container_${CONTAINER_NAMESPACE}_zookeeper" &> /dev/null; then
    print_info "zookeeper container is running, allowed to continue."
else
    print_error "zookeeper container is not running, it is necessary to start ZooKeeper first."
    exit 1
fi

