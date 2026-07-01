# 错误码字典模板

> 复制本文件, 重命名为 `README.md` 放到 `.hl/knowledge/error-codes/`

## 格式说明

| 列 | 说明 |
|---|---|
| 错误码 | 项目内统一编码 |
| HTTP 状态 | HTTP 协议层状态码 |
| 业务含义 | 错误的中文/英文描述 |
| 触发场景 | 何时返回 |
| 关联接口 | 哪些接口会返回 |
| 引入版本 | 何时新增 |

## 错误码总表

| 错误码 | HTTP | 含义 | 触发场景 | 关联接口 | 引入版本 |
|---|---|---|---|---|---|
| `0` | 200 | 成功 | - | 全部 | v1 |
| `40001` | 400 | 参数错误 | 入参缺失/格式错误/超长 | 全部 POST | v1 |
| `40002` | 400 | 业务规则违反 | 证件号格式错 / 日期未来 / 原因必填 | POST /blacklist 等 | v2 |
| `40003` | 400 | 重复新增 | 同证件号 ACTIVE 已存在 | POST /blacklist | v2 |
| `40004` | 400 | 文件超限 | Excel > 1000 行 | POST /blacklist/import | v2 |
| `40301` | 403 | 无权限 | `@PreAuthorize` 拦截 | 全部 | v1 |
| `40401` | 404 | 资源不存在 | ID 不存在(可能已物理删除) | POST /blacklist/{id}/remove, **POST /blacklist/restore/{id}** | v2 |
| `40402` | 404 | 文件不存在 | 模板下载失败 | GET /blacklist/template.xlsx | v2 |
| `40901` | 409 | 状态冲突 | 恢复时状态已非 REMOVED / 并发冲突 | **POST /blacklist/restore/{id} (v3 新增)** | **v3** |
| `40902` | 409 | 唯一索引冲突 | 数据库唯一索引冲突(并发新增) | POST /blacklist | v2 |
| `50001` | 500 | 系统错误 | 事务失败 / DB 异常 | 全部 | v1 |
| `50002` | 500 | 解析失败 | Excel 解析失败 | POST /blacklist/import | v2 |
| `50301` | 503 | 服务不可用 | 数据库连接失败 | 全部 | v1 |

## 错误码使用规范

### 前端处理

- 错误码 `0` → 成功
- `4xx` → 业务错误, `el-message.error(错误码对应文案)`, **不重定向**
- `5xx` → 系统错误, `el-message.error("系统繁忙, 请稍后重试")`, **可重定向**到 `/report/list`
- `403` → 跳登录页

### 后端规范

- 业务异常用 `BizException(code, message)` 抛出
- 全局 `@ControllerAdvice` 统一处理, 包装为 `{code, message, data: null}` 响应
- 不要直接返回 `ResponseEntity.status(400)` 等

### 跨语言约定

- 前端 TS: `enum ErrorCode { SUCCESS = 0, PARAM_INVALID = 40001, ... }`
- 后端 Java: `public class ErrorCode { public static final int SUCCESS = 0; public static final int PARAM_INVALID = 40001; ... }`
- 新增错误码必须 3 处同步(后端常量 + 前端枚举 + 本知识库)

## 关联

- API 接口: `.hl/knowledge/api/blacklist.md`
- 数据库: `.hl/knowledge/db/blacklist.md`
- 业务规则: `docs/v3/prd.md §{N} BL-{N}` (具体业务规则)