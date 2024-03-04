#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# only include defined variables and functions.
# this is no side effects.
. .work/include/internal/constant.sh
. .work/include/internal/helper.sh
. .work/include/internal/dockerhub.sh

# update /env file and export env variables.
if ! upenv; then
    print_error "upenv error: upenv failed"
    exit 1
fi

# update /docker-compose.yml file.
if ! upcompose; then
    print_error "upcompose error: upcompose failed"
    exit 1
fi
