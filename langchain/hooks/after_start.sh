#!/bin/sh

# not need to include sdk of sparrow.
# because the execution of hook scripts must be within the sparrow script, sdk.sh has already been imported at this point.
# source .work/include/sdk.sh

echo "after start, please reset your OPENAI_API_KEY inside the container manually: export OPENAI_API_KEY=''"
docker exec -d sparrow_container_${CONTAINER_NAMESPACE}_langchain bash /home/sparrow/langchain/init/init.sh
