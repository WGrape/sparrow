#!/bin/sh

# define the base path of project.
CUR_PATH=$(cd "$(dirname "$0")" && cd ../../ && pwd)
SPARROW_BASE_PATH=$CUR_PATH

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# include sdk of sparrow.
. .work/include/sdk.sh

sleep_seconds 3

testhttp() {
    if is_mac; then
        # open websites.
         open "http://127.0.0.1:${ETCDKEEPER_HOST_PORT}/etcdkeeper/" # etcdkeeper
         open "http://127.0.0.1:${KAFKAUI_HOST_PORT}/" # kafkaui
         open "http://127.0.0.1:${PROMETHEUS_HOST_PORT}/targets" # prometheus
         open "http://127.0.0.1:${PROMETHEUS_HOST_PORT}/graph" # prometheus
         open "http://127.0.0.1:${GRAFANA_HOST_PORT}/graph" # prometheus
    fi
}
# testhttp

echo "test search"
for service in "${ENABLE_SERVICE_LIST[@]}"; do
    image="sparrow-basic-${service}"
    search "$DOCKERHUB_REPO/$image"
    image="sparrow-app-${service}"
    search "$DOCKERHUB_REPO/$image"
done

printf "UnitTest Success"
exit 0
