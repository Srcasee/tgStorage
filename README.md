# tgStorage

## 项目定位

tgStorage 是基于 Telegram 作为存储后端的资源管理系统。

核心链路：

```
Telegram Storage Source
        ↓
Indexer / Metadata
        ↓
Resource API
        ↓
Web Frontend
        ↓
Search / Download / Preview
```

核心目标：

1. Telegram 存储源 → API → 系统识别 → Web → 用户搜索、下载
2. 管理员 Web 后台管理账号、来源、资源和分类
3. Proxy / Network 作为可选热插拔插件
4. 最大化利用多账号、多连接提升 Telegram 下载能力
5. 保持系统轻量，部署简单

---

## 当前架构状态

已完成：

- Telegram Connector
- 多账号基础支持
- Resource Indexer
- FastAPI API Gateway
- Search API
- Streaming Download
- Admin API
- Network Plugin 基础抽象
- Docker / Alembic / CI 工程修复

当前进入升级阶段：

- Network Plugin Runtime 接入
- 下载调度优化
- Web Admin 完善

---

## 升级路线

### Phase 0 - 工程基础

状态：完成

- Docker 部署优化
- Alembic migration 修复
- SQLite migration 兼容
- CI 测试完善

### Phase 1 - 核心资源系统

目标：

Telegram → Resource → API → Web

计划：

- 资源识别增强
- 分类规则
- 搜索优化
- 元数据完善

### Phase 2 - 管理后台

目标：

管理员通过 Web 管理：

- Telegram Accounts
- Sources
- Resources
- Categories

### Phase 3 - Network Plugin

目标：

将网络能力插件化：

```
Network Selector
        ↓
Network Plugin
        ↓
Telegram Client
```

支持：

- Direct
- SOCKS5
- HTTP Proxy
- 其他网络适配器

要求：

- 可选启用
- 热插拔
- 多账号独立配置

### Phase 4 - Download Optimization

目标：最大化 Telegram 下载能力。

方向：

- 多账号下载池
- Chunk 并发
- 下载任务恢复
- 速度调度
- 热点缓存

说明：不会绕过 Telegram 服务限制，而是通过合理调度提高实际吞吐。

---

## 部署

目标：

```
docker compose up
```

即可运行。

原则：

- 不引入不必要复杂组件
- 保持单机部署简单
- 根据规模选择扩展能力

---

## 开发原则

- 保留 FastAPI
- 保留 Telegram Connector
- 保留轻量前端路线
- 优先修复工程债务
- 再增加核心能力

