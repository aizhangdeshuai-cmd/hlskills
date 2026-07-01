# 枚举字典模板

> 复制本文件, 重命名为 `{enum}.md` 放到 `.hl/knowledge/enums/`

## 枚举信息

| 项 | 值 |
|---|---|
| 枚举名 | `BlacklistStatus` |
| 字段 | `status` |
| 引入版本 | v1 初始 / v3 扩展 |
| 数据库类型 | `ENUM` (MySQL) |

## 枚举值

| 值 | 中文 | 含义 | 引入版本 |
|---|---|---|---|
| `ACTIVE` | 活跃 | 正常状态, 默认列表显示 | v1 |
| `REMOVED` | 已移除 | 软删除, 需"显示已移除"开关才可见 | v1 |
| `SUPERSEDED` | 已取代 | v3 新增终态, 恢复时同证件号 ACTIVE 合并级联 | **v3** |
| `HISTORICAL` | 归档 | v3 新增终态, 预留归档策略(本期不实现) | **v3** |

## 写入方

| 枚举值 | 写入方 | 触发场景 |
|---|---|---|
| `ACTIVE` | `BlacklistController` / `BlacklistSyncService` | 新增 / 导入 / 上游推送 / 恢复 |
| `REMOVED` | `BlacklistController.remove` | 操作列"移除" |
| `SUPERSEDED` | `BlacklistController.restore` (事务) | 恢复时同证件号 ACTIVE 存在, 级联 |
| `HISTORICAL` | (本期不实现) | (预留) |

## 列表可见规则

- **ACTIVE**: 默认列表显示(BL-2 默认 ACTIVE only)
- **REMOVED**: 需打开"显示已移除"开关(BL-2) 才显示
- **SUPERSEDED**: 永不显示(数据库保留, 审计可查)
- **HISTORICAL**: 永不显示(本期不触发)

## 前端显示文本

| 值 | 显示文本 |
|---|---|
| `ACTIVE` | (无标签, 默认) |
| `REMOVED` | "已移除" |
| `SUPERSEDED` | (不显示) |
| `HISTORICAL` | (不显示) |

## 关联

- 状态机: `.hl/knowledge/state-machines/blacklist.md`
- 业务规则: `docs/v3/prd.md §1 BL-1 / §1.12 BL-12`
- 数据库: `.hl/knowledge/db/blacklist.md §状态枚举扩展历史`