# 环境变量模板

> 复制本文件, 重命名为 `README.md` 放到 `.hl/knowledge/env-vars/`

## 格式说明

| 列 | 说明 |
|---|---|
| 变量名 | 环境变量名 |
| 含义 | 作用 |
| 默认值 | 开发/生产环境默认值(如有) |
| 环境差异 | dev / staging / prod 区别 |
| 引入版本 | 何时引入 |
| 关联 | 关联接口/配置 |

## 环境变量总表

### 数据库

| 变量 | 含义 | 默认值 | dev | staging | prod | 引入版本 | 关联 |
|---|---|---|---|---|---|---|---|
| `DB_HOST` | 数据库地址 | `localhost` | `localhost` | `db-staging.internal` | `db-prod.internal` | v1 | `.hl/knowledge/db/` |
| `DB_PORT` | 数据库端口 | `3306` | `3306` | `3306` | `3306` | v1 | - |
| `DB_NAME` | 数据库名 | `ehr` | `ehr_dev` | `ehr_staging` | `ehr` | v1 | - |
| `DB_USER` | 数据库用户 | `root` | `dev_user` | `staging_user` | `prod_user` | v1 | - |
| `DB_PASSWORD` | 数据库密码 | (空) | (本地) | (secret manager) | (secret manager) | v1 | **强敏感, 严禁进 git** |

### Redis (缓存)

| 变量 | 含义 | 默认值 | 引入版本 |
|---|---|---|---|
| `REDIS_HOST` | Redis 地址 | `localhost` | v1 |
| `REDIS_PORT` | Redis 端口 | `6379` | v1 |
| `REDIS_PASSWORD` | Redis 密码 | (空) | v1 |

### 认证与安全

| 变量 | 含义 | 默认值 | 引入版本 |
|---|---|---|---|
| `JWT_SECRET` | JWT 签名密钥 | (随机生成) | v1 |
| `SESSION_TIMEOUT_MINUTES` | 会话超时 | `60` | v1 |
| `CORS_ALLOWED_ORIGINS` | 跨域白名单 | `http://localhost:8080` (dev) | v1 |

### 应用

| 变量 | 含义 | 默认值 | 引入版本 |
|---|---|---|---|
| `SERVER_PORT` | HTTP 服务端口 | `8080` | v1 |
| `LOG_LEVEL` | 日志级别 | `INFO` | v1 |
| `UPLOAD_MAX_SIZE` | 上传文件最大字节 | `10485760` (10MB) | v2 |
| `IMPORT_MAX_ROWS` | Excel 导入最大行数 | `1000` | v2 |

### v3 新增

| 变量 | 含义 | 默认值 | 引入版本 |
|---|---|---|---|
| `AUDIT_LOG_RETENTION_DAYS` | audit_log 保留天数 | `365` | v3 |
| `RESTORE_REASON_MAX_LENGTH` | 恢复原因最大字符 | `500` | v3 |
| `BLACKLIST_DRY_RUN_MODE` | 黑名单操作 dry-run 模式 | `false` | v3 |

## 环境差异速查

| 维度 | dev | staging | prod |
|---|---|---|---|
| DB | localhost / ehr_dev | db-staging.internal / ehr_staging | db-prod.internal / ehr |
| 日志级别 | DEBUG | INFO | WARN |
| 上传文件大小 | 10MB | 10MB | 5MB(更严格) |
| CORS 白名单 | `*` (放宽) | `https://*.company.com` | `https://ehr.company.com` |
| Mock 数据 | 启用(方便开发) | 部分 | 禁用(用真数据) |

## 敏感变量管理

### 强敏感(严禁进 git)

- `*_PASSWORD` / `*_SECRET` / `*_KEY` 等
- **必须**通过 secret manager 注入(开发用 `.env.local`, 生产用 Vault / 阿里云 KMS)

### 弱敏感(可进 git 但需 base64 加密)

- 公开 API key(有 rate limit)
- 第三方 SDK 标识(client_id / app_id)

### 不敏感

- `SERVER_PORT` / `LOG_LEVEL` 等

### 注入机制

| 环境 | 机制 |
|---|---|
| dev | `.env.local`(git ignore) |
| staging / prod | K8s Secret / Vault / 云 secret manager |

## 配置变更流程

### 新增环境变量

1. 在本知识库表格加一行(完整字段)
2. 在 `application-{profile}.yml` 加默认值
3. K8s Secret / Vault 加实际值(staging/prod)
4. `.env.example` 加占位符(dev)
5. **同 PR 提交** 知识库 + 代码

### 修改/废弃环境变量

1. 在本知识库表格加 `**v{N} 废弃**` 标记
2. 代码层兼容(读取旧变量名 fallback)
3. 新版本完全移除时, 用 `git log --all -- {变量名}` 确认无残留引用

## 关联

- 数据库: `.hl/knowledge/db/`
- API 接口: `.hl/knowledge/api/`
- 依赖: `.hl/knowledge/dependencies/`
- 项目元信息: 项目根 `CLAUDE.md`