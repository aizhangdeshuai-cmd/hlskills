---
name: hldb
description: 数据库迁移规范，覆盖安全清单（UP/DOWN/默认值/分离DDL DML）、零停机策略（扩展-收缩模式/CREATE INDEX CONCURRENTLY/分批更新）、禁止事项（严禁编辑已部署迁移）。Use when 用户需要数据库迁移或审查迁移安全性时调用。
---

# 数据库迁移规范

> 属于 `project-dev-workflow` 技能系统的一部分。完整规范见 `database-migrations` 技能。

---

## 安全清单（每次迁移必查）

- [ ] 每个迁移必须有 **UP**（执行）和 **DOWN**（回滚）
- [ ] 新增 NOT NULL 列必须提供**默认值**
- [ ] 同一迁移中**禁止混用 DDL**（结构变更）和 **DML**（数据变更）
- [ ] 迁移脚本须针对**生产级数据量**进行测试

---

## 零停机策略

### 列操作
列重命名/删除使用**扩展-收缩模式**（expand-contract）：

```
1. 新增列（expand）
2. 应用代码同时写新旧两列
3. 数据迁移：将旧列数据复制到新列
4. 切换读取到新列（contract）
5. 确认无问题后删除旧列
```

### 索引
- 大表创建索引使用 `CREATE INDEX CONCURRENTLY`（PostgreSQL）
- 创建索引前评估查询模式，避免冗余索引

### 批量更新
- 大批量数据更新**分批处理**，每批不超过 **10,000 行**
- 每批之间留有间隔，避免长事务锁表

---

## 禁止事项

| 禁止 | 原因 |
|------|------|
| **编辑**已部署的迁移文件 | 破坏迁移历史一致性 |
| **删除**迁移文件"清理"历史 | 其他环境无法正确迁移 |
| **DROP TABLE / DROP DATABASE** | 不可逆数据丢失，须有审批+备份+回滚方案 |
| 在生产环境手动执行 SQL | 绕过迁移版本控制 |

---

## 迁移文件命名

```
YYYYMMDDHHMMSS_descriptive_name.sql
20240520143000_add_user_avatar_column.sql
```

---

## 关联命令
- `/hlapi` — API设计规范
- `/hldeploy` — 部署规范（含回滚）

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm-product/path-conventions.md` 中央规范。
