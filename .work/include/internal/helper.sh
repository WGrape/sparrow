#!/bin/sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH && cd ../../../
BATH_PATH=$(pwd)

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
    for ((i = $1; i >= 0; i--)); do
        printf  "sleep seconds: $i seconds\r"
        sleep 1
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

# ------------------------------end-------------------------------------

# -----------------------define some sparrow helpers-----------------------

# create /env file and export these variables.
upenv() {
    print_stage "upenv"

    # must not to regenerate the env file, if env file exists.
    env_file=$CONST_SPARROW_CONFIG_ENV_FILE
    if [ ! -f "${env_file}" ]; then
        print_info "cp ${CONST_BASE_CONFIG_ENV_AMD64_FILE} file to ${env_file} file..."
        cp "${CONST_BASE_CONFIG_ENV_AMD64_FILE}" "./${env_file}"

        # traverse every service directory.
        for dir in */; do
            # remove the end slash (/) from the path
            dir_name=$(basename "$dir")
            if [ "$dir_name" == ".work" ]; then
                print_info "pass: $dir"
                continue
            fi

            # find every service's env file.
            srv_env_file="${dir_name}/${CONST_SPARROW_CONFIG_ENV_FILE}"
            if [ ! -f "${srv_env_file}" ]; then
                print_error "no ${env_file} file found in ${dir_name}"
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

    # export environment variables.
    print_stage "export environment variables..."
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
    done < $CONST_SPARROW_CONFIG_ENV_FILE

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
    elif source "./$service/make_app_image/run.sh"; then
        print_info "build success: run $service/make_app_image/run.sh"
    else
        print_error "pull and build sparrow-app-$service image error"
        exit 1
    fi
}

# ------------------------------end-------------------------------------
