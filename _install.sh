#!/bin/sh

# this script is basic tool, such as install, uninstall, .etc
# This script is a fundamental operations tool, including installation, uninstallation, updates, etc.
# To maintain consistency and facilitate management, the filenames of these scripts all use the underscore (_) prefix.
# _install.sh

# define the base path of project.
CUR_PATH=$(cd "$(dirname "$0")" && pwd)
SPARROW_BASE_PATH=$CUR_PATH

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# include sdk of sparrow.
. .work/include/sdk.sh

# chmod files.
chmod_files() {
    print_stage "do chmod_files..."

    print_stage "chmod ./sparrow"
    if ! chmod a+x ./sparrow; then
        print_error "error: chmod sparrow"
        exit 1
    fi

    print_stage "chmod ./sparrowtool"
    if ! chmod a+x ./sparrowtool; then
        print_error "error: chmod sparrowtool"
        exit 1
    fi
}

# create files.
create_files() {
    # create PHPFPM_LOCALHOST_LARAVEL_APP_LOG_PATH.
    create_dir=$PHPFPM_LOCALHOST_LARAVEL_APP_LOG_PATH
    print_stage "check directory: PHPFPM_LOCALHOST_LARAVEL_APP_LOG_PATH=${create_dir}"
    if [ ! -d "${create_dir}" ]; then
        print_info "directory: ${create_dir} not exist, auto creating..."

        if ! mkdir -p "${create_dir}"; then
            print_error "error: can't create log directory ${create_dir}"
            exit 1
        fi
    fi
}

# modify files.
modify_files() {
    # compute go_path.
    print_stage "compute local_go_path"
    if command -v go &> /dev/null; then
        local_go_path=$(go env GOPATH)  # cmd: go env GOPATH
    fi
    if [ "$local_go_path" = "" ]; then
        local_go_path=$GO_PATH
    fi

    # modify go_path in /env file.
    # this operation is fine because when the sdk.sh file is included at the beginning, the /env file is created.
    print_info "set GO_PATH: before($GO_PATH), after($local_go_path)"
    awk -F= '/^GO_PATH=/{OFS="="; $2="'${local_go_path}'"}1' "$CONST_SPARROW_CONFIG_ENV_FILE" > temp && mv temp "$CONST_SPARROW_CONFIG_ENV_FILE"
}

# before run install command.
before_install_command() {
    print_stage "do before_install_command..."

    # check docker is installed.
    if ! command -v docker &> /dev/null; then
        print_info "please install docker and docker-compose firstly, reference: https://github.com/WGrape/sparrow/tree/main/.work/extra/doc/5.QA_EN.md"
        echo "==================================================================================="

        echo "1. install docker"
        echo "curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun"

        echo "2. install docker-compose"
        echo "curl -L https://github.com/docker/compose/releases/download/1.27.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"
        echo "chmod +x /usr/local/bin/docker-compose"
    else
        print_info "docker is already installed."
    fi
}

# after run install command.
after_install_command() {
    print_stage "do after_install_command..."
}

##################### start script exec flow #####################

# before run install command.
before_install_command

# chmod files.
chmod_files

# modify files.
modify_files

# create files.
create_files

# after run install command.
after_install_command

# end.
print_info "install successfully"

##################### end script exec flow #######################
