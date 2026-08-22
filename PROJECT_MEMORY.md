# tgStorage 项目审查记忆

> 用于持续代码审查记录。每次审查后更新本文件，直到完成整体代码审计。

## 1. 项目架构

当前目标架构：

```
Telegram Storage Source
        |
 Telegram Client Runtime
        |
 Resource Index / Metadata Layer
        |
        API
        |
 Web Frontend
        |
 User Search / Download / Preview
```

管理链路：

```
Admin Web
    |
Resource Management
    |
Telegram Account Management
    |
Category Management
```

下载链路当前实现：

```
FastAPI Download API
        |
TelegramStreamBackend
        |
TelegramChunkReader
        |
RuntimeTelegramFileProvider
        |
Telegram Client
        |
Telegram Storage
```

核心模块：

- api: HTTP API 层
- download: 下载引擎、chunk、stream、scheduler 抽象
- telegram: Telegram runtime/client 管理
- admin: 管理后台
- cache: 消息及媒体缓存
- models/services: 业务模型与服务层

目标扩展架构：

```
Download Manager
        |
 Chunk Scheduler
        |
 +-------------+-------------+
 |             |             |
TG Account A TG Account B TG Account C
 |             |             |
Workers     Workers      Workers
        |
 Chunk Merger
        |
 User Stream
```

Proxy/network 目标架构：

```
Telegram Client
       |
 Network Plugin Interface
       |
 +---------+----------+----------+
 Direct   SOCKS5     HTTP Proxy
```

---

## 2. 已实现功能

### 已完成

- Telegram 文件 Provider 抽象
- Telegram Runtime Client 接入
- Resource API 基础能力
- Download Streaming 基础能力
- HTTP Range 下载基础支持
- Chunk Reader
- Chunk Scheduler 基础结构
- Chunk Merger 基础结构
- Concurrent Stream 基础结构
- Download Runtime/Factory 基础结构
- Telegram 多账号方向设计
- Admin 后台基础目录
- 数据库迁移体系
- Docker 部署体系

### 部分完成

- 多账号并行下载
- 下载调度优化
- Proxy 插件系统
- 资源分类管理
- 用户 Web 前端
- 搜索体验

---

## 3. 当前存在的问题

### P0

1. 下载链路仍偏向单账号直接流式读取。

需要进一步接入：

- Download Manager
- Chunk Scheduler
- Multi Account Worker
- Retry/Resume

2. StreamingResponse 生命周期风险。

需要检查：

- 数据库 session 生命周期
- 长连接释放
- 下载取消清理

3. Telegram 资源异常处理不足。

需要完善：

- deleted message
- missing media
- Telegram API error


### P1

1. Proxy 插件化未完整落地。

需要：

- NetworkPlugin interface
- Plugin registry
- 热插拔机制
- Direct/SOCKS5/HTTP 支持

2. Resource Domain 需要增强。

需要：

- 分类
- 标签
- 搜索索引
- 账号维度管理

3. 用户 Web 产品层不足。

需要：

- 搜索页面
- 下载页面
- 资源详情

---

## 审查记录

### 第一次审查

范围：

- download/telegram_file_provider.py
- download/telegram_reader.py
- download/telegram.py
- api/download.py

结论：

当前架构方向符合 TG 云存储系统目标，但下载加速、多账号并发、网络插件、用户产品层仍未完成。

后续审查继续更新本文件。
