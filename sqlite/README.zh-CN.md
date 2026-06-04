# SQLite 服务

<sub>[English](./README.md) / [中文](./README.zh-CN.md)</sub>

容器化的 SQLite 环境，自带基于 [sqlite-web](https://github.com/coleifer/sqlite-web) 的 Web 管理界面，并保留标准的 `sqlite3` 命令行。

## 快速开始

```bash
./sparrow startone sqlite
```

然后在浏览器打开：**http://localhost:4700**

## 配置

`sqlite/.env` 中的关键变量：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `SQLITE_HOST_PORT` | `4700` | Web UI 的宿主机端口 |
| `SQLITE_CONTAINER_PORT` | `8080` | 容器内 sqlite-web 端口 |
| `SQLITE_DATA_DIR` | `/var/data/sqlite` | 容器内 db 文件存放路径 |
| `SQLITE_DB_FILE` | `sparrow.db` | 默认数据库文件名 |

## 数据持久化

数据库文件存放在宿主机 `./sqlite/data/`，挂载到容器的 `/var/data/sqlite/`。

## Web UI 功能

- 浏览表与行
- 执行 SQL 查询
- 导入 / 导出数据
- 创建 / 删除表

## 为什么 official 镜像是 `python` 而不是 `sqlite`？

这是这个服务最容易让人困惑的地方。`sqlite/.env` 里这两行——

```env
IMAGE_OFFICIAL_SQLITE_NAME=python
IMAGE_OFFICIAL_SQLITE_VERSION=3.11-slim
```

——并不是配错了，而是 SQLite 的本质决定的有意设计。下面把这条链路讲清楚。

### (1) SQLite 没有"服务进程"，无法直接做成 daemon 容器

绝大多数数据库（MySQL、Redis、Postgres……）都是 **C/S 架构**：跑一个 server 进程在某个端口监听，客户端通过网络连接。所以它们天然适合容器化——把那个 server 进程关在容器里 + 暴露端口即可。

**SQLite 不是这种东西**。SQLite 是一个嵌入式的 **C 库**（`libsqlite3`），它没有任何 server 进程、不监听任何端口、不接受网络连接。使用 SQLite 的方式只有两种：

- 程序静态/动态链接 `libsqlite3`，直接把数据库文件当作本地文件来读写；
- 用命令行工具 `sqlite3` 打开一个 `.db` 文件做交互式操作。

所以**直接把 sqlite 做成一个长期运行的容器是没有意义的**——它没有进程可以"前台保活"，容器一启动就会立刻退出。

### (2) 那这个容器实际上跑的是什么？

跑的是 **`sqlite_web`**——一个用 Python 写的 SQLite **Web 管理界面**（类似 phpMyAdmin 之于 MySQL）。看 `make_app_image/Dockerfile` 最后一行就一目了然：

```dockerfile
CMD sh -c "sqlite_web --host 0.0.0.0 --port ${SQLITE_CONTAINER_PORT} --no-browser ${SQLITE_DATA_DIR}/${SQLITE_DB_FILE}"
```

容器里那个长期保活的进程，就是 `sqlite_web` 这个 Python web server。它在容器内部用 `libsqlite3` 库读写 `sparrow.db` 文件，并通过 HTTP 把内容展示成浏览器可访问的界面。这才是这个容器存在的真正意义。

### (3) 为什么 official 是 `python:3.11-slim`？

因为 `sqlite_web` 是用 **`pip install sqlite-web`** 安装的 Python 包，所以基础镜像必须先有 Python 运行时。我们没有自己从零搭一个 Python 环境，而是直接复用了 Docker Hub 官方的 `python:3.11-slim`——这是最省事、最干净的做法。

`-slim` 这个 tag 表示精简版（约 50MB），只带 Python 运行时和 pip，没有编译工具链，足够 `sqlite_web` 用。

### (4) 那 `sqlite3` 命令是哪来的？

`python:3.11-slim` 自身**不带** `sqlite3` 命令行工具（它只带 Python 标准库里的 `sqlite3` 模块）。所以我们在 `make_basic_image/Dockerfile` 里又额外装了一下：

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir sqlite-web
```

两步：

1. `apt install sqlite3` —— 装 SQLite 的命令行工具，让你 `./sparrow enter sqlite` 后能直接用 `sqlite3 sparrow.db` 进交互式 shell。
2. `pip install sqlite-web` —— 装 Web 管理界面。

至此，basic 镜像同时具备了：Python 运行时 + sqlite3 命令行 + sqlite_web 包。app 镜像再在上面加上 `EXPOSE` 端口、`CMD` 启动命令、目录初始化，就成了最终运行的容器。

### (5) 整体构建链路

```
docker.io/python:3.11-slim          ← official 镜像（Python 运行时）
        │
        │  apt install sqlite3 + pip install sqlite-web
        ▼
sparrow-basic-sqlite:3.11           ← basic 镜像
        │
        │  EXPOSE + CMD sqlite_web ...
        ▼
sparrow-app-sqlite:latest           ← app 镜像
        │
        │  docker compose up
        ▼
sparrow_container_test_sqlite       ← 运行中的容器
   ├── 后台进程：sqlite_web         ← 浏览器从 localhost:4700 访问
   └── 命令行工具：sqlite3          ← ./sparrow enter sqlite 后可用
```

## 命令行使用 sqlite

容器里已经装好了 `sqlite3` 命令，三种方式都可以用：

### 方式 1：进容器（最常用）

```bash
./sparrow enter sqlite
sqlite3 /var/data/sqlite/sparrow.db
sqlite> .tables
sqlite> CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
sqlite> SELECT * FROM users;
sqlite> .quit
```

### 方式 2：宿主机一行命令

```bash
# 单条 SQL
docker exec sparrow_container_test_sqlite \
    sqlite3 /var/data/sqlite/sparrow.db "SELECT name FROM sqlite_master WHERE type='table';"

# 交互式
docker exec -it sparrow_container_test_sqlite \
    sqlite3 /var/data/sqlite/sparrow.db
```

### 方式 3：宿主机直接打开 db 文件（macOS 自带 sqlite3）

因为 `./sqlite/data/` 已经挂载到容器的 `/var/data/sqlite/`，db 文件其实就在宿主机：

```bash
sqlite3 ./sqlite/data/sparrow.db
```

⚠️ **注意**：方式 3 不要和容器里的 `sqlite_web` 同时写同一个 db。SQLite 是文件级锁，并发写会冲突；只读不会有问题。
