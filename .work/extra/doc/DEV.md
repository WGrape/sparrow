# DEV Doc

## 1. How to upload image

### (1) upload a basic image

Assuming there is a service named ```etcd``` locally, with the image name ```sparrow-basic-etcd``` and version ```3.5.0```. If you want to upload this image to Docker Hub, you need to use the following commands

```bash
./sparrowtool upload -t basic -s etcd -v 3.5.0
```

It must be noted that after upload, the version of the remote image may not be the same as the local version.

- local image version: ```3.5.0```
- remote image version: ```1.0.{{timestamp}}```

![image](https://github.com/WGrape/lexer/assets/35942268/0c8b2850-940b-4d38-b307-e5508b1df9fe)

In order to prevent the remote image version from being mistakenly replaced, if you want to upload a version same to the local one, you must use the ```-r``` option, it means ```replace```, such as ```-r true```.

```bash
./sparrowtool upload -t basic -s etcd -v 3.5.0 -r true
```

This way, there will be a remote image with version ```3.5.0```.

![image](https://github.com/WGrape/lexer/assets/35942268/60b3fc54-2535-4319-83d5-1f7b0dc4a37c)

### (2) upload a app image

The usage is the same as above, not repeated here.

```bash
./sparrowtool upload -t app -s etcd -v latest

./sparrowtool upload -t app -s etcd -v latest -r true
```

## 2. How to create new service

### (1) use sparrowtool

You can use the ```sparrowtool``` to create new service. If you want to create a ```jupyter``` service, you can use this command bellow.

```bash
# if you forget command, for help.
./sparrowtool --help

./sparrowtool new -t service -s jupyter -p 8888
```

After a successful execution, there will be a directory named ```./jupyter``` under the project root directory.

### (2) modify your service configuration.

You must modify these image variables in ```./jupyter/.env``` file as bellow.

- ```IMAGE_OFFICIAL_JUPYTER_NAME```: the official image name
- ```IMAGE_OFFICIAL_JUPYTER_VERSION```: the official image version
- ```IMAGE_BASIC_JUPYTER_VERSION```: the basic image name.
- ```IMAGE_APP_JUPYTER_VERSION```: the app image name.

These are must modify variables, if you have another demand, you can modify more in the ```./jupyter``` directory.

### (3) add your service to ENABLE_SERVICE_LIST in /.env file.

The ```ENABLE_SERVICE_LIST``` variables is defined in ```/.env``` file, you should add ```jupyter``` the new service to the variable.

```
ENABLE_SERVICE_LIST=("xxx" "xxx" "jupyter")
```
