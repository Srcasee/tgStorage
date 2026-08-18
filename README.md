# Telegram Drive v1.0

## 项目简介

Telegram Drive 是一个基于 Telegram 作为对象存储后端的个人云盘系统。

通过 Telethon 连接 Telegram，多账号扫描 Telegram 文件消息，建立 SQLite
文件索引，并通过 FastAPI 提供下载与视频在线播放能力。

------------------------------------------------------------------------

## 当前版本

版本：

`v1.0`

最终稳定提交：

`629e7fa sync database schema with current production structure`

Release：

`v1.0`

------------------------------------------------------------------------

## 核心功能

### Telegram 多账号

支持：

-   多 Telegram Session
-   多账号同时在线
-   文件绑定账号
-   自动选择账号下载

当前账号：

-   larsniel
-   DGWosh
-   Asada

### 文件扫描

支持：

-   Channel / Group 扫描
-   增量同步
-   定时扫描
-   文件索引

### 文件下载

接口：

`GET /files/{id}/download`

支持：

-   大文件下载
-   HTTP Range
-   分段读取

### 视频流

接口：

`GET /files/{id}/stream`

支持：

-   Range 请求
-   浏览器在线播放
-   视频 seek

------------------------------------------------------------------------

## 数据库

数据库：

`/data/files.db`

主要表：

-   files
-   accounts
-   telegram_sources
-   categories
-   shares

唯一索引：

`(account_id, telegram_chat_id, message_id)`

用于避免重复索引。

------------------------------------------------------------------------

## v1.0 验收记录

### 下载测试

26MB+ 文件下载成功。

### Range 测试

结果：

`206 Partial Content`

支持：

-   bytes=0-1023
-   随机偏移读取

### 视频流测试

结果：

`206 Partial Content`

浏览器播放和分段读取正常。

------------------------------------------------------------------------

# v1.0 已知问题

## 1. Telethon 偶发连接关闭日志

日志：

    Server closed the connection:
    0 bytes read on a total of 8 expected bytes

原因：

Telegram MTProto 长连接网络行为。

影响：

无。

验证：

-   Scanner 正常运行
-   Client 未退出
-   下载正常
-   视频正常

后续版本可优化日志处理。

------------------------------------------------------------------------

## 2. Stream 接口暂不支持 HEAD

现象：

    HEAD /files/{id}/stream

返回：

    405 Method Not Allowed

影响：

低。

不影响：

-   浏览器播放
-   Range 请求

计划：

v1.1 增加 HEAD。

------------------------------------------------------------------------

## 3. HTTP Header 可继续优化

当前：

-   下载正常
-   Range 正常

后续：

-   完善 HEAD 信息
-   增加缓存策略
-   增加 ETag

------------------------------------------------------------------------

## 4. 数据库初始化历史差异

早期开发环境数据库结构与生产结构存在差异。

v1.0 已完成：

-   database.py 对齐生产结构
-   保持现有 files.db 兼容

------------------------------------------------------------------------

##5. Video streaming

Current status:
- File download works normally.
- HTTP Range requests are supported.
- Browser video playback is unstable.

Symptoms:
- Video player may keep loading.
- Seek bar cannot be moved.
- Playback may fail after buffering.

Possible causes:
- Telegram remote random access performance.
- Stream layer lacks optimized caching.
- Browser Range request handling needs improvement.

Planned fix:
v1.1 StreamService redesign.

------------------------------------------------------------------------

## Docker

挂载：

源码：

`/app`

数据：

`/data`

重要数据：

    /data/files.db
    /data/accounts

------------------------------------------------------------------------

## 安全注意

禁止提交 Git：

    /data/accounts
    /data/*.db

原因：

包含 Telegram 登录状态和索引数据。

------------------------------------------------------------------------

## Git Release

提交：

    8c88d59 cleanup v1.0 source cache and temporary files

    3401528 ignore runtime telegram sessions and databases

    aedfdc8 refactor download layer with TelegramDownloader

    629e7fa sync database schema with current production structure

------------------------------------------------------------------------

## 后续方向 v1.1

计划：

-   权限系统
-   分享链接
-   文件管理
-   收藏
-   标签
-   下载优化
-   视频信息解析
-   缩略图
-   PostgreSQL 支持

------------------------------------------------------------------------

## 当前状态

Telegram Drive v1.0 Stable Release

核心能力：

-   Telegram Storage
-   Multi Account
-   File Index
-   File Download
-   HTTP Range
-   Video Streaming
-   Docker Deployment
-   Production Database

v1.0 已完成封版。
