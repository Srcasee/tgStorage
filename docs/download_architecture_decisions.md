# Download 模块架构决策记录

## 命名决策

重构后的下载模块继续使用 `download` 命名，不引入 `download_v2`。

原因：

- 不维护新旧两个下载体系；
- 重构完成后直接替换旧实现；
- `app/download` 保持唯一下载入口。

## 网络边界

已确定：所有 Telegram 账号使用同一网络策略。

不设计：

- 账号级 proxy；
- 账号绑定独立网络出口。

目标结构：

```
System Network Plugin
        |
        v
Telegram Runtime
        |
        v
All Telegram Accounts
```

## Download 模块职责

负责：

- Download Task；
- Chunk Planning；
- 并发调度；
- 重试；
- Chunk 合并；
- 多账号下载调度。

不负责：

- Telegram Client 生命周期；
- Proxy 实现；
- 网络连接管理。

## Telegram Runtime 边界

负责：

- Client 生命周期；
- Session；
- Account Runtime；
- 系统网络插件注入。

## 重构方向

旧下载实现直接替换，不长期维护并行版本。
