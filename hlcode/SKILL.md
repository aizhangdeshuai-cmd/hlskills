---
name: hlcode
description: 编码标准规范，覆盖命名规范（camelCase/PascalCase/UPPER_SNAKE）、不可变性与类型安全（禁止any/展开运算符）、文件组织（功能模块/单文件<=300行）、代码味道清单（魔法数字/复杂三元/重复代码/未处理错误）。Use when 用户需要遵循编码标准（命名/不可变性/文件组织/代码味道）时调用。
---

# 编码标准

---

## 命名与可读性

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `getUserById`、`handleSubmit` |
| 组件/类 | PascalCase | `UserProfile`、`OrderService` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`、`API_BASE_URL` |

- 命名表达意图，**避免缩写**：`getUserById` 而非 `getUsr`
- 函数**单一职责**，长度不超过 **50 行**
- 嵌套深度不超过 **4 层**

---

## 不可变性与类型安全

### 不可变模式
- 优先使用展开运算符等不可变模式
- **避免直接修改**原数据

```typescript
// 好
const updated = { ...user, name: 'new' };

// 差
user.name = 'new';
```

### 类型安全（TypeScript）
- **禁止使用 `any`**，使用 `unknown` + 类型守卫替代
- 使用接口配合**可辨识联合**（discriminated union）处理多态数据

```typescript
// 好
type Shape = 
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number };
```

---

## 文件组织

按功能模块组织：

```
src/
├── components/   # UI组件
├── hooks/        # 自定义Hooks
├── lib/          # 工具函数
├── types/        # 类型定义
└── api/          # API调用
```

- **单文件不超过 300 行**，超出则拆分

---

## 代码味道清单（Code Review 必查）

| 问题 | 处理 |
|------|------|
| 魔法数字 | 用命名常量替代 |
| 过度复杂的三元表达式 | 改用 if/switch |
| 重复代码块 | 提取公共函数 |
| 未处理的错误路径 | 添加错误处理 |
| 过长函数（>50行） | 拆分为多个小函数 |
| 深层嵌套（>4层） | 提前return / 提取子函数 |

---

## 关联命令
- `/hlreview` — 代码审查规范
- `/hlerror` — 错误处理规范

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
