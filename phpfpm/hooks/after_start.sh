#!/bin/sh

# not need to include sdk of sparrow.
# because the execution of hook scripts must be within the sparrow script, sdk.sh has already been imported at this point.
# . .work/include/sdk.sh

docker exec -e PHPFPM_LARAVEL_APP_LOG_PATH=$PHPFPM_LARAVEL_APP_LOG_PATH -d sparrow_container_${CONTAINER_NAMESPACE}_phpfpm bash /home/sparrow/phpfpm/init/init.sh
