<div align="center" >
    <img width="350" alt="img" src="https://github.com/WGrape/sparrow/assets/35942268/ab3ef3f3-8625-41df-99ed-50edde47a68e">
</div>

<div align="center">
    <p><a href="https://github.com/WGrape/sparrow">English</a> / <a href="./README.zh-CN.md">中文</a></p>
    <p><a href="#2-快速开始">快速开始</a> / <a href="#3-更多文档">文档教程</a> / <a href="https://www.ixigua.com/7350725273806963219">视频教程</a></p>
    <p><a href="https://github.com/WGrape/sparrow/blob/main/.work/extra/doc/1.WHY_SPARROW_ZH.md">什么是sparrow？为什么要使用sparrow？</a></p>
    <p>基于Docker一键启动多个服务环境的容器化编排工具</p>
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

> 更详细的使用教程，请查看[使用文档](./.work/extra/doc/2.USAGE_ZH.md)。

<video src="https://github.com/WGrape/sparrow/assets/35942268/bc180f06-fedc-42d2-b21b-f7c7fa1b65ea" width="" height="" controls="controls"></video>

```bash
# 安装
git clone https://github.com/WGrape/sparrow.git
cd sparrow
bash _install.sh

# 启动 / 停止 / 重启所有服务
./sparrow start
./sparrow stop
./sparrow restart

# 操作单个服务
./sparrow startone {service_name}
./sparrow stopone {service_name}

# 启动工作后台
./sparrow web

# 进入容器
./sparrow enter
./sparrow enter {service_name}
```

完整的使用说明（配置、更新、监控、常见问题等），请查看[使用文档](./.work/extra/doc/2.USAGE_ZH.md)。

## 3. 更多文档

- 1.项目背景 ：[English](.work/extra/doc/1.WHY_SPARROW_EN.md) / [中文](.work/extra/doc/1.WHY_SPARROW_ZH.md)
- 2.使用文档 ：[English](.work/extra/doc/2.USAGE_EN.md) / [中文](.work/extra/doc/2.USAGE_ZH.md)
- 3.开发教程 ：[English](.work/extra/doc/3.DEVELOPMENT_EN.md) / [中文](.work/extra/doc/3.DEVELOPMENT_ZH.md)
- 4.如何贡献 ：[English](.work/extra/doc/4.HOW_TO_CONTRIBUTE_EN.md) / [中文](.work/extra/doc/4.HOW_TO_CONTRIBUTE_ZH.md)
- 5.常见问题 ：[English](.work/extra/doc/5.QA_EN.md) / [中文](.work/extra/doc/5.QA_ZH.md)

## 4. 贡献

在使用项目的过程中，如果您有任何的问题和建议可以随时在 [Issues](https://github.com/WGrape/sparrow/issues/new) 中提问，或者在 [Pull Requests](https://github.com/WGrape/sparrow/pulls) 中提交代码。关于代码贡献等，请参考 [如何贡献](./.work/extra/doc/4.HOW_TO_CONTRIBUTE_ZH.md) 文档

<img src="https://contrib.rocks/image?repo=wgrape/sparrow">

## 5. 开源许可证

[MIT](https://opensource.org/licenses/MIT), Copyright (c) 2013-present, [Wgrape](https://github.com/WGrape/)
