# 第五阶段：交付与发布

13. **交付验证**（`verifier` 主导：创建完成标记）
    - 验收所有文档与功能完整性
    - 按适用条件验证 14 类项目文档（8 类产品段 + 6 类开发段补充，按 `hlpm/path-conventions.md`）。步骤 10 写入的跨版本总测试库由 12.7 单独验收。
    - 完成步骤 9–12.7 和适用的发布前补充验收后再处理分支。若用户决定丢弃，则记录放弃的候选 SHA 并结束当前链路，保留拒收或验收历史，不创建开发完成标记。
    - 保留候选时，先由执行者运行 `python3 "$HLPM_DIR/version.py" mark "$VERSION_DIR" complete`，在实际版本目录记录已开发。保留本期验收与复盘记录再按用户选择保留分支、开 PR 或合并。
    - 收尾前保存需要交付的内容并确认最终 SHA。合并、解决冲突或补交形成新提交时，发布前取得最终提交的必需验证记录。保留分支时保留其工作区，清理前核对交付及所有权。

14. **发布交接**：将候选 SHA、测试报告、生产审计、变更范围和适用的迁移／回滚证据交给 [hlrelease](../hlrelease/SKILL.md)。是否发布及推送由用户授权。

15. **部署交接**：等待 hlrelease 确认远端发布完成；仅用已核对的标签、完整提交、产物标识、目标环境和回滚计划向 [hldeploy](../hldeploy/SKILL.md) 交接。未选发布、无同版本发布证据或部署未获授权时，停在相应阶段。

15.5. **★ 开发段复盘**(v32 新增,自我进化信号采集)
    - **时机**: 步骤 13 交付验证通过后(14/15 用户确认不阻塞本步)
    - **写入**：从项目根运行 `python3 "$HLPM_DIR/version.py" retro . "$VERSION_DIR"`，对照 `package` 核实产品交接并更新其 `report` 的开发段信号。记录候选 SHA 和完成日期；单独运行时可新建。历史文件归属按[复盘约定](../hlpm/path-conventions.md#022-包身份与复盘)核对。
    - **采集项**(如实填写,无则写"无"):
      1. 交付物拒收统计: 步骤 0 拒收次数 + 拒收原因分类(**拒收原因指向 hlpm 的改进点**, retro 回顾时重点看)
      2. 7.5 走查偏离统计(⚠️/➕ 行数 + 偏离类型)
      3. 12.5 覆盖率审计: 覆盖率数值 + 差异清单分类
      4. 发布准备度和未关闭的风险（步骤 12）
      5. 代码审查 finding 采纳/拒绝比(v26 advisory 纪律执行情况)
      6. 本期修复的 bug 数 + 根因是否已全部沉淀 `knowledge/pitfalls/`(hlbug 步骤 14 的强制项,此处核对)
    - **用途**: 与产品段信号合并,供 hlchain 第五步"retro 模式回顾"产出技能修改提案(只提案,人审合入)
    - **豁免**: 无——每个版本都写

---

## 交付文档清单（开发段补充）

开发段在产品段 8 类交付物(5 必出 + 3 条件出)基础上，补充以下 6 类，编号与 `hlpm/path-conventions.md` §3.2 对齐。步骤 10 同时更新跨版本总测试库 `knowledge/tests/{module}.md`，由 hlkb 单独维护。

| # | 文档 | 路径 | 负责 Agent | 步骤 |
|---|------|------|-----------|------|
| 9 | 技术设计文档 | `knowledge/tech-design.md` | `architect`(内容)→ `executor`(落盘) | 3 |
| 10 | 架构决策记录 | `knowledge/adr/*.md` | `architect`(内容)→ `executor`(落盘) | 3 |
| 11 | 用户操作手册 | `knowledge/user/manual.md` | `writer` | 13 |
| 12 | 帮助文档 | `knowledge/user/help.md` | `writer` | 13 |
| 13 | 变更日志 | `CHANGELOG.md` | `executor` | 13 |
| 14 | 回滚方案 | `knowledge/rollback.md` | `architect`(内容)→ `executor`(落盘) | 13 |

> 注:`architect` / `planner` 等只读或路径受限 agent 仅负责**内容生成**,文件落盘统一由 `executor` 执行(参照 hlpm 对 `analyst` 的"生成内容→主 agent 写入"模式)。`CHANGELOG.md` 在仓库根,不在 `planner` 的 `docs/plans` / `docs/drafts` 输出范围内,故由 `executor` 落盘。

---
