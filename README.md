<div align="center" >
    <img width="350" alt="img" src="https://github.com/WGrape/sparrow/assets/35942268/ab3ef3f3-8625-41df-99ed-50edde47a68e">
</div>

<div align="center">
    <p><a href="https://github.com/WGrape/sparrow">English</a> / <a href="./README.zh-CN.md">中文</a></p>
    <p><a href="#2-quick-start">Quick Start</a> / <a href="#3-more-documents">Documents</a> / <a href="https://www.ixigua.com/7350725273806963219">Videos</a></p>
    <p><a href="https://github.com/WGrape/sparrow/blob/main/.work/extra/doc/1.WHY_SPARROW_EN.md">What is sparrow and why should we use sparrow?</a></p>
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

<!-- <img width="882" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/5bf35edb-7b5f-4407-86e8-f1fcc1815e03"> -->

<!-- <img width="882" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/0294fc18-2714-466f-898a-61dac573c479"> -->

<img width="880" alt="image" src="https://github.com/WGrape/sparrow/assets/35942268/52d3a44c-5b89-4847-996e-ebef00a4a107">

## 2. Quick start

> For detailed tutorials, check the [Usage Document](.work/extra/doc/2.USAGE_EN.md).

<video src="https://github.com/WGrape/sparrow/assets/35942268/bc180f06-fedc-42d2-b21b-f7c7fa1b65ea" width="" height="" controls="controls"></video>

<img width="2554" height="1084" alt="Image" src="https://github.com/user-attachments/assets/542cc16d-3aa6-41c8-8412-27f35cd018bb" />

```bash
# Install
git clone https://github.com/WGrape/sparrow.git
cd sparrow
bash _install.sh

# Start / Stop / Restart all services
./sparrow start
./sparrow stop
./sparrow restart

# Operate a single service
./sparrow startone {service_name}
./sparrow stopone {service_name}

# Start web dashboard
./sparrow web

# Enter container
./sparrow enter
./sparrow enter {service_name}
```

For full usage details (configuration, update, monitor, Q&A, etc.), see the [Usage Document](.work/extra/doc/2.USAGE_EN.md).

## 3. More documents

- 1.Project Background ：[English](.work/extra/doc/1.WHY_SPARROW_EN.md) / [中文](.work/extra/doc/1.WHY_SPARROW_ZH.md)
- 2.Usage Document ：[English](.work/extra/doc/2.USAGE_EN.md) / [中文](.work/extra/doc/2.USAGE_ZH.md)
- 3.Development Document ：[English](.work/extra/doc/3.DEVELOPMENT_EN.md) / [中文](.work/extra/doc/3.DEVELOPMENT_ZH.md)
- 4.How to contribute ：[English](.work/extra/doc/4.HOW_TO_CONTRIBUTE_EN.md) / [中文](.work/extra/doc/4.HOW_TO_CONTRIBUTE_ZH.md)
- 5.Q&A Document ：[English](.work/extra/doc/5.QA_EN.md) / [中文](.work/extra/doc/5.QA_ZH.md)

## 4. Contributions
During the use of the project, if you have any questions or suggestions, please submit [issues](https://github.com/WGrape/sparrow/issues/new) or [pull requests](https://github.com/WGrape/sparrow/pulls) any time. About Contribution，please check [How to Contribute](./.work/extra/doc/4.HOW_TO_CONTRIBUTE_EN.md) document.

<img src="https://contrib.rocks/image?repo=wgrape/sparrow">

## 5. License

[MIT](https://opensource.org/licenses/MIT), Copyright (c) 2013-present, [Wgrape](https://github.com/WGrape/)
