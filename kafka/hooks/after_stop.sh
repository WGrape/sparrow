#!/bin/sh

# not need to include sdk of sparrow.
# because the execution of hook scripts must be within the sparrow script, sdk.sh has already been imported at this point.
# . .work/include/sdk.sh

output=$(docker container ps -a | grep 'sparrow_container_${CONTAINER_NAMESPACE}_kafka1')
if [ -n "$output" ]; then
    docker stop sparrow_container_${CONTAINER_NAMESPACE}_kafka1 && docker rm sparrow_container_${CONTAINER_NAMESPACE}_kafka1
fi
