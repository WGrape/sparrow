<div align="center" >
    <img width="350" alt="img" src="https://github.com/WGrape/sparrow/assets/35942268/ab3ef3f3-8625-41df-99ed-50edde47a68e">
</div>

<div align="center">
    <p><a href="https://github.com/WGrape/sparrow">English</a> / <a href="./README.zh-CN.md">中文</a></p>
    <p>基于Docker一键启动多个服务环境的容器化编排工具</p>
    <p><a href="https://github.com/WGrape/sparrow/blob/main/.work/extra/doc/1.WHY_SPARROW_ZH.md">什么是sparrow？为什么要使用sparrow？</a></p>
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

## 1. 支持的服务列表

添加一个新的服务，请[点击这里](https://github.com/WGrape/sparrow/issues/4)。

<!-- <img width="882" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/5bf35edb-7b5f-4407-86e8-f1fcc1815e03"> -->

<!-- <img width="882" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/0294fc18-2714-466f-898a-61dac573c479"> -->

<img width="880" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/52d3a44c-5b89-4847-996e-ebef00a4a107">

## 2. 快速开始

> 下面是快速使用的简单例子，请点击[使用文档](./.work/extra/doc/2.USAGE_ZH.md)查看更多详细教程。

### (1) 安装

使用如下命令快速完成安装。

```bash
# 获取项目
git clone https://github.com/WGrape/sparrow.git
cd sparrow

# 执行安装脚本
bash _install.sh
```

在安装成功后，项目根目录下会自动生成一个```.env```配置文件，它是sparrow的唯一且统一的配置入口，可以查看它的[示例文件](./.env.template)，在这里你可以修改服务版本、容器命名空间等。

> 1、如果使用```./sparrow xxx```命令时出现语法错误，请尝试使用bash运行```bash ./sparrow xxx```
>
> 2、在安装过程中会提示输入```DOCKERHUB_REPO```，用于配置自己的sparrow镜像的远程仓库。它的默认值是[docker.io/lvsid](https://hub.docker.com/repositories/lvsid)，如果以后需要修改，直接修改```/.env```配置文件即可
>
> 3、如需要帮助，请查看 [常见问题](.work/extra/doc/5.QA_ZH.md)

### (2) 启动

使用如下命令启动整个环境中的所有服务。当然这个```所有服务```是可定义的，它由根目录下```/.env```文件中配置的```ENABLE_SERVICE_LIST```数组变量控制。

```bash
./sparrow start
```

如果只需要启动某一个服务，使用如下命令即可，传递的```service```就是在```docker-compose.yml```配置文件中的```services```列表中某一个服务的名称，如```phpfpm/nginx/mysql/redis```等

```bash
./sparrow startone {service_name}
```

### (3) 停止

停止整个环境中的所有服务。

```bash
./sparrow stop
```

同样的如果只需要停止某一个服务，使用如下命令即可

```bash
./sparrow stopone {service_name}
```

### (4) 重启

重启整个环境中的所有服务

```bash
./sparrow restart
```

### (5) 更新一个服务

当某个服务需要更新时，如其镜像内容需要修改，就需要对服务（镜像）进行更新，在自行修改完后，使用如下命令更新

```bash
./sparrow updateone {service_name}
```

## 3. 更多文档

- 1.项目背景 ：[English](.work/extra/doc/1.WHY_SPARROW_EN.md) / [中文](.work/extra/doc/1.WHY_SPARROW_ZH.md)
- 2.使用文档 ：[English](.work/extra/doc/2.USAGE_EN.md) / [中文](.work/extra/doc/2.USAGE_ZH.md)
- 3.开发教程 ：[English](.work/extra/doc/3.DEVELOPMENT_EN.md) / [中文](.work/extra/doc/3.DEVELOPMENT_ZH.md)
- 4.如何贡献 ：[English](.work/extra/doc/4.HOW_TO_CONTRIBUTE_EN.md) / [中文](.work/extra/doc/4.HOW_TO_CONTRIBUTE_ZH.md)
- 5.常见问题 ：[English](.work/extra/doc/5.QA_EN.md) / [中文](.work/extra/doc/5.QA_ZH.md)

## 4. 贡献

在使用项目的过程中，如果您有任何的问题和建议可以随时在 [Issues](https://github.com/WGrape/ngxway/issues/new) 中提问，或者在 [Pull Requests](https://github.com/WGrape/ngxway/pulls) 中提交代码。关于代码贡献等，请参考 [如何贡献](./.work/extra/doc/4.HOW_TO_CONTRIBUTE_ZH.md) 文档

<img src="https://contrib.rocks/image?repo=wgrape/ngxway">

## 5. 开源许可证

[MIT](https://opensource.org/licenses/MIT), Copyright (c) 2013-present, [Wgrape](https://github.com/WGrape/)
