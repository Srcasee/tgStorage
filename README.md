# tgStorage

## 项目定位

tgStorage 是基于 Telegram 作为存储后端的资源管理系统。

## 当前架构检查记录

当前 Telegram 下载与运行时架构：

```
Telegram Runtime
        ↓
Telegram Client Provider
        ↓
Telegram Client
        ↓
Telegram File Provider
        ↓
Download Backend
        ↓
Chunk Reader
```

已完成：

- Telegram Connector
- Telegram Client Runtime 生命周期管理
- Network Plugin Runtime 接入
- 多账号 Client 管理基础能力
- Download Provider 抽象
- Chunk Range 下载接口设计
- Docker / Alembic / CI 工程修复

当前开发阶段：

- Telegram File Provider Adapter
- 下载调度优化
- Chunk 并发下载能力
- Web Admin 完善

## 扩展路线

当前设计保留未来扩展能力：

```
单机多账号
        ↓
多 Worker
        ↓
分布式下载调度
```

未来扩展无需改变 Resource API 与 Download 抽象。

## 开发原则

- 保留 FastAPI
- 保留 Telegram Connector
- 保留模块解耦
- 优先修复工程债务
- 再增加核心能力
