# Milvus 帮助文档

## 1. 容器内启动了哪些服务

Milvus 以 **Standalone（单机）** 模式运行，容器内包含以下三个组件，全部在同一个进程中启动：

| 组件 | 说明 |
|------|------|
| **Embedded etcd** | 内嵌的 etcd，负责存储 Milvus 的元数据（Collection、Index 等） |
| **Local Storage** | 本地文件存储，负责持久化向量数据（替代 MinIO） |
| **Milvus Server** | 核心服务，提供 gRPC（19530）和 HTTP（9091）两个端口 |

数据目录：
- 元数据（etcd）：`./milvus/data/etcd/`
- 向量数据：`./milvus/data/`

---

## 2. 端口说明

| 宿主机端口 | 容器端口 | 协议 | 用途 |
|-----------|---------|------|------|
| `4100` | `19530` | gRPC | SDK 客户端连接（pymilvus 等） |
| `4101` | `9091` | HTTP | 健康检查 / Metrics / REST API |

---

## 3. 命令行测试

### (1) 健康检查

```bash
curl http://localhost:4101/healthz
# 返回: OK
```

```bash
curl http://localhost:4101/api/v1/health
# 返回: {"status":"ok"}
```

### (2) 查看版本信息

```bash
curl http://localhost:4101/api/v1/health
```

### (3) 查看 Metrics（Prometheus 格式）

```bash
curl http://localhost:4101/metrics
```

### (4) 用 pymilvus（Python SDK）测试连通性

安装 SDK：

```bash
pip install pymilvus
```

测试连接：

```python
from pymilvus import connections, utility

# 连接到 Milvus（gRPC 端口 4100）
connections.connect(host="127.0.0.1", port="4100")

# 检查是否连接成功
print(utility.get_server_version())

# 查看已有 Collection
print(utility.list_collections())
```

### (5) 创建 Collection 并插入向量（完整示例）

```python
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
import random

connections.connect(host="127.0.0.1", port="4100")

# 定义 Schema
fields = [
    FieldSchema(name="id",     dtype=DataType.INT64,        is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
]
schema = CollectionSchema(fields, description="test collection")

# 创建 Collection
col = Collection("test_col", schema)

# 插入随机向量
vectors = [[random.random() for _ in range(128)] for _ in range(10)]
col.insert([vectors])
col.flush()

print(f"插入成功，共 {col.num_entities} 条")
```

---

## 4. Web 管理界面

从 **v2.5.0** 起，Milvus 内置了 Web UI，无需额外安装任何工具。

启动容器后直接访问：

```
http://localhost:4101/webui
```

页面提供以下功能：
- 查看集群实时状态（组件健康、内存、CPU）
- 浏览 Collection / Segment / Channel 信息
- 查看慢查询和系统日志
- 查看各项 Metrics 指标

> v2.4.x 及以下版本无内置 Web UI，需使用第三方工具 [Attu](https://github.com/zilliztech/attu)。

---

## 5. 停止 / 重启

```bash
# 停止
./sparrow stopone milvus

# 重启
./sparrow startone milvus
```
