#!/bin/sh

# include sdk of sparrow.
. .work/include/sdk.sh

docker exec -d sparrow_container_${CONTAINER_NAMESPACE}_azkaban bash /home/azkaban/azkaban-solo-server/build/install/azkaban-solo-server/bin/start-solo.sh
