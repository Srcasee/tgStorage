# tgStorage

## 当前架构检查记录

Telegram Runtime、Network Plugin 与 Download 抽象层已完成阶段性整合。

当前目标：补齐 Telegram File Provider Adapter，将 Telegram Client 生命周期与下载流连接。

当前设计：

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

- Telegram Client Runtime 生命周期管理
- Network Plugin Runtime 注入
- 多账号 Client 管理基础能力
- Download Provider 抽象
- Chunk Range 下载接口

进行中：

- Telegram File Provider Adapter
- 下载调度优化
- Chunk 并发下载

未来扩展路线保持：

```
单机多账号
        ↓
多 Worker
        ↓
分布式下载调度
```

当前架构不会改变 Resource API 和 Download 抽象。
