# tgStorage 项目审查记忆

> 持续代码审查记录。用于记录架构、功能和问题状态。

状态流转：发现 → 确认 → 修复中 → 已修复 → 测试通过

---

# 1. 项目架构

当前核心架构：

```
Telegram
   |
Telegram Source
   |
Indexer
   |
Resource Metadata
   |
Database
   |
+----------------+
|                |
Search API   Download API
                  |
            Telegram Runtime
                  |
        Account Pool / Network Layer
```

目标下载加速架构：

```
Download API
      |
Download Manager
      |
Chunk Scheduler
      |
Account Pool
      |
+------+------+
TG A  TG B  TG C
      |
Workers
      |
Chunk Merger
      |
User Stream
```

Network目标：

```
Account
   |
Network Profile
   |
Network Selector
   |
Network Plugin
   |
Telegram Client Runtime
```

---

# 2. 已实现功能

## 已确认实现

- Telegram Client Pool 基础抽象
- Telegram Runtime 生命周期管理
- Client Provider
- 多账号基础模型
- Network Plugin 基础入口
- Indexer 增量扫描能力
- Resource Identity 设计
- Search API 基础能力
- Download API Range 支持
- Admin API 基础能力
- Admin Frontend 基础验证页面
- Alembic migration体系
- GitHub Actions CI 基础流程

## 部分完成

- 多账号并行下载
- 下载调度
- Proxy热插拔闭环
- 完整管理员后台
- 用户级权限模型
- 高级搜索

---

# 3. 存在的问题

## P0

### Download API 未完全接入 DownloadManager

状态：确认

当前下载路径仍存在直接构造 Telegram streaming path 的风险。

目标：

Download API → DownloadManager → Scheduler → Account Pool → Telegram Runtime

---

### Telegram Client 创建路径需要统一

状态：确认

需要避免旧 client 创建方式绕过 Runtime/Network Plugin。

---

### ConcurrentChunkStream 接口一致性问题

状态：确认

需要修正 Scheduler 与 Stream 调用契约并增加测试。

---

## P1

### 多账号加速缺少调度指标

需要：

- speed
- active tasks
- failures
- network quality

---

### Network Plugin 与账号绑定模型不足

需要引入 Network Profile 层。

---

### Admin权限模型不足

当前主要为 API Key 管理，需要扩展 Role/Permission/Resource Scope。

---

### 数据库schema治理需要继续确认

已确认：

- Alembic存在
- migration链完整

仍需确认：

- runtime schema初始化是否与Alembic重复
- models与migration一致性

---

### 测试覆盖不足

CI存在，但需要增加：

- Download测试
- Telegram Runtime测试
- Indexer测试
- API测试
- Admin权限测试

---

# 审查记录

## 已完成

- app/download
- app/telegram
- app/network
- app/models
- app/indexer
- app/search
- app/api
- app/admin
- app/frontend
- app/config/auth
- database
- deployment基础
- CI
- Alembic

## 补充审查发现

### CI修正

之前判断不存在CI，已修正。

实际存在：

- .github/workflows/test.yml
- pytest基础配置
- Alembic检查

正确结论：

CI存在，但业务回归测试不足。

### Migration修正

之前判断缺少migration，已修正。

实际存在Alembic迁移链：

- initial schema
- source identity
- scanner cursor
- resource identity
- resource relations

当前关注点变为schema治理一致性。
