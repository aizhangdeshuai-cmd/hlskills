# 测试覆盖模板(总测试库)

> 复制本文件, 重命名为 `{module}.md` 放到 `knowledge/tests/`。
> 一个模块一个文件,是该模块的**总测试库**:验收用例(黑盒)+ 代码层用例(白盒)+ 交叉追溯,累计当前状态,标注引入版本。
> - 验收用例:hlpm 步骤 8 产出(`docs/{ver}/test-cases.md` 为版本快照),hldev 步骤 10 沉淀到本文件
> - 代码层用例:hldev 步骤 10 基于本次 code diff 编写
> - 与代码同 commit 维护,跨版本持续更新(同 `knowledge/api/`、`knowledge/db/`)

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
| 版本快照 | `docs/v{N}/test-cases.md`(产品段当期产出,固定不变) |

## 一、验收用例(黑盒,hlpm 产出)

> 业务黑盒视角,基于 PRD + 设计双源编写。每个验收用例编号 `AC-NNN`,可反推 PRD 验收标准。

| AC ID | 标题 | 对应 PRD 规则 | 验收方法 | 引入版本 |
|---|---|---|---|---|
| AC-001 | 列表展示 10 字段 | BL-1 | 实际渲染对比 | v1 |
| AC-011 | 权限细粒度(view/create/import/remove) | BL-11 | 4 角色 × 4 权限点 | v1 |
| AC-012 | 恢复已移除黑名单 | BL-12 | 恢复操作 + 状态对比 | v3 |

## 二、代码层用例(白盒,hldev 产出)

> 覆盖验收用例写不出的代码层修改点:内部 API 异常分支 / DB 约束 / 缓存 / 并发 / 实现选型边界 / 重构回归点。

| 测试点 ID | 类型 | 覆盖的代码分支/修改点 | 对应 AC | 测试代码位置 | 引入版本 |
|---|---|---|---|---|---|
| UT-BL-001 | 内部分支 | `restore()` 的 null 入参分支 | AC-012 | `BlacklistServiceTest#restore_nullInput` | v3 |
| UT-BL-002 | DB 约束 | 软唯一索引 `uniq_blacklist_active` 冲突 | AC-007 | `BlacklistServiceTest#create_duplicateActive` | v3 |
| UT-BL-003 | 并发竞态 | 两人同时恢复同证件号(supersede 事务原子性) | AC-012 | `BlacklistServiceTest#restore_concurrent` | v3 |
| IT-BL-001 | 集成 | restore API 全链路(鉴权→service→DB→审计) | AC-012 | `BlacklistAPIIT#restore_fullChain` | v3 |

## 三、交叉追溯

| AC ID(验收) | 代码层覆盖(UT/IT) | 覆盖状态 |
|---|---|---|
| AC-001 | UT-BL-Display / IT-BL-List | ✅ |
| AC-011 | UT-BL-Permission | ✅ |
| AC-012 | UT-BL-001/003 + IT-BL-001 | ✅ |
| AC-XXX | (待补) | ⚠️ 待补 |

**规则**:
- 每个验收用例(AC-NNN)须在"代码层覆盖"列出现至少一次,或显式标注"由 xx 覆盖"
- 未覆盖的 AC 标 `⚠️ 待补`,不得遗漏
- **反模式禁止**:不得"照着实现写用例"——预期以 PRD 验收标准为准,代码偏离 PRD 时改代码不改用例

## 四、代码层用例类型说明

| 类型 | 含义 | 何时补 |
|---|---|---|
| 内部分支 | Service/Util 的 null/超时/降级/边界分支 | 每个新增/修改的函数 |
| DB 约束 | 唯一索引/外键/乐观锁/事务原子性 | 涉及 DDL 或数据一致性逻辑时 |
| 缓存 | 失效/穿透/雪崩/一致性 | 涉及缓存时 |
| 并发竞态 | 同一资源并发操作 | 涉及状态变更/资源争用时 |
| 实现选型 | 因技术选型带来的边界(软删除开关/部分索引/降级策略) | 有 ADR 支撑的选型 |
| 集成 | 跨层全链路(鉴权→service→DB→MQ) | 每个 API 至少 1 条 |

## 关联

- 版本快照: `docs/{ver}/test-cases.md`(hlpm 当期产出,固定不变)
- 一致性矩阵 §1: `docs/{ver}/consistency-matrix.md`("实现覆盖"列指向本文件测试点 ID)
- 涉及决策: `knowledge/adr/{NNNN}-{slug}.md`
- 状态机: `knowledge/state-machines/{entity}.md`
