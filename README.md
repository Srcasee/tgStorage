# tgStorage

## 项目定位

tgStorage 是基于 Telegram 作为存储后端的资源管理系统。

## 当前架构检查记录

当前 Telegram 下载与运行时架构已经完成核心解耦：

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

已确认完成：

- Telegram Client Runtime 生命周期管理
- Network Plugin Runtime 接入
- 多账号 Client 管理基础能力
- Download Provider 抽象
- Chunk Range 下载接口设计

当前开发阶段：

- Telegram File Provider Adapter
- 下载调度优化
- Chunk 并发下载能力

架构扩展方向：

当前设计保留未来升级路径：

```
单机多账号
      ↓
多 Worker
      ↓
分布式下载调度
```

无需改变 Resource API 和 Download 抽象即可扩展。

## 核心原则

- 保留 FastAPI
- 保留 Telegram Connector
- 保留轻量部署路线
- 优先保持模块解耦
- 逐步增强下载能力
