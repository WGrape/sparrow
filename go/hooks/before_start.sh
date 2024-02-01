#!/bin/sh

# not need to include sdk of sparrow.
# because the execution of hook scripts must be within the sparrow script, sdk.sh has already been imported at this point.
# source .work/include/sdk.sh

if [ ! -d "$GO_PATH" ]; then
    if ! mkdir -p "$GO_PATH"; then
        print_error "mkdir $GO_PATH failed"
        exit 1
    fi
fi
