# 审查流程与角色的上游对照

## 审查流程

本库在维护时比较下列发布版本，将选用的方法写入 hlreview。运行审查使用本地的技能、角色和项目证据。

| 来源 | 采用的方法与本地适配 |
|---|---|
| [Matt Pocock skills v1.3.2 · code-review](https://github.com/mattpocock/skills/blob/v1.3.2/skills/engineering/code-review/SKILL.md) | 固定比较基线，分别审查规范和需求；项目内文档或用户给定材料均可作为依据。 |
| [Superpowers v7.0.2 · 请求审查](https://github.com/obra/superpowers/blob/v7.0.2/skills/requesting-code-review/SKILL.md)、[接收审查](https://github.com/obra/superpowers/blob/v7.0.2/skills/receiving-code-review/SKILL.md) | 交接范围、验收和验证证据；对每条反馈核实、修复并复核。 |
| [ECC v2.2.3 · production-audit](https://github.com/affaan-m/ECC/blob/v2.2.3/skills/production-audit/SKILL.md)、[security-review](https://github.com/affaan-m/ECC/blob/v2.2.3/skills/security-review/SKILL.md) | 以版本对应的本地证据做生产准备度分级和封顶，按风险审查认证、数据、凭证和供应链。 |
| [gstack v1.102.0.0 · a0534ce 发布说明](https://github.com/garrytan/gstack/releases/tag/v1.102.0.0) | 将原有 review、cso、codex 引用替换为本库结构检查、静态安全审查和第二意见步骤。记录截断、复核失败和签核状态，保留可重查的证据。 |
| [OWASP Top 10:2025](https://top10.owasp.org/2025/) | security-reviewer 中的风险分类依据。检查项由本库根据角色职责编写。 |

## OMC 角色逐文件比较

比较 [OMC 4.15.0 源码提交 542b7a4](https://github.com/Yeachan-Heo/oh-my-claudecode/tree/542b7a4cf56fb1618d3b397603cca93bfdaa1df5/agents) 与 [OMC v5.8.4 正式发布的角色目录](https://github.com/Yeachan-Heo/oh-my-claudecode/tree/v5.8.4/agents) 中以下同名文件。旧版使用包内 package.json 标注的版本。本表用两份上游原文比较正文，最后一列说明本库的处理。上游 19 份角色均移除了 frontmatter 的 level 字段，此字段在 hlskills 原有角色中已经省略。仅 debugger、explore、scientist 的上游正文变化。

校验列取 v5.8.4 原始 `agents/<角色>.md` 完整字节的 SHA-256 前 12 位。在上游克隆中运行 `git show v5.8.4:agents/scientist.md | shasum -a 256` 可复核单项。已有衍生角色随仓保留 [OMC 的 MIT 版权与许可全文](../../agents/LICENSE-OMC)。

| 本地角色 | 上游文件 SHA-256 前缀 | 两版本上游正文 | 本库处理 |
|---|---|---|---|
| `analyst` | `4a2b6437fcca` | 相同 | 区分起草、缺口评审和一致性提取，版本 PRD 集中登记未确认需求、外部依赖和后续优化。 |
| `architect` | `3f5b0f6a97d7` | 相同 | 新建设计引用业务约束和契约，已有系统诊断核对源码及运行证据。 |
| `code-reviewer` | `1cb6f9f77bb3` | 相同 | 保留只读职责与专项检查，按本库规范和需求双轴给出证据、分级与结论。 |
| `code-simplifier` | `ad0bbcaeb000` | 相同 | 保留本库角色与权限。 |
| `critic` | `acf6fbf3958e` | 相同 | 单点可回退任务做短评，跨模块、高风险计划按实际分支深审。 |
| `debugger` | `1f93d3dc10ec` | 有变化 | 按委派区分诊断与修复，保留故障现场，在隔离副本查证因果。 |
| `designer` | `ea7828072d77` | 相同 | 区分视觉探索、版本原型和确认稿还原，按委派限定生产写入范围。 |
| `document-specialist` | `b90dc2de3d9a` | 相同 | 保留本库角色与权限。 |
| `executor` | `8390d97b9db3` | 相同 | 保留唯一写入者职责，允许用会话清单跟踪任务。 |
| `explore` | `306c3fb1b8ad` | 有变化 | 区分符号定义与引用查询，覆盖调用方，报告动态引用和未读范围。 |
| `git-master` | `dfe50a570826` | 相同 | 按可独立回退的业务变化分组，历史操作沿用项目 Git 规范及用户授权。 |
| `planner` | `9928a1b416ec` | 相同 | 共识计划按需启用，版本 PRD 与变更记录由调用方指定的写入者落盘。 |
| `qa-tester` | `460aeabde03a` | 相同 | 按实际候选执行浏览器、API 和 CLI 用例，回传范围、版本、TC 及证据。 |
| `scientist` | `ae4867e345e2` | 有变化 | 改为只读内存统计，返还汇总证据、样本量及局限，取消插件和磁盘报告要求。 |
| `security-reviewer` | `dd06b242b1e1` | 相同 | 保留只读职责，统一脱敏检查和依赖证据，校正 OWASP 2025 编号。 |
| `test-engineer` | `7acd13fce7cd` | 相同 | 区分产品侧业务用例和开发侧代码测试，沿用同一批 AC 与 TC。 |
| `tracer` | `6dd603a2e894` | 相同 | 保留本库角色与权限。 |
| `verifier` | `48076c6f6a29` | 相同 | 分别核验产品包、候选实现及生产证据，区分通过、证实失败和证据不足。 |
| `writer` | `bbbfb8c3968d` | 相同 | 保留本库角色与权限。 |
