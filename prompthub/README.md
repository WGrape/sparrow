## Usage

> [deepset-ai/prompthub](https://github.com/deepset-ai/prompthub)

A prompt includes the ```markdown``` file and the ```yaml``` file. You can copy ```templates/deepset-zero-shot-react.yaml``` and ```templates/deepset-zero-shot-react.yaml``` files to ```./prompthub/data```.

When you start ```prompthub```, just add your own ```prompts``` to ```./prompthub/data``` directory. 

```bash
curl -i -H 'Accept: application/json' 127.0.0.1:4100/prompts
```

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

