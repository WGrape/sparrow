<div align="center" >
    <img width="350" alt="img" src="https://github.com/WGrape/sparrow/assets/35942268/ab3ef3f3-8625-41df-99ed-50edde47a68e">
</div>

<div align="center">
    <p>基于Docker一键创建多种语言环境、多种服务环境的容器化编排工具</p>
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

## 支持的服务列表

添加一个新的服务，请[点击这里](https://github.com/WGrape/sparrow/issues/4)。

<img width="882" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/5bf35edb-7b5f-4407-86e8-f1fcc1815e03">

## 一、介绍
sparrow是基于Docker，用于本地一键创建多种语言环境、多种服务环境的容器化编排工具。

## 二、环境依赖
本项目完全依赖于Docker环境，所以一定要先安装并启动Docker。

## 三、安装和更新

此项目提供了开发版本和Release版本两种不同的安装方式，二者的区别如下，请根据需求的不同自行选择。

- 开发版本 ：项目以高频率的速度更新，所以功能和特性一定是最新的！但是无法避免的会出现些bug，不能保证100%稳定
- Release版本 ：项目在某个时间下发布的一个经过多级测试，且稳定运行一段时间后的版本，在[这里查看](https://github.com/WGrape/sparrow/releases)各个Release版本

### 1、开发版本

#### (1) 安装

如果是首次安装，使用如下命令快速完成安装。

```bash
# 获取项目
git clone https://github.com/WGrape/sparrow.git
cd sparrow

# 执行安装脚本
bash _install.sh

# 查看使用帮助
./sparrow --help
```

#### (2) 更新

在安装后，如果需要更新至最新的开发版本，执行以下命令开始更新。

```bash
bash _update.sh
```

### 2、Release版本

#### (1) 安装

如果需要特定版本的Release包，请[点击这里](https://github.com/WGrape/sparrow/releases)下载，然后执行以下操作

```bash
cd sparrow

# 执行安装脚本
bash _install.sh

# 查看使用帮助
./sparrow --help
```

#### (2) 更新

需要注意的是，Release包不支持更新 ！所以在安装完特定版本的Release包后，请不要执行```bash _update.sh```命令。


## 四、快速使用

### 1、启动

使用如下命令启动整个环境中的所有服务。当然这个```所有服务```是可定义的，它由根目录下```/.env```文件中配置的```ENABLE_SERVICE_LIST```数组变量控制。

```bash
./sparrow start
```

#### (1) 启动某一个服务

如果只需要启动某一个服务，使用如下命令即可，传递的```service```就是在```docker-compose.yml```配置文件中的```services```列表中某一个服务的名称，如```phpfpm/nginx/mysql/redis```等

```bash
./sparrow startone {service_name}
```

#### (2) 测试是否启动成功

使用如下命令，会自动在Chrome中打开对应的网页，如果每一个网页都可以成功打开，则说明安装成功

```bash
bash .work/tests/run.sh
```

### 2、停止

停止整个环境中的所有服务

```bash
./sparrow stop
```

### 3、重启

重启整个环境中的所有服务

```bash
./sparrow restart
```

### 4、更新

当镜像内容需要修改以支持新的需求时，就需要对服务进行更新，其实就是对镜像进行更新

#### (1) 更新一个服务

```bash
./sparrow updateone {service}
```

#### (2) 使用示例

当我们需要把Go版本调整为```1.17.0```（默认为1.21.1）时，使用如下步骤完成

1. 先修改官方镜像 ：把```/.env```文件中的```IMAGE_OFFICIAL_GO_VERSION=1.21.1```修改为```IMAGE_OFFICIAL_GO_VERSION=1.17.0```
2. 再修改basic镜像 ：把```/.env```文件中的```IMAGE_BASIC_GO_VERSION=1.21.1```修改为```IMAGE_BASIC_GO_VERSION=1.17.0```
3. 最后更新go服务 ：执行```./sparrow updateone go```

### 5、监控

如果需要查看sparrow的运行状态和所允许服务的容器信息，使用如下命令即可

```bash
./sparrow status
```

## 五、相关文档

- [Q&A汇总文档](.work/extra/doc/QA.md)
- [DEV开发文档](.work/extra/doc/DEV.md)
- [FEEDBACK反馈文档](.work/extra/doc/FEEDBACK.md)
