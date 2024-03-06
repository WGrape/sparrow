#!/bin/sh

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# -----------------------define some basic helpers-----------------------

# is mac platform.
# if is_mac; then
#     echo "is mac"
# else
#     echo "is not mac"
# fi
is_mac() {
    uname_out="$(uname -s)"
    if [ "$uname_out" = "Darwin" ]; then
        return 0  # yes
    else
        return 1  # no
    fi
}

# is linux platform.
# if is_linux; then
#     echo "is linux"
# else
#     echo "is not linux"
# fi
is_linux() {
    uname_out="$(uname -s)"
    if [ "$uname_out" = "Linux" ]; then
        return 0  # yes
    else
        return 1  # no
    fi
}

# sleep for x seconds.
sleep_seconds() {
    print_info "sleeping for while"
    i=$1
    # this syntax is not available in sh, only available in bash, so changed it.
    # for ((i = $1; i >= 0; i--)); do
    while [ "$i" -ge 0 ]; do
        printf  "sleep seconds: $i seconds\r"
        sleep 1
        i=$(( i - 1 ))
    done
    printf "\r\n"
}

# print info message.
print_info() {
    if [ "$VAR_RUNTIME_NO_PRINT_MESSAGE" = "ON" ]; then
        return 0
    fi
    printf "\033[34m\n===== $1 =====\033[0m\n\n"
}

# print stage message.
print_stage() {
    if [ "$VAR_RUNTIME_NO_PRINT_MESSAGE" = "ON" ]; then
        return 0
    fi

    if [ "$STAGE_ID" = "" ]; then
        STAGE_ID=0
    fi
    ((STAGE_ID++))
    printf "\033[32m\n+++++ stage$STAGE_ID: $1 +++++\033[0m\n\n"
}

# print error message.
print_error() {
    printf "\033[31m>>>>> $1 <<<<<\033[0m\n"
}

# print warn message.
print_warn() {
    if [ "$VAR_RUNTIME_NO_PRINT_MESSAGE" = "ON" ]; then
        return 0
    fi
    printf "\e[33m~~~~~ $1 ~~~~~\e[0m\n\n"
}

# the common function to parse env file, and export variables.
parse_env_file() {
    if [ "$1" == "" ]; then
        print_error "miss file to parse"
        exit 1
    fi

    # export environment variables.
    print_info "parse_env_file: parse and export environment variables..."
    while IFS= read -r line || [[ -n "$line" ]]; do
        line=$(echo "$line" | sed 's/#.*//' | awk '{$1=$1};1')
        if [ "$line" = "" ]; then
            continue
        fi

        key=$(echo "$line" | cut -d '=' -f1)
        value=$(echo "$line" | cut -d '=' -f2-)
        # print_info "env variable: ${key}=${value}"
        if ! eval "$key"="$value"; then
            print_error "parse env error: $line | $key | $value"
            exit 1
        fi
    done < $1
}

# ------------------------------end-------------------------------------

# -----------------------define some sparrow helpers-----------------------

