# tgStorage 项目审查记忆

> 持续代码审查记录。用于记录架构、功能和问题状态。

状态流转：

发现 → 确认 → 修复中 → 已修复 → 测试通过

---

# 1. 项目架构

当前核心链路：

```
Telegram Source
        |
Indexer
        |
Resource Metadata
        |
Search API
        |
Web Frontend
```

下载目标架构：

```
Download API
        |
Download Manager
        |
Download Engine
        |
Chunk Scheduler
        |
Account Pool
        |
Telegram Runtime
        |
Network Plugin
```

当前状态：

- Resource 搜索链路已形成基础闭环。
- Admin、Database、Deployment 基础能力存在。
- 下载子系统组件较完整，但职责边界未稳定。
- 未来下载子系统倾向直接重写，不继续在旧链路上无限修补。

---

# 2. 下载系统逆向审查结论

## 可保留设计思想

- ResourceResolver 作为资源定位抽象。
- AccountSelector 作为账号选择入口。
- ChunkRange / ChunkManager 的分片思想。
- DownloadRuntime / Engine 的策略隔离方向。
- Factory 负责 provider 装配的方向。
- Provider 抽象方向。
- Message cache adapter 解耦方向。

## 需要重写

- ConcurrentChunkStream 调度实现。
- ChunkScheduler 与 Worker 的接口设计。
- DownloadManager 到 Chunk Engine 的生产链路。
- Account 调度策略。
- ChunkMerger 完整性处理。
- Telegram backend 直接绑定的执行接口。

## 当前确认问题

- ConcurrentChunkStream 调用 ChunkScheduler 接口不一致。
- DownloadManager 未形成完整加速链路。
- DownloadEngine 存在但未确认进入主路径。
- AccountSelector 只有 enabled 检查，没有速度、负载、失败状态调度。
- ResourceResolver 与 Telegram backend 耦合，需要抽象 ResourceLocation。
- ChunkMerger 只能保证排序，不能保证数据完整性。
- providers.py 抽象存在，但接口仍暴露 Telegram 细节。
- merger.py 与 chunk_merger.py 存在重复职责。

---

# 3. 已实现功能

已确认：

- Telegram Runtime 基础抽象
- Network Plugin 加载入口
- Resource/Search 链路
- Admin API
- Alembic migration
- GitHub Actions
- pytest 基础设施
- Docker production compose
- Download HTTP Range
- Download contract tests
- Chunk 基础组件

---

# 4. 存在的问题

## P0

- ConcurrentChunkStream 与 ChunkScheduler 接口错误。
- Telegram client 创建入口分叉。
- 下载加速链路未形成统一生产路径。

## P1

- ChunkMerger 缺少完整性校验。
- AccountSelector 缺少动态调度能力。
- ResourceResolver 与具体 backend 耦合。
- DownloadManager / Engine / Scheduler 边界需要重新设计。
- 核心 Chunk 调度路径缺少测试覆盖。
- Network Plugin 与 Account Profile 未闭环。
- Provider 接口需要升级为通用 Backend 接口。
- Merger 存在重复实现。

---

# 审查记录

已完成：

- .github/workflows
- alembic
- tests
- docker
- scripts
- requirements
- app/download 初步逆向架构审查

当前继续：

- app/download 剩余模块审查
- 输出 KEEP / REWRITE / DELETE 分类
- 设计 download v2 架构
