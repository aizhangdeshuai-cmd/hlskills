# 术语表模板(通用语言 / Ubiquitous Language)

> 复制本文件, 重命名为 `glossary.md` 放到 `knowledge/`。
> 本文件是项目的**通用语言**(Ubiquitous Language,DDD 概念):领域术语的标准叫法 + 定义 + 同义词。
> 目的:让 AI Agent 和人用同一套词汇,用 1 词代 20 词,变量/函数/文件命名一致,token 省。
> 来源:mattpocock/skills 的 CONTEXT.md 理念,沉淀进 hlkb 知识库。
> 维护:hlpm 步骤 1(需求分析)梳理时发现领域术语即记入;hldev 步骤 4.5(PRD 走查)时同步;与代码同 commit。

## 怎么用

- Agent 进入项目先读本表,用表内标准术语沟通(不说"那个东西""就是 XXX")
- 命名变量/函数/文件/类时,优先用本表术语(如术语"materialization cascade"→ 函数名 `materializeCascase()`)
- 发现新领域术语立即追加;发现同义词(同一概念多叫法)统一到标准叫法,标注弃用叫法
- PRD/测试用例/ADR 引用术语时,用标准叫法(不翻译不复述定义)

## 术语表

| 标准术语 | 定义 | 同义词/弃用叫法 | 引入版本 | 来源 |
|---------|------|----------------|---------|------|
| materialization cascade | 课程章节从"占位"变"真实文件系统占位"的级联过程 | "lesson real"、"section make real"(弃用) | v1 | PRD BL-3 |
| 黑名单 | 离职员工禁止再入职的记录集合 | "block list"(弃用)、"封禁列表" | v1 | 业务术语 |
| 软删除 | 不物理删除,标记状态为 REMOVED | "假删"、"标记删除"(弃用) | v1 | 通用 |
| 恢复 | 将 REMOVED 状态的记录改回 ACTIVE | "撤销删除"(弃用) | v3 | BL-12 |

## 命名映射(术语 → 代码命名)

| 术语 | 变量/函数命名 | 文件命名 | 表/字段 |
|------|-------------|---------|---------|
| 黑名单 | `blacklist` | `BlacklistService.java` | `blacklist` 表 |
| 软删除 | `softDelete` / `status=REMOVED` | - | `status` 字段 |
| 恢复 | `restore` | `BlacklistService#restore` | `restored_by/at/reason` |

## 关联

- PRD:`knowledge/doc/{ver}/prd.md`(术语首次出现处)
- ADR:`knowledge/adr/`(术语相关决策)
- 枚举:`knowledge/enums/`(术语对应枚举值)
