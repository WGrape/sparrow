<div align="center" >
    <img width="350" alt="img" src="https://github.com/WGrape/sparrow/assets/35942268/ab3ef3f3-8625-41df-99ed-50edde47a68e">
</div>

<div align="center">
    <p>A Docker tool for one-click startup of multiple services and environments.</p>
</div>

<p align="center">
    <a href="https://www.oscs1024.com/project/oscs/WGrape/sparrow?ref=badge_small" alt="OSCS Status"><img src="https://www.oscs1024.com/platform/badge/WGrape/sparrow.svg?size=small"/></a>
    <img src="https://img.shields.io/badge/dockerdesktop-4.10.0+-red.svg">
    <img src="https://img.shields.io/badge/docker-18.01+-red.svg">
    <img src="https://img.shields.io/badge/dockercompose-1.20.0+-red.svg">
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/wgrape/sparrow">
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg"></a>
    <a href="./README.zh-CN.md"><img src="https://img.shields.io/badge/doc-中文-green.svg"></a>
</p>

## Support Service List

Add a new service, please [click  here](https://github.com/WGrape/sparrow/issues/4).

<img width="882" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/5bf35edb-7b5f-4407-86e8-f1fcc1815e03">


## 1. Introduction
Sparrow is a Docker tool for one-click startup of multiple services and environments.

## 2. Dependencies
This project relies entirely on Docker, so Docker must be installed and running.

## 3. Installation and Update

This project offers two different installation methods: development version and release version. The differences between the two are as follows. Please choose according to your needs:

- Development version: The project updates at a high frequency, so the features and functionalities are always up-to-date! However, there may be some bugs that cannot be avoided, and 100% stability cannot be guaranteed.
- Release version: A version of the project released at a certain point in time, which has undergone multi-level testing and has been running stably for a period of time. You can view various release versions [here](https://github.com/WGrape/sparrow/releases).

### (1) Development version

#### ① Installation

If it's the first time, you can use the following commands to install.

```bash
# get project
git clone https://github.com/WGrape/sparrow.git
cd sparrow

# install
bash _install.sh

# usage help
./sparrow --help
```

#### ② Update

After installation, if you need to update to the latest development version, execute the following command to begin the update.

```bash
bash _update.sh
```

### (2) Release version

#### ① Installation

If you need a specific version of the release package, please [click here](https://github.com/WGrape/sparrow/releases) to download, and then follow these steps.

```bash
cd sparrow

# install
bash _install.sh

# usage help
./sparrow --help
```

#### ② Update

Please note that the release package does not support updates! So after installing a specific version of the release package, please do not execute the ```bash _update.sh``` command.

## 4. Quick Start

### (1) Start

Use the following command to start all services in the entire environment. Of course, this ```all services``` can be defined and is controlled by the ```ENABLE_SERVICE_LIST``` array variable configured in the ```/.env``` file in the root directory.

```bash
./sparrow start
```

#### ① Start a Specific Service

If you only need to start a specific service, you can use the following command. The ```service``` passed in is the name of a service in the ```services``` list in the ```docker-compose.yml``` configuration file, such as ```phpfpm/nginx/mysql/redis```, etc.

```bash
./sparrow startone {service_name}
```

#### ② Test if Startup is Successful

Use the following command, if nothing wrong output, it means the installation is successful.

```bash
bash .work/tests/run.sh
```

### (2) Stop

Stop all services in the entire environment

```bash
./sparrow stop
```

### (3) Restart

Restart all services in the entire environment

```bash
./sparrow restart
```

### (4) Update

When the content of the image needs to be modified to support new requirements, the services need to be updated, which is actually updating the image.

#### ① Update a Service

```bash
./sparrow updateone {service}
```

#### ② Usage Example

When we need to adjust the Go version to ```1.17.0``` (default is 1.21.1), follow these steps:

1. First, modify the official image: change ```IMAGE_OFFICIAL_GO_VERSION=1.21.1``` in the ```/.env``` file to ```IMAGE_OFFICIAL_GO_VERSION=1.17.0```.
2. Then, modify the basic image: change ```IMAGE_BASIC_GO_VERSION=1.21.1``` in the ```/.env``` file to ```IMAGE_BASIC_GO_VERSION=1.17.0```.
3. Finally, update the go service: execute ```./sparrow updateone go```.

### (5) Monitor

If you need to view the running status of sparrow and the container information of the allowed services, you can use the following command.

```bash
./sparrow status
```

## 5. About Documents

- [Q&A Document](.work/extra/doc/QA.md)
- [DEV Document](.work/extra/doc/DEV.md)
- [FEEDBACK Document](.work/extra/doc/FEEDBACK.md)
