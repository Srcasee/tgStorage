我对这个系统的要求是
1、TG存储源→API→系统识别→web前端→用户搜索、下载是核心功能(视频播放图片预览等属于可扩展)
2、管理员→web后台→控制资源按账号显示、分类，支持多账号
3 、proxy始终是可选的插件要成为热插拔项，而且支持多种网络类型
4、尽可能绕过TG下载速度的限制
5、系统不要臃肿，最终的实际部署操作要简单

根据你提出的目标，tgStorage 的定位需要从目前的：

Telegram 文件读取网关 + 视频流服务

升级为：
Telegram 作为对象存储后端的多账号资源管理系统（Storage Gateway）
核心不再是视频播放，而是：
Telegram Storage Layer
        ↓
Indexer / Metadata Layer
        ↓
Storage API Layer
        ↓
Web Admin + User Frontend
        ↓
Search / Download / Preview

下面按优先级制定升级路线。

一、目标架构调整
当前架构
目前：
Telegram
   |
Telethon
   |
Scanner
   |
SQLite
   |
FastAPI
   |
简单Web

问题：
TG资源和用户没有分层
管理能力不足
Proxy耦合
下载优化不足
没有权限模型
升级后架构
建议：
                    ┌──────────────┐
                    │ Web Admin    │
                    └──────┬───────┘
                           │
                    Resource Manager
                           │
                           ▼
Telegram Accounts
        |
        |
┌───────┴────────┐
│ TG Connector   │
│ Plugin System  │
└───────┬────────┘
        |
        ▼
 Telegram Storage Layer
        |
        ▼
 Metadata Engine
        |
        |
 ┌──────┴────────┐
 │ Search Index  │
 │ PostgreSQL    │
 └───────────────┘
        |
        ▼
 API Gateway
        |
        ▼
 Web Frontend

二、开发阶段规划
分：
Phase 0 修复基础问题
Phase 1 核心资源系统
Phase 2 管理后台
Phase 3 网络插件系统
Phase 4 下载性能优化
Phase 5 云盘化
Phase 0：基础修复（必须）

目标：
让现有系统成为可靠基础。

周期：
约 1~2 周

0.1 数据模型重构（最高优先）
当前：
accounts
files
telegram_sources
关系不完整。

改：
accounts

TG账号

accounts

id
name
phone
session_path
enabled
status
last_login
telegram_sources

TG资源来源：
telegram_sources

id
account_id

chat_id
chat_type

name

sync_mode

enabled

关系：
Account
 |
 +-- Channel A
 |
 +-- Channel B
files

资源文件：
files
id
source_id
telegram_message_id
filename
mime
size
hash
category_id
created_time
status
categories

新增：
categories
id
name
parent_id
icon

支持：
影视
 ├── 动画
 ├── 电影

资料
 ├── PDF
 └── 软件

Phase 1：资源管理核心

对应你的第1、2点。

目标：
TG存储源 → API → 系统识别 → Web

1.1 增加资源识别引擎
新增：
Resource Analyzer
扫描文件：
自动判断：
文件类型
.mp4
.mkv
.jpg
.png
.pdf
.zip
.apk
.exe
分类规则
例如：
文件：
[BDMV]鬼灭之刃S01E01.mkv
自动：
视频
 |
 动画
规则系统

数据库：
category_rules
pattern
category_id
priority
例如：
*.mkv
→ 视频
*.pdf
→ 文档

1.2 搜索系统升级
当前：
LIKE
升级：
PostgreSQL + FTS

支持：
关键词、文件名、标签、分类、来源
搜索：
鬼灭
返回：
动画
电影
BD
1080P

1.3 API重新设计
当前：
/files
改：
REST：
/api/resources

GET
资源列表

GET
资源搜索

GET
资源详情

GET
download

Phase 2：管理员后台
对应你的第2点。
目标：
管理员：
Web Admin
管理：

2.1 TG账号管理
页面：
Telegram Accounts
账号A
状态:
在线
资源:
12000
流量:
500GB

操作：启用、禁用、删除
测试连接

2.2 来源管理
页面：
Channels
账号A
 ├── Movie Channel
 ├── Anime Channel

账号B
 └── Backup Channel

操作：
添加频道
设置同步模式
设置分类

2.3 文件管理
显示：
资源
文件名
来源账号
来源频道
分类
大小
时间

支持：
修改分类
批量移动
删除索引

Phase 3：Proxy插件系统
对应你的第3点。
现在：
proxy写死配置。
需要改成：
Proxy Provider架构
Network Layer
       Proxy Manager
              |
      +-------+-------+
 SOCKS5
 HTTP
 MTProto Proxy
 Direct
 WireGuard
 VPN

3.1 Proxy接口
定义：
class ProxyProvider:
    connect()
    test()
    get_proxy()
    health_check()

3.2 插件目录
plugins/
proxy/
    socks5.py
    http.py
    mtproto.py
    wireguard.py

3.3 热插拔
数据库：
network_plugins
id
type
config
enabled
priority
运行：
修改后台配置
↓
reload
↓
无需重启TG服务

Phase 4：绕过TG下载限制（重点）
对应你的第4点。
先说明：
Telegram下载速度限制无法真正“绕过”。
但是可以：
最大化利用多账号、多连接、缓存。

4.1 多账号下载池
现在：
file
 |
account
升级：
Downloader Pool
Account A
  |
 10MB/s

Account B
  |
 10MB/s

Account C
  |
 10MB/s
       ↓
 Merge Stream

4.2 Chunk并发下载
当前：
单文件：
chunk1
chunk2
chunk3
升级：
          file
chunk1 ─ account A
chunk2 ─ account B
chunk3 ─ account C
merge

