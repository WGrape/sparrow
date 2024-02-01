#!/bin/sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH && cd ../../
BATH_PATH=$(pwd)

# only include defined variables and functions.
# this is no side effects.
source .work/include/internal/constant.sh
source .work/include/internal/helper.sh
source .work/include/internal/dockerhub.sh

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
