#!/bin/sh

current_dir=$(pwd)

printf "init phpfpm ...\n\n"
printf "\n"
printf "sleep 10 seconds ...\n\n"
sleep 10

# Switch the composer mirror to avoid some errors.
# Such as the network error, the authentication required error.
composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/

# Traverse all php-fpm project directories under /var/data/phpfpm/ and execute composer install
auto_composer_install=false
if [ "${auto_composer_install}" = "true" ]; then
  for dir in /var/data/phpfpm/*; do
    # Check if the directory is a directory and contains a composer.json file
    if [[ -d "$dir" && -f "$dir/composer.json" ]]; then
      # Change to the project directory
      cd "$dir"
      
      # Execute composer install command
      # It will take long times ... just wait for a while
      composer install
    fi
  done
fi

# Create some must directories
if [ "${PHPFPM_LARAVEL_APP_LOG_PATH}" != "" ]; then
  mkdir -p ${PHPFPM_LARAVEL_APP_LOG_PATH}
  chmod -R 777 ${PHPFPM_LARAVEL_APP_LOG_PATH}
fi

cd ${current_dir}
