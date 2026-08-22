# tgStorage 项目审查记忆

> 持续代码审查记录。用于记录架构、功能和问题状态。

状态流转：

发现 → 确认 → 修复中 → 已修复 → 测试通过

---

# 1. 项目架构

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

Network 插件目标架构：

```
Telegram Runtime Lifecycle
        |
Network Selector
        |
Network Plugins
        |
Telegram Client Runtime
```

---

# 2. 已实现功能

已完成：

- Telegram Client Pool 基础抽象
- Database Telegram Client Provider
- 多账号查询能力
- Telegram Runtime 生命周期管理
- Network Plugin 加载入口
- Client authorization 检查
- 账号状态更新
- Chunk 基础拆分
- Chunk Scheduler 基础结构
- Chunk Merger 基础结构
- Concurrent Stream 基础结构

部分完成：

- 多账号并行下载
- 动态账号选择
- Proxy 热插拔完整流程
- 下载速度优化策略
- 用户搜索和资源管理产品层

---

# 3. 存在的问题

## P0

### 1. Telegram client 创建入口分叉

状态：发现

涉及：

- app/telegram/client.py
- app/telegram/client_provider.py
- app/telegram/lifecycle.py

问题：

旧 client.py 直接创建 TelethonClient 并注入 proxy，可能绕过 Runtime 和 Network Plugin。

需要统一入口。

---

### 2. 多账号没有进入下载加速主链路

状态：发现

当前：

Account → Client → Download

目标：

Resource → Chunk Scheduler → Account Pool → Workers → Chunk Merger

缺少：

- Account Pool
- Worker binding
- Scheduler integration

---

### 3. ConcurrentChunkStream 调用接口错误

状态：发现

位置：

- app/download/concurrent_stream.py
- app/download/chunk_scheduler.py

问题：

ConcurrentChunkStream 调用 Scheduler.execute 参数与实际定义不一致，可能导致运行时 TypeError。

需要修正接口设计后测试。

---

## P1

### 4. ChunkMerger 缺少完整性校验

状态：发现

缺少：

- offset continuity check
- missing chunk detection
- chunk size validation

---

### 5. ResourceResolver 限制多账号加速

状态：发现

当前 Resource 绑定固定 Telegram Source/Account。

目标：

Resource → Source Pool → Account Pool

---

### 6. ClientPool 缺少调度指标

状态：发现

缺少：

- 下载速度
- 当前任务数
- 错误次数
- 网络质量
- 自动降级

---

### 7. DownloadStrategySelector 决策维度不足

状态：发现

当前主要依据文件信息。

未来需要加入：

- 账号数量
- 网络状态
- 历史速度
- proxy 状态

---

### 8. Streaming 生命周期风险

状态：发现

StreamingResponse 与数据库 session、异步下载生命周期需要进一步验证。

---

### 9. Telegram 资源异常处理不足

状态：发现

需要处理：

- message 不存在
- media 不存在
- 删除消息
- 下载中断

---

### 10. Network Plugin 闭环未确认

状态：发现

已有 lifecycle 加载入口，但需要继续检查：

NetworkSelector → Runtime → TelegramClient 是否完整贯通。

---

# 审查记录

## 第一次审查

范围：

- app/download

重点：

验证 TG 下载加速架构。

结论：

Chunk 架构已经建立，但多账号并行下载尚未进入实际主流程。

发现 ConcurrentChunkStream 接口调用错误等问题。

---

## 第二次审查

范围：

- app/telegram/client.py
- app/telegram/client_pool.py
- app/telegram/client_provider.py
- app/telegram/lifecycle.py

结论：

Telegram 多账号和网络插件方向已经开始落地，但下载加速仍未形成完整闭环。

当前最大风险：旧 client 创建逻辑与新 runtime/provider 架构并存。