4.3 热点缓存
增加：
Hot Cache
访问次数
最近访问
播放位置
例如：
热门视频：
自动缓存：
0-500MB

4.4 下载调度器
新增：
Download Scheduler
负责：
选择：
哪个TG账号下载最快
指标：
speed
error rate
flood wait
latency

Phase 5：用户系统
后续。
增加：
Users
Roles
Permissions
权限：
管理员
普通用户
游客

三、推荐技术升级
数据库
当前：
SQLite
升级：
PostgreSQL
原因：
需要：用户、权限、分类、搜索、统计、缓存

增加：
Redis
用途：文件热点、Session、下载任务、后端
保留：
FastAPI
很好。

前端
建议：
替换：
index.html
为：
Vue3 + TypeScript

结构：
frontend
admin
user

四、最终版本目标
完成后：
                Admin
                 |
                 |
Telegram Accounts
        |
        |
 Proxy Plugin Layer
        |
        |
 TG Storage Engine
        |
        |
 Metadata/Search Engine
        |
        |
 API Gateway
        |
        |
 --------------------
 |                  |
User Web        Mobile/API

搜索
下载
预览
播放

五、开发优先级排序
按你的需求：
优先级	任务	重要性
P0	数据库重构	★★★★★
P0	资源索引系统	★★★★★
P0	管理员后台	★★★★★
P1	搜索系统	★★★★★
P1	Proxy插件化	★★★★
P1	多账号下载调度	★★★★★
P2	缓存优化	★★★★
P2	视频图片预览	★★★
P3	用户权限系统	★★★

六、我建议的最终版本路线
不要继续在现有代码上堆功能。
建议：
tgStorage v1
        |
        |
tgStorage v2

重新定义：
Core
Plugin
API
Admin
Frontend

其中：
保留：
✅ Telethon Connector
✅ Scanner思想
✅ VideoStream思想
✅ Chunk Cache思想

Phase 0-A：目录重构方案

当前：
app/
├── files/
├── telegram/
├── cache/
├── web/
├── database.py
├── config.py
└── main.py
保留兼容，但逐步迁移为：
app/
├── core/
│   ├── config.py
│   ├── database.py
│   ├── logging.py
│   ├── security.py
│   └── events.py
├── models/
│   ├── account.py
│   ├── resource.py
│   ├── category.py
│   └── network.py
├── storage/
│   ├── base.py
│   ├── telegram/
│   │   ├── client.py
│   │   ├── session.py
│   │   ├── scanner.py
│   │   └── downloader.py
│   ├── scheduler.py
│   └── cache.py
├── metadata/
│   ├── analyzer.py
│   ├── classifier.py
│   └── rules.py
├── api/
│   ├── resources.py
│   ├── download.py
│   ├── admin.py
│   └── auth.py
├── plugins/
│   │
│   └── network/
│       ├── base.py
│       ├── direct.py
│       ├── socks5.py
│       ├── http.py
│       └── mtproto.py
├── admin/
│   └── frontend/
├── user/
│   └── frontend/
└── main.py

Phase 0-B：核心模块职责重新定义
1. Storage Layer
负责：
“如何从存储取文件”
未来不仅 Telegram。
接口：
class StorageBackend:
    async def get_file_info()
    async def stream()
    async def download()
    async def health()
目前实现：
TelegramStorageBackend
未来可以：
S3Backend
LocalBackend
WebDAVBackend

2. Telegram Layer
只负责：
Telegram通信。
不负责：
分类
API
用户

结构：
storage/telegram/
client.py
    登录
    session
    connection

scanner.py
    消息扫描

downloader.py
    chunk读取

3. Metadata Layer
新增。
职责：
把：
Telegram文件
变成：
系统资源。
例如：
输入：
Avatar.2024.1080p.mkv
输出：
{
"type":"video",
"category":"movie",
"tags":[
 "1080p"
]
}

Phase 0-C：数据库模型设计
从当前：
files.db
升级：
推荐：
PostgreSQL
但是 Phase 0 保持：
SQLAlchemy ORM
方便迁移。

表1：telegram_accounts
telegram_accounts
id
name
phone
session_path
enabled
status
last_login
created_at

表2：telegram_sources
解决当前：
account_id缺失问题
telegram_sources
id
account_id
chat_id
chat_type
title
sync_mode
enabled
last_message_id
last_sync_time

关系：
Account
   |
Sources

表3：resources
替换 files：
resources
id
source_id
telegram_message_id
filename
extension
mime_type
size
hash
category_id
status
created_at

表4：categories
categories
id
name
parent_id
sort_order
支持：
视频
 ├电影
 ├动漫
资料
 ├教程
 └文档

表5：network_plugins
为 Proxy 热插拔准备：
network_plugins
id
name
type
config_json
enabled
priority
status

Phase 0-D：迁移策略
不会直接删除旧代码。
采用：
双结构过渡：
旧:
files
新:
resources
迁移工具：
新增：
tools/
migrate_v1_to_v2.py
流程：
files.db
   |
读取旧files
   |
转换
   |
resources表

Phase 0-E：第一批 Commit 计划
建议拆：
Commit 1
chore:
create v2 architecture skeleton
内容：
新增：
core/
models/
storage/
metadata/
plugins/
不影响运行。

Commit 2
feat:
introduce v2 database models
新增：
ORM模型。

Commit 3
feat:
add v1 database migration tool
迁移旧：
files.db

Commit 4
refactor:
move telegram connector into storage layer
迁移：
app/telegram
↓
app/storage/telegram
Phase 0 完成标准
完成后：
仓库状态：
main
 |
 |
 +-- v2-architecture-phase0
        |
        |
        + core
        + models
        + storage
        + metadata
        + plugins

并且：
现有功能：
✅ Telegram扫描
✅ 文件下载
✅ 视频播放
保持可运行。

