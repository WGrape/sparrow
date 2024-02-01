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


