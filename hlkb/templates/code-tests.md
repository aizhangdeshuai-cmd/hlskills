# 代码层测试覆盖模板

> 复制本文件, 重命名为 `{module}.md` 放到 `knowledge/tests/`。
> 一个模块一个文件,记录该模块代码层测试点 ↔ 验收用例(AC) ↔ 测试代码路径的交叉追溯。
> 由 `hldev` 步骤 10 基于本次 code diff 编写并维护,与代码同 commit。

## 模块基本信息

| 项 | 值 |
|---|---|
| 模块名 | `blacklist` |
| 中文名 | 黑名单服务 |
| 引入版本 | v1 / v3 扩展 |
| 源码路径 | `src/main/java/.../BlacklistService.java` |
| 测试代码路径 | `src/test/java/.../BlacklistServiceTest.java`(按项目语言约定,不写死) |
| 关联接口知识库 | `knowledge/api/blacklist.md` |
| 关联数据库知识库 | `knowledge/db/blacklist.md` |

## 代码层测试点(白盒)

> 覆盖 hlpm 验收用例写不出的代码层修改点:内部 API 异常分支 / DB 约束 / 缓存 / 并发 / 实现选型边界 / 重构回归点。

| 测试点 ID | 类型 | 覆盖的代码分支/修改点 | 对应 AC | 测试代码位置 | 引入版本 |
|---|---|---|---|---|---|
| UT-BL-001 | 内部分支 | `restore()` 的 null 入参分支 | AC-011 | `BlacklistServiceTest#restore_nullInput` | v3 |
| UT-BL-002 | DB 约束 | 软唯一索引 `uniq_blacklist_active` 冲突 | AC-007 | `BlacklistServiceTest#create_duplicateActive` | v3 |
| UT-BL-003 | 并发竞态 | 两人同时恢复同证件号(supersede 事务原子性) | AC-011 | `BlacklistServiceTest#restore_concurrent` | v3 |
| UT-BL-004 | 实现选型 | 方案 C 软唯一:REMOVED 行不受约束 | AC-010 | `BlacklistServiceTest#create_removedNotUnique` | v3 |
| IT-BL-001 | 集成 | restore API 全链路(鉴权→service→DB→审计) | AC-011 | `BlacklistAPIIT#restore_fullChain` | v3 |

## 类型说明

| 类型 | 含义 | 何时补 |
|---|---|---|
| 内部分支 | Service/Util 的 null/超时/降级/边界分支 | 每个新增/修改的函数 |
| DB 约束 | 唯一索引/外键/乐观锁/事务原子性 | 涉及 DDL 或数据一致性逻辑时 |
| 缓存 | 失效/穿透/雪崩/一致性 | 涉及缓存时 |
| 并发竞态 | 同一资源并发操作 | 涉及状态变更/资源争用时 |
| 实现选型 | 因技术选型带来的边界(软删除开关/部分索引/降级策略) | 有 ADR 支撑的选型 |
| 集成 | 跨层全链路(鉴权→service→DB→MQ) | 每个 API 至少 1 条 |

## 交叉验证

- 每个验收用例(AC-NNN)须在本表"对应 AC"列出现至少一次,或显式标注"由 xx 覆盖"
- 未覆盖的 AC 标 `⚠️ 待补`,不得遗漏
- **反模式禁止**:不得"照着实现写用例"——预期以 PRD 验收标准为准,代码偏离 PRD 时改代码不改用例

## 关联

- 验收用例: `docs/{ver}/test-cases.md`(hlpm 产出)
- 一致性矩阵 §1: `docs/{ver}/consistency-matrix.md`(实现覆盖列指向本文件测试点 ID)
- 涉及决策: `knowledge/adr/{NNNN}-{slug}.md`
- 状态机: `knowledge/state-machines/{entity}.md`
