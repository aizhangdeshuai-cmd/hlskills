---
name: hlerror
description: 错误处理规范，覆盖类型化错误（AppError基类/具体错误类型）、API错误处理中间件（不泄露堆栈）、指数退避重试与断路器模式、React错误边界。Use when 用户需要设计错误处理（类型化/重试/断路器/错误边界）时调用。
---

# 错误处理规范

---

## 类型化错误

定义 `AppError` 基类，包含：`code`、`statusCode`、`message`、`details`

按错误类型继承：

```
AppError
├── ValidationError   — 参数验证失败 (400/422)
├── NotFoundError     — 资源不存在 (404)
├── AuthError         — 认证/鉴权失败 (401/403)
├── ConflictError     — 资源冲突 (409)
├── RateLimitError    — 频率限制 (429)
└── ExternalServiceError — 外部服务调用失败 (502/504)
```

---

## API 错误处理

- 全局错误处理中间件格式化所有错误响应，**不泄露堆栈跟踪**
- 用户可见的错误消息使用友好表达
- 技术细节记录到日志（供排查）

```
用户看到：     "邮箱地址格式不正确"
日志记录：     ValidationError: email field failed regex validation
              at UserService.updateEmail (src/services/user.ts:42)
```

---

## 重试与韧性

### 指数退避重试
- 初始间隔 1s，最大间隔 30s，最多重试 3 次
- 仅对瞬时失败（网络超时、503、429 with Retry-After）重试
- **不可重试**的错误（401、403、422）**直接返回**

### 断路器模式
关键依赖使用断路器，防止级联故障：
- **关闭态** → 正常调用
- **开启态** → 直接返回降级响应（5次失败后开启）
- **半开态** → 探测性调用（30s后），成功则关闭，失败则重新开启

---

## React 错误边界

- 每个页面/功能模块包裹错误边界组件
- 错误边界显示用户友好回退 UI，**不暴露原始错误**
- 提供"重试"按钮让用户恢复

```tsx
<ErrorBoundary fallback={<ErrorFallback />}>
  <UserDashboard />
</ErrorBoundary>
```

---

## 关联命令
- `/hlapi` — API设计规范
- `/hlcode` — 编码标准

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
