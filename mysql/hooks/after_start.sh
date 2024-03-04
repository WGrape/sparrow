#!/bin/sh

# not need to include sdk of sparrow.
# because the execution of hook scripts must be within the sparrow script, sdk.sh has already been imported at this point.
# . .work/include/sdk.sh

docker exec -d sparrow_container_${CONTAINER_NAMESPACE}_mysql bash /home/sparrow/mysql/init/init.sh
