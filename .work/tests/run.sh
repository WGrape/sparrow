#!/bin/sh

# include sdk of sparrow.
. .work/include/sdk.sh

testhttp() {
    if is_mac; then
        # open websites.
        open "http://127.0.0.1:${ETCDKEEPER_HOST_PORT}/etcdkeeper/" # etcdkeeper
        open "http://127.0.0.1:${KAFKAUI_HOST_PORT}/" # kafkaui
    fi
}
testhttp

printf "UnitTest Success"
exit 0
