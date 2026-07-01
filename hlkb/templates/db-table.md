# 数据库表模板

> 复制本文件, 重命名为 `{table}.md` 放到 `.hl/knowledge/db/`

## 表基本信息

| 项 | 值 |
|---|---|
| 表名 | `blacklist` |
| 中文名 | 黑名单主表 |
| 引入版本 | v1 初始 / v2 完善 / v3 扩展 |
| 引擎 | InnoDB (MySQL 8.0+) |
| 字符集 | utf8mb4 |
| 排序规则 | utf8mb4_unicode_ci |
| 存储位置 | ehr-report 数据库 |

## 字段列表

| 字段 | 类型 | 必填 | 默认 | 注释 | 引入版本 |
|---|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | Y | AUTO_INCREMENT | 主键 | v1 |
| `company_id` | BIGINT UNSIGNED | Y | - | 公司 ID, 多公司隔离 | v1 |
| `emp_no` | VARCHAR(32) | Y | - | 工号 | v1 |
| `emp_name` | VARCHAR(64) | Y | - | 姓名 | v1 |
| `gender` | TINYINT | Y | - | 性别(0=未知, 1=男, 2=女) | v1 |
| `resigned_company` | VARCHAR(64) | Y | - | 离职公司 | v1 |
| `id_type` | ENUM('身份证', '护照', '其他') | Y | - | 证件类型 | v1 |
| `id_number` | VARCHAR(64) | Y | - | 证件号 | v1 |
| `resigned_date` | DATE | Y | - | 离职日期(<= today) | v1 |
| `remark` | VARCHAR(500) | N | NULL | 备注(0-500 字符) | v1 |
| `source` | ENUM('UPSTREAM', 'MANUAL', 'IMPORT') | Y | 'MANUAL' | 数据来源 | v2 |
| `status` | ENUM('ACTIVE', 'REMOVED', 'SUPERSEDED', 'HISTORICAL') | Y | 'ACTIVE' | 状态(v3 新增 2 枚举) | v1 / v3 扩展 |
| `created_by` | BIGINT UNSIGNED | Y | - | 创建人(关联 user.id) | v1 |
| `created_at` | DATETIME | Y | CURRENT_TIMESTAMP | 创建时间 | v1 |
| `removed_by` | BIGINT UNSIGNED | N | NULL | 移除人 | v2 |
| `removed_at` | DATETIME | N | NULL | 移除时间 | v2 |
| `removed_reason` | VARCHAR(500) | N | NULL | 移除原因(必填落库) | v2 |
| `restored_by` | BIGINT UNSIGNED | N | NULL | 恢复人 | **v3 新增** |
| `restored_at` | DATETIME | N | NULL | 恢复时间 | **v3 新增** |
| `restored_reason` | VARCHAR(500) | N | NULL | 恢复原因(必填落库) | **v3 新增** |
| `superseded_by` | BIGINT UNSIGNED | N | NULL | 被本记录取代的 ID | **v3 新增** |
| `superseded_at` | DATETIME | N | NULL | 被取代时间 | **v3 新增** |
| `version` | INT UNSIGNED | N | 0 | 乐观锁(预留, 本期不用) | (预留) |

## 索引

| 索引名 | 类型 | 字段 | 唯一性 | 引入版本 | 备注 |
|---|---|---|---|---|---|
| `PRIMARY` | 主键 | `id` | 是 | v1 | - |
| `idx_company_status` | 普通 | `company_id, status` | 否 | v1 | 列表查询常用 |
| `idx_resigned_date` | 普通 | `resigned_date` | 否 | v1 | 日期过滤 |
| `uniq_active_blacklist` | **硬唯一** | `company_id, id_type, id_number, status` | 是 | v2 | **v3 已废弃** |
| `uniq_blacklist_active` | **软唯一(部分索引)** | `company_id, id_type, id_number` WHERE `status='ACTIVE'` | 是(仅 ACTIVE) | **v3 新增** | 阻止同证件号多条 ACTIVE |
| `idx_status_company` | 普通 | `status, company_id` | 否 | v2 | "显示已移除"开关查询 |
| `idx_created_at` | 普通 | `created_at DESC` | 否 | v1 | 默认排序 |

## 外键

| 字段 | 引用 | 关系 |
|---|---|---|
| `company_id` | `company.id` | 多对一(无显式 FK 约束,应用层校验) |
| `created_by` / `removed_by` / `restored_by` | `user.id` | 多对一(无显式 FK 约束) |
| `superseded_by` | `blacklist.id` | 自引用多对一(无显式 FK 约束) |

> 注: 项目不强制使用数据库外键(便于快速迭代),应用层校验。ER 图见 `er-diagram.md`。

## 状态枚举扩展历史

| 版本 | 状态枚举 | 触发 |
|---|---|---|
| v1 | `ACTIVE`, `REMOVED` | 初始 |
| v3 | + `SUPERSEDED`, `HISTORICAL` | BL-12 恢复 + 合并 + 预留归档 |

详见 `.hl/knowledge/enums/blacklist-status.md` + `state-machines/blacklist.md`

## 关键变更(v3 BL-12 方案 C 软唯一索引)

### 改造前 (v2)

```sql
CREATE UNIQUE INDEX uniq_active_blacklist
  ON blacklist(company_id, id_type, id_number, status);
```

问题: REMOVED 行不在唯一约束(因 status != ACTIVE), 但 ACTIVE 行唯一。同证件号新增 ACTIVE 后, 旧 REMOVED 无法恢复(唯一索引冲突)。

### 改造后 (v3 方案 C)

```sql
-- 删除 v2 硬唯一
DROP INDEX uniq_active_blacklist ON blacklist;

-- 新建 v3 软唯一 (仅 ACTIVE 受约束)
CREATE UNIQUE INDEX uniq_blacklist_active
  ON blacklist(company_id, id_type, id_number)
  WHERE status = 'ACTIVE';
-- MySQL 8.0+ 支持函数索引 / 部分索引
```

效果:
- 阻止同证件号多条 ACTIVE
- 允许同证件号多条 REMOVED / SUPERSEDED
- 恢复时可同证件号合并(参见 `state-machines/blacklist.md`)

## 关联

- ADR: `.hl/knowledge/adr/0001-bl12-restore-strategy.md`
- 业务规则: `docs/v3/prd.md §12 BL-12`
- 状态机: `state-machines/blacklist.md`
- 枚举: `enums/blacklist-status.md` + `enums/data-source.md`
- 迁移脚本: `migrations/v3_001_soft_unique_index.sql`