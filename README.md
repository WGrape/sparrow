# sparrow
基于Docker一键创建多种语言环境、多种服务环境的容器化编排工具

## 一、介绍
sparrow是基于Docker，用于本地一键创建多种语言环境、多种服务环境的容器化编排工具。

## 二、环境依赖
本项目完全依赖于Docker，所以一定要先安装和开启Docker。

## 三、安装和更新

### 1、安装

如果是首次使用，使用如下命令快速完成安装。

```bash
git clone https://github.com/WGrape/sparrow.git
cd sparrow

# 执行安装脚本
bash _install.sh

# 查看使用帮助
./sparrow --help
```

### 2、更新

在安装后，如果需要更新至最新版本，执行以下命令开始更新。

```bash
bash _update.sh
```

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

### (1) 更新一个服务

```bash
./sparrow updateone {service}
```

### (2) 使用示例

当我们需要把Go版本调整为```1.17.0```（默认为1.21.1）时，使用如下步骤完成

1. 先修改官方镜像 ：把```/.env```文件中的```IMAGE_OFFICIAL_GO_VERSION=1.21.1```修改为```IMAGE_OFFICIAL_GO_VERSION=1.17.0```
2. 再修改basic镜像 ：把```/.env```文件中的```IMAGE_BASIC_GO_VERSION=1.21.1```修改为```IMAGE_BASIC_GO_VERSION=1.17.0```
3. 最后更新go服务 ：执行```./sparrow updateone go```

## 五、相关文档

- [Q&A汇总文档](.work/extra/doc/QA.md)
- [DEV开发文档](.work/extra/doc/DEV.md)
