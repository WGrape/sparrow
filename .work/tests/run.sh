#!/bin/sh

# include sdk of sparrow.
source .work/include/sdk.sh

if ! check_startable; then
    print_error "test failed: check_startable error"
    exit 1
fi

sleep_seconds 2

testhttp() {
    # open websites.
    open "http://127.0.0.1:${ETCDKEEPER_HOST_PORT}/etcdkeeper/" # etcdkeeper
    open 'http://127.0.0.1:7080/test' # golang
    open 'http://127.0.0.1:80' # php/laravel/nginx
    open 'http://127.0.0.1:7600/' # kafkaui
}
testhttp

# You can start one by one, to test !
# ./sparrow stop
# ./sparrow startone redis
# ./sparrow startone mysql
# ./sparrow startone go

printf "UnitTest Success"
exit 0
