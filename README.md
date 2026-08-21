# tgStorage

## 项目定位

tgStorage 是基于 Telegram 作为存储后端的资源管理系统。

## Telegram 下载架构

当前稳定运行路径：

```
Telegram Runtime
        ↓
Telegram Client Provider
        ↓
RuntimeTelegramFileProvider
        ↓
TelegramChunkReader
        ↓
TelegramStreamBackend
        ↓
Download API
```

## 当前稳定阶段

已完成：

- Telegram Client Runtime 生命周期管理
- Network Plugin Runtime 接入
- 多账号 Client 管理基础能力
- Telegram File Provider 抽象
- Runtime Telegram File Provider 接入
- Chunk Range 下载接口设计
- Chunk Scheduler 基础能力
- Telegram Chunk Worker Adapter
- Ordered Chunk Merger
- Concurrent Chunk Stream 抽象
- Download Strategy Selector
- Download Engine 抽象

## Legacy 路径清理

旧版直接下载路径已移除：

```
TelegramDownloader
TelethonFileProvider
```

当前所有下载请求统一通过：

```
TelegramFileProvider Protocol
```

保持上层下载逻辑与 Telegram 实现解耦。

## 当前回滚状态

并发下载 API 最终接线阶段已暂停，代码恢复至稳定架构节点：

```
23066fe
feat: assemble download runtime factories
```

保留已完成的抽象层设计，不启用未完成的 API 路由切换。

## 分布式下载扩展路线

当前抽象仍保留未来扩展能力：

```
单机多账号
        ↓
多 Worker
        ↓
分布式下载调度
        ↓
Remote Chunk Provider
```

未来增加远程 Worker 时，只需新增 Provider 实现，不需要修改 Resource API、Chunk Reader 或 Download API。

## 开发原则

- 保留 FastAPI
- 保留 Telegram Connector
- 保持模块解耦
- Provider 优先于具体实现依赖
- 优先修复工程债务
- 再增加核心能力
