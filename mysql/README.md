## What is this directory
This is the service directory, it includes these directories and files as bellow.

## 1. Directories

### (1) Commit to Git.

#### /hooks

```/hooks```: This is the hook actions while the service/container start/stop.

#### /init

```/init```: This is init scripts after the container created, is executed by ```./hooks/after_start.sh```

#### /make_app_image
```/make_app_image```: This is the ```sparrow-app-*``` image making directory.

#### /make_basic_image
```/make_basic_image```: This is the ```sparrow-basic-*``` image making directory.

#### /templates
```/templates```: this is the template directory for the service, the ```template``` means all static and unchanging files.

### (2) Not commit to Git.

#### /conf
```conf```: This is config dir of the running service. In the ```docker-compose.yml```/```make_app_image/Dockerfile``` file in this directory, the configuration files in this directory are mapped/copied to the configuration files required by the service in the container.
> By default, the configuration files in the ```templates``` directory will be used. If there are corresponding configuration files in the ```conf``` directory, the configuration files in the ```conf``` directory will be used first.

#### /data
```data```: This is the data storage directory for the service/container, you mustn't create any files in the ```data``` directory, because it may cause service/container start failed.

#### /logs
```logs```: This is the log storage directory for the service/container.

## 2. Files

#### /.env
```/.env```: this is the environment variables file.

#### /docker-compose.yml
```/docker-compose.yml```: this is the ```docker-compose.yml``` file.

## 3. Common Commands

### Import a local SQL dump into MySQL

Run the MySQL client inside the container to import a SQL dump from the local machine:

```bash
docker exec -i \
  -e MYSQL_PWD='your-root-password' \
  sparrow_container_test_mysql \
  mysql --default-character-set=utf8mb4 -u root database_name \
  < /Users/xxx/Downloads/sql_dump.sql
```

Replace `your-root-password`, the database name, and the SQL dump path as needed.

