#!/bin/sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH && cd ../../../
BATH_PATH=$(pwd)

# -----------------------define some basic helpers-----------------------

# print info message.
print_info() {
    printf "\033[34m\n===== $1 =====\033[0m\n\n"
}

# print stage message.
print_stage() {
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
    printf "\e[33m~~~~~ $1 ~~~~~\e[0m\n\n"
}

# when an error occurs, provide some command tip.
error_cmdtip() {
    print_warn "tip: you should run the command firstly: $1"
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

# ------------------------------end-------------------------------------

# -----------------------define some sparrow helpers-----------------------

# check if sparrow can be started when run command: ./sparrow start, ./sparrow stop .etc.
check_startable() {
    # check docker.
    if ! docker info > /dev/null 2>&1; then
        print_error "error: please install or start docker first, installation of mac is here : https://docs.docker.com/desktop/release-notes/#4242 (you can choose any version)."
        exit 1
    fi

    # check ip.
    local_ip=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | sed 's/,$//' | head -n 1)
    if [ "$local_ip" != "$DOCKER_HOST_IP" ]; then
        print_warn "your ip: before=$DOCKER_HOST_IP, after=$local_ip"

        DOCKER_HOST_IP=$local_ip  # update environment DOCKER_HOST_IP
        if is_mac; then
            sed -i '' "s/^DOCKER_HOST_IP=.*/DOCKER_HOST_IP=${DOCKER_HOST_IP}/g" "${CONST_SPARROW_CONFIG_ENV_FILE}"
        elif is_linux; then
            sed -i "s/^DOCKER_HOST_IP=.*/DOCKER_HOST_IP=${DOCKER_HOST_IP}/g" "${CONST_SPARROW_CONFIG_ENV_FILE}"
        else
            print_error "your local ip changed, please modify DOCKER_HOST_IP in the ${CONST_SPARROW_CONFIG_ENV_FILE} file"
            exit 1
        fi
    fi
}

# check if sparrow can be updated when run command: ./_update.sh
check_updatable() {
    if ! git diff --quiet; then
        print_error "install failed: please don't modify any files."
        exit 1
    fi
}

# do sparrow hook
hook() {
    if [ "$2" = "all" ]; then
        # exec every service's hook
        for service in "${ENABLE_SERVICE_LIST[@]}"; do
            hook_file="${service}/hooks/$1.sh"
            if [ -f "${hook_file}" ]; then
                print_info "do hook: ${hook_file}"
                source "${hook_file}"
            fi
        done
    else
        # exec the service's hook
        hook_file="$2/hooks/$1.sh"
        if [ -f "${hook_file}" ]; then
            print_info "do hook: ${hook_file}"
            source "${hook_file}"
        fi
    fi
}

# clear service, include remove container and remove images.
clear_service() {
    # check service param.
    if [ "$1" == "" ]; then
        print_error "miss service"
        exit 1
    fi
    if [ "$1" == "all" ]; then
        service_list=("${ENABLE_SERVICE_LIST[@]}")  # copy the whole array
    else
        service_list=($1)
    fi

    print_info "clear service_list: ${service_list}"
    for service in "${service_list[@]}"; do
        # remove the $service container.
        print_stage "stop and remove container: sparrow_container_${CONTAINER_NAMESPACE}_${service}"
        docker stop "sparrow_container_${CONTAINER_NAMESPACE}_${service}"
        docker rm "sparrow_container_${CONTAINER_NAMESPACE}_${service}"

        # remove the all version images of sparrow-basic-$service/sparrow-app-$service.
        print_stage "removing images: sparrow-basic-$service(all version), sparrow-app-$service(all version)"
        docker images | grep "sparrow-app-$service" | awk '{print $3}' | xargs -I {} sh -c 'if [ -n "{}" ]; then docker rmi "{}"; fi'
        # perhaps there's no need to delete the basic image; we'll see later if this operation can be removed.
        docker images | grep "sparrow-basic-$service" | awk '{print $3}' | xargs -I {} sh -c 'if [ -n "{}" ]; then docker rmi "{}"; fi'
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

# ------------------------------end-------------------------------------

# -----------------------define some help-document helpers-----------------------

# sparrow's help command
sparrow_help() {
    printf "welcome to sparrow\n"
    printf "========================================================\n"
    printf "load env file: ${CONST_SPARROW_CONFIG_ENV_FILE}\n"
    printf "the enable service list: $(IFS=,; echo "${ENABLE_SERVICE_LIST[*]}")\n"
    printf "========================================================\n"
    printf "\n"
    printf "1、Control all service.\n"
    printf "(1) stop all services: ./sparrow stop\n"
    printf "(2) start all services: ./sparrow start\n"
    printf "(3) restart all services: ./sparrow restart\n"
    printf "\n"
    printf "2、Control one service.\n"
    printf "(1) stop one service: ./sparrow stopone {service_name}\n"
    printf "(2) start one service: ./sparrow startone {service_name}\n"
    printf "(3) update one service: ./sparrow updateone {service_name}\n"
    printf "(4) clear service: ./sparrow clear {service_name}/all\n"
    printf "\n"
    printf "4、Container helper.\n"
    printf "(1) enter all containers(Automatically open all required resources): ./sparrow enter\n"
    printf "(2) enter one container: ./sparrow enter {service_name}\n"
    printf "\n"
}

# sparrowtool's help command
sparrowtool_help() {
    printf "welcome to sparrowtool\n"
    printf "========================================================\n"
    printf "load env file: ${CONST_SPARROW_CONFIG_ENV_FILE}\n"
    printf "========================================================\n"
    printf "\n"
    printf "1、about create.\n"
    printf "(1) create service: ./sparrowtool new -t service -s {service_name} -p port -v version\n"
    printf "    ① params: -t(type:service) / -s(service) / -p(port) / -v(version)\n"
    printf "    ② example: ./sparrowtool new -s prometheus -p 9876 -v 0.0.98\n"
    printf "(2) create nginx virtual host file: ./sparrowtool new -t nginx -s {app_name}\n"
    printf "    ① params: -t(type:service) / -s(app_name)\n"
    printf "\n"
    printf "2、about image.\n"
    printf "(1) push image: ./sparrowtool upload -t(type:app|basic) -s(service) -v(version) -r(replace)\n"
    printf "    ① param: {app}means the application image, {basic}means the basic image, {service}means the name of service.\n"
    printf "    ② example: ./sparrowtool upload -t basic -s etcd -v 3.5.0\n"
    printf "\n"
    printf "3、about env.\n"
    printf "(1) list all matched environment variables in /env file : ./sparrowtool env -l {match_pattern}\n"
    printf "    ① param: -l(match_pattern)\n"
    printf "    ① example: ./sparrowtool env -l port\n"
    printf "\n"
    printf "========================================================\n"
    printf "NGINX_SITES_PATH=$NGINX_SITES_PATH\n"
    printf "FROM_PLATFORM=$FROM_PLATFORM\n"
    printf "========================================================\n"
}

# ------------------------------end-------------------------------------
