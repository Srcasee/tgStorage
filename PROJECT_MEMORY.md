# tgStorage 项目审查记忆

> 持续代码审查记录。

## 1. 项目架构

当前 Telegram 架构：

```
Telegram Client Runtime
        |
Client Provider
        |
Client Pool
        |
Download Provider
        |
Telegram Storage
```

目标下载架构：

```
Download Manager
        |
Account Selector
        |
+---------+---------+
|         |         |
TG A     TG B      TG C
|         |         |
Workers Workers Workers
        |
Chunk Merger
        |
User Stream
```

Network 插件入口已存在：

```
Telegram Runtime Lifecycle
        |
Network Selector
        |
Network Plugins
```

## 2. 已实现功能

已完成：

- Telegram Client Pool 基础抽象
- Database Telegram Client Provider
- 多账号查询能力
- Telegram Runtime 生命周期管理
- Network Plugin 加载入口
- Client authorization 检查
- 账号状态更新

部分完成：

- 多账号并行下载
- 动态账号选择
- Proxy 热插拔完整流程
- 下载速度优化策略

## 3. 存在的问题

### P0

1. Telegram client.py 仍存在旧版实现和新 runtime 架构并存问题。

旧实现直接创建 TelethonClient，并直接注入 proxy，可能绕过新的 Network Plugin 架构。

2. 多账号目前主要用于选择 client，而未接入 chunk worker 调度。

需要：

- Account Pool
- Worker binding
- Download scheduler integration

### P1

1. ClientPool 缺少：

- 负载统计
- 下载速度统计
- 错误次数
- 自动降级

2. Network Plugin 虽有 lifecycle 接入，但需要继续检查实际 provider 使用链路。

3. 需要统一 Telegram client 创建入口，避免旧代码和新架构分叉。

## 审查记录

### 第二次审查

范围：

- app/telegram/client.py
- app/telegram/client_pool.py
- app/telegram/client_provider.py
- app/telegram/lifecycle.py

结论：

Telegram 多账号和网络插件方向已经开始落地，但下载加速仍未形成完整闭环。当前最大风险是旧 client 创建逻辑与新 runtime/provider 架构并存。