# create /env file and export these variables.
upenv() {
    print_stage "upenv"

    # must not to regenerate the env file, if env file exists.
    env_file=$CONST_SPARROW_CONFIG_ENV_FILE
    if [ ! -f "${env_file}" ]; then
        # parse /.work/config/.env file firstly
        # Because there are many variables in this file that need to be used now, such as ```ENABLE_SERVICE_LIST```
        parse_env_file $CONST_BASE_CONFIG_ENV_AMD64_FILE

        # copy /.work/config/.env file to /.env file
        print_info "cp ${CONST_BASE_CONFIG_ENV_AMD64_FILE} file to ${env_file} file..."
        cp "${CONST_BASE_CONFIG_ENV_AMD64_FILE}" "./${env_file}"

        # copy every /service/.env file to /.env file
        # traverse every service directory, but only include enabled service, so not run ```for dir in */; do```
        service_list=("${ENABLE_SERVICE_LIST[@]}")
        for service in "${service_list[@]}"; do
            # find service's env file.
            srv_env_file="${service}/${CONST_SPARROW_CONFIG_ENV_FILE}"
            if [ ! -f "${srv_env_file}" ]; then
                print_error "no ${env_file} file found in ${service}"
                exit 1
            fi

            # cp every service's env file to /env file.
            print_info "cp ${srv_env_file} file to /${env_file} file..."
            echo "" >> $CONST_SPARROW_CONFIG_ENV_FILE
            cat "${srv_env_file}" >> $CONST_SPARROW_CONFIG_ENV_FILE
        done
    else
        print_info "/${env_file} file exists, pass"
    fi

    # parse /.env file
    # must put it outer, because even if there is an .env file when it is started, the variables in this file need to be parsed.
    parse_env_file $CONST_SPARROW_CONFIG_ENV_FILE

    # check environment configuration.
    enable_service_list_length=${#ENABLE_SERVICE_LIST[@]}
    if [ "$enable_service_list_length" = 0 ]; then
        print_error "the ENABLE_SERVICE_LIST must not be empty!"
        exit 1
    fi
}

# create and update /docker-compose file, must after run upenv.
# if ENABLE_SERVICE_LIST is configured, the /docker-compose.yml configuration file also needs to be updated accordingly.
# therefore, it is necessary to regenerate the /docker-compose.yml file each time
upcompose() {
    print_stage "upcompose"

    # cp base_config_compose file to /docker-compose file.
    print_info "cp ${CONST_BASE_CONFIG_COMPOSE_FILE} file to docker-compose file..."
    cp "${CONST_BASE_CONFIG_COMPOSE_FILE}" "./${CONST_SPARROW_CONFIG_COMPOSE_FILE}"

    # traverse every service directory.
    for service in "${ENABLE_SERVICE_LIST[@]}"; do
        dir_name="$service"
        if [ ! -d "${dir_name}" ]; then
            print_error "the service directory not exist: ${dir_name}"
            exit 1
        fi

        # find every service's docker-compose file.
        srv_compose_file="${dir_name}/${CONST_SPARROW_CONFIG_COMPOSE_FILE}"
        if [ ! -f "${srv_compose_file}" ]; then
            print_error "no docker-compose.yml file found in ${dir_name}"
            exit 1
        fi

        # cp every service's docker-compose file to /docker-compose file.
        echo "" >> "${CONST_SPARROW_CONFIG_COMPOSE_FILE}"
        sed '/services:/d' "${srv_compose_file}" >> "${CONST_SPARROW_CONFIG_COMPOSE_FILE}"
    done
}

# pull or build app image.
pull_or_build_app_image() {
    if [ "$1" == "" ]; then
        print_error "pull_or_build_app_image miss service param"
        exit 1
    fi
    service="$1"

    version_name=$(echo "IMAGE_APP_${service}_VERSION" | awk '{print toupper($0)}')
    version=$(eval echo "$"$version_name)
    if pull app $service $version; then
        print_info "pull success: pull app $service $version"
    elif . "./$service/make_app_image/run.sh"; then
        print_info "build success: run $service/make_app_image/run.sh"
    else
        print_error "pull and build sparrow-app-$service image error"
        exit 1
    fi
}

# clear the resources(container, image) of service
clear_service_resources() {
    service=$1
    if [ "$service" == "" ]; then
        print_error "clear_service_resources miss param"
        exit 1
    fi
    # remove the $service container.
    print_stage "stop and remove container: sparrow_container_${CONTAINER_NAMESPACE}_${service}"
    docker stop "sparrow_container_${CONTAINER_NAMESPACE}_${service}"
    docker rm "sparrow_container_${CONTAINER_NAMESPACE}_${service}"

    # remove the all version images of sparrow-basic-$service/sparrow-app-$service.
    print_stage "removing images: sparrow-basic-$service(all version), sparrow-app-$service(all version)"
    docker images | grep "sparrow-app-$service" | awk '{print $3}' | xargs -I {} sh -c 'if [ -n "{}" ]; then docker rmi "{}"; fi'
    # perhaps there's no need to delete the basic image; we'll see later if this operation can be removed.
    docker images | grep "sparrow-basic-$service" | awk '{print $3}' | xargs -I {} sh -c 'if [ -n "{}" ]; then docker rmi "{}"; fi'
}

# ------------------------------end-------------------------------------
