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
Chunk Scheduler
        |
Account Pool
        |
Telegram Runtime
        |
Network Plugin
```

当前架构状态：

- Resource 搜索链路已形成基础闭环。
- Admin API 已提供账号、Source、Resource、Network 管理基础。
- 下载组件已存在 Chunk、Stream、Runtime 抽象，但多账号加速主链路仍未完全闭环。
- 生产部署已具备 Docker Compose、数据库迁移入口和可选 proxy 容器。
- CI、pytest、Alembic 均已确认存在。
- scripts/index_telegram_source.py 已接入 runtime_registry/get_provider，不属于旧式直连客户端路径。
- scripts/list-account-dialogs.py 仍存在直接 TelegramClient 创建路径，需要后续统一。
- requirements-dev.txt 已确认存在，包含 pytest、pytest-asyncio、pytest-cov、ruff、mypy 等开发工具链。

---

# 2. 已实现功能

已确认：

- Telegram Client Pool 基础抽象
- Telegram Client Provider
- Telegram Runtime 生命周期管理
- Network Plugin 加载入口
- Client authorization 检查
- 多账号查询能力
- Chunk 基础拆分
- Chunk Scheduler 基础结构
- Chunk Merger 基础结构
- HTTP Range 下载接口
- Admin API
- Admin Frontend 基础页面
- Alembic migration
- GitHub Actions CI
- pytest 测试基础设施
- Docker production compose
- entrypoint 自动执行 migration
- scripts/index_telegram_source.py 使用 Runtime Provider 执行索引
- requirements-dev 开发测试依赖体系

---

# 3. 存在的问题

## P0

### Telegram client 创建入口分叉

旧 client 创建路径可能绕过 Runtime 和 Network Plugin。

新增确认：

`scripts/list-account-dialogs.py` 直接调用 `TelegramClient(...)`，需要后续改造为统一 Provider。

---

### 下载加速链路未完全闭环

目标：

```
Resource
 |
Chunk Scheduler
 |
Account Pool
 |
Workers
 |
Chunk Merger
```

缺少完整调度闭环。

---

### ConcurrentChunkStream 接口风险

需要修正接口一致性并增加测试。

---

## P1

- ChunkMerger 完整性校验不足。
- ResourceResolver 限制多账号下载策略。
- Network Plugin 缺少 Account Network Profile 闭环。
- Download API 与 DownloadManager 职责边界需要收敛。
- Admin 权限模型需要从 API Key 扩展到资源级权限。
- 搜索能力需要长期全文检索方案。
- CI 已存在，但需要增加 lint/static analysis。
- 测试存在，但核心下载加速路径覆盖不足。
- docker proxy 容器存在，但与 NetworkPlugin runtime 关联仍需验证。

---

# 审查记录

## 当前补充审查

范围：

- .github/workflows
- alembic/
- tests/
- docker-compose.prod.yml
- docker-entrypoint.sh
- scripts/
- requirements.txt
- requirements-dev.txt

结论：

- CI 基础存在，不再认为项目缺少 CI。
- pytest 基础设施存在，测试覆盖方向已确认。
- Alembic migration 存在，数据库演进机制已建立。
- production compose 存在。
- proxy 使用可选 profile。
- entrypoint 使用 Alembic upgrade head。
- scripts/index_telegram_source.py 遵循 Runtime Provider 架构。
- scripts/list-account-dialogs.py 仍需要迁移到统一 Runtime 架构。
- requirements-dev.txt 提供测试与静态检查工具，但需确认 CI 是否实际执行这些检查。

仍需补充：

- tests/download 深度覆盖
- Chunk Scheduler
- ConcurrentChunkStream
- 多账号并行下载
- Network Plugin runtime switching
- 最终架构复盘

---

## 下一步审查范围

- tests 深度审查
- 最终架构复盘
- 修复计划重新制定
