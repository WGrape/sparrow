> Since dify relies on too many services, the difylocal service will have the following characteristics, which are different from other services.
> 1. ```difylocal``` only provides the nodejs and python environment for running dify, and does not have any other dependencies.
> 2. you should clone dify to ```difylocal/data```, and run it by source code: https://docs.dify.ai/v/zh-hans/getting-started/install-self-hosted/local-source-code
>
> ![image](https://github.com/WGrape/sparrow/assets/35942268/5f12c6c5-3e2e-497f-a257-4888439a9b9f)


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

### (2)Not commit to Git.

#### /data
```data```: This is the data storage directory for the service/container, you mustn't create any files in the ```data``` directory, because it may cause service/container start failed.

#### /logs
- ```logs```: This is the log storage directory for the service/container.

## 2. Files

#### /.env
```/.env```: this is the environment variables file.

#### /docker-compose.yml
```/docker-compose.yml```: this is the ```docker-compose.yml``` file.

