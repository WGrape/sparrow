#!/bin/sh

# this script is basic tool, such as install, uninstall, .etc
# This script is a fundamental operations tool, including installation, uninstallation, updates, etc.
# To maintain consistency and facilitate management, the filenames of these scripts all use the underscore (_) prefix.
# _update.sh

# define the base path of project.
CUR_PATH=$(cd "$(dirname "$0")" && pwd)
SPARROW_BASE_PATH=$CUR_PATH

# cd base dir of project.
# the process is in the same shell as the starting shell.
cd $SPARROW_BASE_PATH

# include sdk of sparrow.
. .work/include/sdk.sh

# update project.
update_project() {
    print_stage "git pull..."
    if ! git pull; then
        print_error "update project failed: git pull error"
        exit 1
    fi
}

# before run update command.
before_update_command() {
    print_stage "do before_update_command..."

    # check updatable
    if ! git diff --quiet; then
        print_error "update failed: please don't modify any files."
        exit 1
    fi
}

# after run update command.
after_update_command() {
    print_stage "do after_update_command..."
}

##################### start script exec flow #####################

# before run update command.
before_update_command

# update project.
update_project

# after run update command.
after_update_command

# end.
print_info "update successfully"

##################### end script exec flow #######################
