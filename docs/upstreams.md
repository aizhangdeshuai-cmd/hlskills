# 外部来源与本库实现

未单列日期的来源核对于 2026-11-20。下表记录采用的上游版本和本库的具体入口。hlskills 使用仓库内的技能文件、角色和脚本。更新本表时应核对相应目录的实际变化，保留 hlskills 自身的交付条件、角色权限和路径约定。

| 来源与固定版本 | 本库入口与采用范围 |
|---|---|
| 用户提供的 codebase-doc-reverse.zip（2026-11-24 核对，SHA-256 `1884b9d7e313b807aefef85355f7ed3654c469c9def01e8e7eb209428a3bed92`） | [hllegacy](../hllegacy/SKILL.md) 将 P1–P6、S1/S1-L、D1 和阶段门禁映射到既有知识条目。提交统计、实测核验和归档使用本库实现。[九类交付物规范](../hllegacy/deliverables.md) |
| [gstack v1.102.0.0](https://github.com/garrytan/gstack/releases/tag/v1.102.0.0) | [hlbrowse](../hlbrowse/SKILL.md) 提供独立浏览器驱动与迁移说明。[hltest](../hltest/SKILL.md)、[hldeploy](../hldeploy/SKILL.md) 用它收集 QA 和金丝雀证据。[hltoolbox](../hltoolbox/SKILL.md) 给出原索引中 16 项专项任务的本地做法。旧守护进程、真实浏览器 Cookie 导入和上游命令全集不在本库的兼容范围内。 |
| [oh-my-claudecode v5.8.4](https://github.com/Yeachan-Heo/oh-my-claudecode/releases/tag/v5.8.4) | 19 个同名角色与 v4.15.0 基线逐一比对，正文有变化的是 debugger、explore、scientist。hlskills 随库分发适配后的角色、[比对记录](../hlreview/references/upstreams.md)和[原许可](../agents/LICENSE-OMC)。 |
| [mattpocock/skills v1.3.2](https://github.com/mattpocock/skills/releases/tag/v1.3.2) | [hlreview](../hlreview/SKILL.md) 搜索目标项目的实际规范，并分别收集规则与需求的审查结论。[hlrefactor](../hlrefactor/SKILL.md) 将模块边界的评估落在真实调用方。 |
| [UI UX Pro Max v2.15.0](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/releases/tag/v2.15.0) | [hldesign](../hldesign/SKILL.md) 和 [hla11y](../hla11y/SKILL.md) 收录焦点、表单错误恢复、缩放长文本与减少动态效果的检查方法。 |
| [ECC v2.2.3](https://github.com/affaan-m/ECC/releases/tag/v2.2.3) | [hlresearch](../hlresearch/SKILL.md) 按一手来源、可比口径与证据缺口交付调研。[hlmedia](../hlmedia/SKILL.md) 用本地录屏、FFmpeg 与 ffprobe 完成原流程用到的抽帧、剪辑和证据关联。云端视频索引、语义检索不属于当前交付流程。 |
| [Superpowers v7.0.2](https://github.com/obra/superpowers/releases/tag/v7.0.2) | [hlreview](../hlreview/SKILL.md) 内置接收意见、对照证据和修复后复核的流程；需要独立审查时记录实际使用的上下文。 |
| goal-workflow / pm-skills（原始引用未提供可核实的唯一仓库与版本） | [hlpm](../hlpm/SKILL.md) 保留 v26 已纳入的可验证验收条件、非目标、假设、未决事项负责人与评审证据。跟踪状态为来源待确认。 |

## 本地版本合并

hlskills 工作区与既有安装副本同源于提交 `70a2528`。本次合并了后者的 v32/v33 修改，包括版本复盘、缺陷根因模板，以及创建项目约束文件时去重。产品到开发的交接仍按本库[交付清单](../hlpm/handoff-package.md)验证。历史版本的计划和审查留在 `docs/`，当前入口见[总索引](../SKILL.md)。

## 验证

从所选仓库根目录运行 `python3 hlsetup/install.py codex --check` 核对 Codex 安装来源，其他宿主可替换平台参数。验证业务页面时，按[浏览器操作与断言](../hlbrowse/SKILL.md#操作与断言)传入项目实际页面和预期结果。正式产品包按[交付清单](../hlpm/handoff-package.md)核验。
