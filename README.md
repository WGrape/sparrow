<div align="center" >
    <img width="350" alt="img" src="https://github.com/WGrape/sparrow/assets/35942268/ab3ef3f3-8625-41df-99ed-50edde47a68e">
</div>

<div align="center">
    <p><a href="https://github.com/WGrape/sparrow">English</a> / <a href="./README.zh-CN.md">中文</a></p>
    <p>A Docker tool for one-click startup of multiple services.</p>
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

## 1. Support services

Add a new service, please [click  here](https://github.com/WGrape/sparrow/issues/4).

<img width="882" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/5bf35edb-7b5f-4407-86e8-f1fcc1815e03">

## 2. Quick start

> Here is a quick usage example. You can check [Usage Document](.work/extra/doc/2.USAGE_EN.md) for detailed tutorials.

### (1) Installation

You can use the following commands to install.

```bash
# get project
git clone https://github.com/WGrape/sparrow.git
cd sparrow

# install
bash _install.sh

# usage help
./sparrow --help
```

> If you encounter some syntax errors while using the ```./sparrow xxx``` command, please try to run with bash ```bash ./sparrow xxx``` command. Check the [Q&A Document](.work/extra/doc/5.QA_EN.md) for more help. 

### (2) Start

Use the following command to start all services in the entire environment. Of course, this ```all services``` can be defined and is controlled by the ```ENABLE_SERVICE_LIST``` array variable configured in the ```/.env``` file in the root directory.

```bash
./sparrow start
```

If you only need to start a specific service, you can use the following command. The ```service``` passed in is the name of a service in the ```services``` list in the ```docker-compose.yml``` configuration file, such as ```phpfpm/nginx/mysql/redis```, etc.

```bash
./sparrow startone {service_name}
```

### (3) Stop

Stop all services in the entire environment

```bash
./sparrow stop
```

The same, if you only need to stop a specific service, you can use the following command.

```bash
./sparrow stopone {service_name}
```

### (4) Restart

Restart all services in the entire environment

```bash
./sparrow restart
```

### (5) Update a Service

When a service needs to be updated, such as when its image content needs to be modified, the service (image) needs to be updated after making the modifications. After modifying it manually, use the following command to update it.

```bash
./sparrow updateone {service_name}
```

## 3. More documents

- 1.Project Background ：[English](.work/extra/doc/1.WHY_SPARROW_EN.md) / [中文](.work/extra/doc/1.WHY_SPARROW_ZH.md)
- 2.Usage Document ：[English](.work/extra/doc/2.USAGE_EN.md) / [中文](.work/extra/doc/2.USAGE_ZH.md)
- 3.Development Document ：[English](.work/extra/doc/3.DEVELOPMENT_EN.md) / [中文](.work/extra/doc/3.DEVELOPMENT_ZH.md)
- 4.How to contribute ：[English](.work/extra/doc/4.HOW_TO_CONTRIBUTE_EN.md) / [中文](.work/extra/doc/4.HOW_TO_CONTRIBUTE_ZH.md)
- 5.Q&A Document ：[English](.work/extra/doc/5.QA_EN.md) / [中文](.work/extra/doc/5.QA_ZH.md)

## 4. Contributions
During the use of the project, if you have any questions or suggestions, please submit [issues](https://github.com/WGrape/ngxway/issues/new) or [pull requests](https://github.com/WGrape/ngxway/pulls) any time. About Contribution，please check [How to Contribute](./.work/extra/doc/4.HOW_TO_CONTRIBUTE_EN.md) document.

<img src="https://contrib.rocks/image?repo=wgrape/ngxway">

## 5. License

[MIT](https://opensource.org/licenses/MIT), Copyright (c) 2013-present, [Wgrape](https://github.com/WGrape/)
