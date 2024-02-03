#!/bin/sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH && cd ../../../
BATH_PATH=$(pwd)

# only define variables, these variables may used defined environment variables in /env file.

# defined different hook type.
CONST_HOOK_BEFORE_START="before_start"
CONST_HOOK_AFTER_START="after_start"
CONST_HOOK_BEFORE_STOP="before_stop"
CONST_HOOK_AFTER_STOP="after_stop"

# defined dir
CONST_SERVICE_EXAMPLE_DIR=".work/extra/service_example/"

# defined different config files.
CONST_BASE_CONFIG_ENV_AMD64_FILE=".work/config/.env.amd64"
CONST_BASE_CONFIG_ENV_ARM64_FILE=".work/config/.env.arm64"
CONST_BASE_CONFIG_COMPOSE_FILE=".work/config/docker-compose.yml"
CONST_SPARROW_CONFIG_ENV_FILE=".env"
CONST_SPARROW_CONFIG_COMPOSE_FILE="docker-compose.yml"
