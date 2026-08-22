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

下载架构重构方向：

```
Download API
        |
Download Service
        |
Download Task
        |
Execution Runtime
        |
Scheduler
        |
Backend Provider
        |
Telegram Runtime
        |
Network Plugin
```

当前状态：

- Resource/Search 链路已形成基础闭环。
- Admin、Database、Deployment 基础能力存在。
- 下载子系统组件较完整，但旧执行链职责混乱。
- 下载模块保持名称 `app/download`，不创建 `download_v2`。
- 旧执行实现直接在原模块内替换。
- 所有 Telegram 账号统一使用同一网络策略，不设计账号级独立代理绑定。

---

# 2. 下载系统迁移记录

已删除：

- app/download/manager.py
- app/download/merger.py
- app/download/concurrent_stream.py

原因：

- 无稳定外部依赖；
- 职责由新的 Service / Scheduler / Assembler 结构替代。

保留并演进：

- chunk.py
- range.py
- chunk_manager.py
- providers.py
- resource_resolver.py
- factory.py
- cache 相关组件

---

# 3. 当前确认问题

- ConcurrentChunkStream 与 ChunkScheduler 接口错误。
- Telegram client 创建入口分叉。
- 下载加速链路未形成统一生产路径。
- AccountSelector 缺少速度、负载、失败状态调度。
- ResourceResolver 与具体 backend 耦合，需要抽象 ResourceLocation。
- ChunkMerger 缺少完整性校验。
- Provider 接口仍暴露 Telegram 细节。
- NetworkPlugin 当前主要服务于 Telegram client 创建阶段，需要与下载策略进一步解耦。

---

# 4. 网络策略决策

已确定：

- 所有 Telegram 账号共享同一网络策略。
- Proxy 不设计为账号级独立配置。
- NetworkPlugin 保留系统级热插拔能力。

目标：

```
System Network Plugin
        |
        v
Telegram Runtime
        |
        v
All Accounts
```

---

# 审查记录

已完成：

- .github/workflows
- alembic
- tests
- docker
- scripts
- requirements
- app/download 架构审查
- Telegram Runtime → Network Plugin → Download Backend 边界审查
- 下载旧代码引用扫描
- 第一阶段迁移删除
