---
name: hlapi
description: API设计规范，覆盖URL命名（复数名词/kebab-case/无动词）、HTTP方法与状态码、分页（cursor-based/offset-based）、错误响应格式、API版本控制（URL路径）、速率限制与鉴权。Use when 用户需要设计或审查 API 接口（URL/状态码/分页/错误格式）时调用。
---

# API 设计规范

---

## URL 与命名

- 资源名使用**复数名词** + **kebab-case**
- URL 中**不含动词**，用 HTTP 方法表达动作

```
GET    /api/users          # 获取用户列表
POST   /api/users          # 创建用户
GET    /api/users/:id      # 获取单个用户
PUT    /api/users/:id      # 更新用户
DELETE /api/users/:id      # 删除用户
GET    /api/users/:id/orders  # 获取用户的订单
```

---

## HTTP 方法与状态码

| 方法 | 成功状态码 | 含义 |
|------|---------|------|
| `GET` | 200 | 获取成功 |
| `POST` | 201 | 创建成功 |
| `PUT` / `PATCH` | 200 | 更新成功 |
| `DELETE` | 204 | 删除成功（无响应体） |

### 错误状态码
| 状态码 | 含义 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 验证失败 |
| 429 | 请求频率限制 |
| 500 | 服务端错误 |

---

## 分页与查询

### 分页策略
- **集合接口**：默认使用基于游标的分页（cursor-based）
- **管理后台**：可使用基于偏移的分页（offset-based）

### 查询参数规范
```
?filter[status]=active
&sort=-created_at
&page[after]=<cursor>
&page[size]=20
```

---

## 错误响应格式

所有错误统一返回以下结构：

```json
{
  "error": {
    "code": "INVALID_PARAM",
    "message": "参数 'email' 格式不正确",
    "details": [
      { "field": "email", "reason": "must be a valid email address" }
    ]
  }
}
```
**不泄露堆栈跟踪。**

---

## 版本控制与安全

- API 版本通过 URL 路径控制：`/api/v1/...`、`/api/v2/...`
- 敏感接口须有速率限制（rate limiting）
- 鉴权使用 Bearer Token：`Authorization: Bearer <token>`
- 密钥不硬编码，通过环境变量注入

---

## 关联命令
- `/hlerror` — 错误处理规范
- `/hldb` — 数据库设计规范

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
