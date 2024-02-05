#!/bin/sh

# this script is basic tool, such as install, uninstall, .etc
# This script is a fundamental operations tool, including installation, uninstallation, updates, etc.
# To maintain consistency and facilitate management, the filenames of these scripts all use the underscore (_) prefix.
# _uninstall.sh

# cd base dir of project.
CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)
cd $CUR_PATH
BATH_PATH=$(pwd)

# command interface.
read -p "do you want to uninstall？(input y): " confirmation
if [ "$confirmation" == "y" ]; then
    echo "start uninstall..."
else
    echo "you canceled uninstall!"
    exit 1
fi

# =================== choose sure ===================

# include sdk of sparrow.
source .work/include/sdk.sh

# remove files.
remove_files() {
    print_stage "removing files..."
    files=("$CONST_SPARROW_CONFIG_ENV_FILE" "$CONST_SPARROW_CONFIG_COMPOSE_FILE")
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_info "removing $file..."
            rm -f "./$file"
        fi
    done
}

# before run uninstall command.
before_uninstall_command() {
    print_stage "do before_uninstall_command..."
}

# after run uninstall command.
after_uninstall_command() {
    print_stage "do after_uninstall_command..."
}

##################### start script exec flow #####################

# before run uninstall command.
before_uninstall_command

# remove files.
remove_files

# after run uninstall command.
after_uninstall_command

# end.
print_info "uninstall successfully!"

##################### end script exec flow #######################
