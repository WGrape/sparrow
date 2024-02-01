
#!/bin/sh

# You can choose any one of the ways of db building.

# exec sql
# 1. You must wait for 10 seconds as the container may not have been fully created yet.
# 2. You must use root account to do some initialization things. Otherwise, it may be failed.
sleep_seconds 10
mysql --default-character-set=utf8mb4 -u${MYSQL_ROOT_USER} -h localhost -P 3306 -p${MYSQL_ROOT_USER} < /home/sparrow/mysql/init/init.sql

# upload db
# mysql --default-character-set=utf8mb4 -usparrow -h localhost -P 3306 -psparrow -Dsparrow < exam.db
