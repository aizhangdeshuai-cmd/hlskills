# v15 发布后 4 视角综合评审(2026-06-26)

## 评审方法

4 个独立只读 sub agent 并行探查:
1. **新用户体验视角** — 模拟陌生开发者刚 clone 仓库
2. **Claude Code 规范合规性视角** — 对照 Claude Code 原生 skill/subagent 规范
3. **跨文件一致性视角** — 量化扫描所有 .md 的一致性
4. **工程实践视角** — 仓库维护健康度

综合阶段合并去重(多视角指向同一问题只列一次)。

## 评审结论

仓库在 v15 收口后已处于"clone 下来真能用"的基本线,但仍有 8 处硬伤(4 处 P0 + 5 处 P1)和 10 处观感问题(P2)。

## P0 (4 项, 全部已修)

| # | 问题 | 修复 commit |
|---|------|------|
| 1 | SKILL.md 表格 `hla11y` 出现两次,破坏"25 项"声明 | 6d7f5a7 |
| 2 | `hlpm-product/INTRO.md:249` 版本号仍是 v14 与 v15 冲突 | 6d7f5a7 |
| 3 | README 第 55 行 `effort` 是 frontmatter 字段 的不实声明 | 6d7f5a7 |
| 4 | 空目录 `docs/v1/analysis/` + README 列出不一致 | 6d7f5a7 |

## P1 (5 项, 全部已修)

| # | 问题 | 修复 commit |
|---|------|------|
| 5 | README 加"调用语法示例"段 (`Skill hlpm(...)`) | 6d7f5a7 |
| 6 | 19 个 agent description 去 (Opus)/(Sonnet)/(Haiku) + 精简 Use when | 6d7f5a7 |
| 7 | `hlpm-product/consistency-rules.md` 第 304-432 行整段"v11 自动化规划"改造 | 6d7f5a7 |
| 8 | `push-to-github.sh` 安全化重写(去硬编码 + 用户确认) | 6d7f5a7 |
| 9 | `hlPermission` → `hl-permission` 重命名(跨平台大小写归一) | 6d7f5a7 |

## P2 (10 项, 待下版本处理)

- agent description 末尾 `(Opus)` 等模型名(已在 P1 中同步处理,这里标记为冗余)
- `hltest/SKILL.md` 描述 vs 表格命令不统一
- `docs/v1/` 演示包 24 处 v13 字样(README 已注明但 grep 仍命中)
- gstack 调用两种写法:`Skill gstack` vs `Skill gstack <技能名>`
- 跨文件"流程速览表"重复 4 处
- `docs/v2/` `docs/v3/` 在文档中提及但实际不存在(属预期,但易误判)
- `hlPermission --off` 命令形式不在 Claude Code Skill 规范内
- 命名风格混用:全小写 / 小写+连字符 / 大写 / 字母数字混写
- `SKILL.md:5` 徽章依赖 `img.shields.io` 外部 CDN(离线破图)
- `docs/v1/` 演示包顶部 README 注明但未统一处理 v13 字样

## 公认做得好

- 三平台诚实声明(README 平台支持分级章节)
- 19 个 agent 的 `disallowedTools` 与角色行为对齐
- frontmatter 字段全部为 Claude Code 原生
- commit 历史干净(12 个 commit,语义化前缀)
- `docs/v1/` 已有 README 注明"非当前版本"
- `.gitignore` 关键项齐全