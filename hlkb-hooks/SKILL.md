---
name: hlkb-hooks
description: 一键把"代码改动→knowledge/ 同步"的 PreToolUse+PostToolUse hooks 装进项目。装后改接口/数据库/枚举/错误码/测试时改完提示,提交时漏同步会真阻断(PreToolUse exit 2)。提供 .hlskills 哨兵(只对 hlskills 涉及的项目生效,其他项目零干扰),--uninstall 一键卸载,含 --dry-run 模拟安装。Use when 希望 hooks 层面强制知识库同步、想机械化兜底"代码+文档同 commit"、或要在新项目复用 hlkb 同步策略。通过 Skill hlkb-hooks 调用。
---

# hlkb-hooks ── 知识库强同步 hooks

> 属于 `hlskills` 技能系统。配套 `hlkb`(项目知识库)使用,**单文件、单职责**:把同步检查机械化进 Claude Code 的 PreToolUse / PostToolUse,**不接管** hlpm / hldev / hlchain 流程。

> ## ⚠️ 能力边界声明(先读)
>
> 本技能**只在 Claude Code 真生效** —— PreToolUse 阻断靠 harness 真实执行 `exit 2 + stderr`,PostToolUse 提示靠 harness 真实执行 stdout。Codex CLI / Cursor **不解析 hooks**（见根 README「平台支持分级」小节）,需要走 `AGENTS.md` 铁律。
>
> 配套项目内 `<项目>/CLAUDE.md` 写铁律才能提升 Agent 自觉率,否则 hook 兜底兜不住漏掉的(架构决策/术语新增/状态机变化,这些 hook 模式匹配不到)。

---

## 角色

| 角色 | Agent / 机制 |
|------|------|
| 执行人 | 用户(显式 `bash hlkb-hooks/install.sh`) |
| 运行时 | Claude Code harness(触发 PreToolUse / PostToolUse) |
| 同步责任人 | 项目内的 executor / analyst / architect / test-engineer 等角色 agent |

---

## 通用纪律

- **能力边界靠声明,不靠"绝对"措辞**:本技能阻断**只对 git commit 真生效**;Agent 写完代码忘同步,**PostToolUse 只能提示**,不能拦
- **可绕过路径保留**:`git commit --no-verify` 或 commit message 加 `[skip-kb-sync]` 都放行,不堵死紧急修复
- **哨兵文件防误伤**:只在放了 `.hlskills` 或已存在 `knowledge/` 的项目里启用 —— **其他项目零干扰**

---

## 流程(3 步)

### 第 1 步:装

```bash
cd <项目根>
# 通用项目(默认 preset)
bash hlkb-hooks/install.sh

# Java/Spring Boot 项目(ehr 项目就属于这一类)
bash hlkb-hooks/install.sh --preset=java
```

**做了什么**:
1. 缺少哨兵时创建带安装器标记的 `.hlskills`；保留原有哨兵
2. 已有设置首次改写前备份为 `.claude/settings.local.json.hlkb-hooks.bak`，已有备份保留
3. 保留原事件和处理器，追加带归属标记的 hooks(具体正则见 `presets.json` 当前选中的 preset,本节只列 default):
   - **PreToolUse(Bash)** ── `git commit` 时检查 `git diff --cached --name-only`,若有 src/api|controllers|routes|endpoints|hlpm|hldev|hlapi|hl-flow 改动但没对应 `knowledge/api|tests` 条目 → exit 2 阻断
   - **PostToolUse(Write|Edit|MultiEdit)** ── 改完文件立即 stdout 提示「🔔 接口/数据库/枚举/错误码/测试 请同步 knowledge/」

### 第 2 步:验证

检查 `.claude/settings.local.json`。PreToolUse / Bash 与 PostToolUse / Write|Edit|MultiEdit 各有一个以 `# hlkb-hooks managed command` 开头的处理器。已有处理器保留；重复安装或切换 preset 更新本技能的两条规则。

旧版内置 preset 的原始命令会在升级或卸载时识别；若旧版曾覆盖同事件配置，安装器从尚存的首次备份补回原有分组。已被旧版重复安装覆盖的备份、手动改写过的旧命令，需要与自己的配置历史核对。卸载保留备份与来源不明的旧哨兵。

**真实拦截测试**(强烈建议跑一次):

```bash
mkdir -p src/api
echo stub > src/api/_tmp_kb_test.md
git add src/api/_tmp_kb_test.md
git commit -m "test"
# 预期:Claude Code harness 输出 🚨 知识库未同步: api:src/api/_tmp_kb_test.md
# commit 失败

# 清理
git reset HEAD src/api/_tmp_kb_test.md
rm src/api/_tmp_kb_test.md
```

### 第 3 步:日常使用

```bash
# 改完代码,Claude Code 自动 PostToolUse 提示「🔔 同步知识库」
# → Agent 自觉同步 → git commit → hook 看到 src/** + knowledge/** 一起,放行

# 紧急跳过
git commit --no-verify -m "hotfix"
# 或
git commit -m "hotfix [skip-kb-sync]"

# 卸载
bash hlkb-hooks/install.sh --uninstall

# 模拟装(看会做什么,不真改)
bash hlkb-hooks/install.sh --dry-run
```

---

## 硬性关卡

| 关卡 | 触发 | 后果 |
|---|---|---|
| `git commit` 漏同步 | PreToolUse exit 2 + stderr | commit 失败,harness 把 stderr 反馈给 Agent |
| 改关键文件(接口/db/枚举/错误/测试) | PostToolUse stdout 提示 | Agent 看到提示,自觉同步 |
| `--no-verify` 或 `[skip-kb-sync]` | PreToolUse 直接 exit 0 | 放行(显式选择,记录在 commit message) |
| 无 `.hlskills` / 无 `knowledge/` | PreToolUse exit 0 | 不启用(非 hlskills 项目零干扰) |
| Codex / Cursor 平台 | 无 hook 解析 | 无效,改用 `AGENTS.md` 铁律 |

---

## 模式匹配规则(可调)

选择 `default`（通用）、`java`（Spring Boot）或 `ehr`（项目专用）。具体规则读取 [presets.json](presets.json) 中所选预设的 `patterns`：`root_dirs` 定义目录范围，分类的 `*_globs` 匹配代码路径，对应的 `sync_*_dir` 指定应同步的知识目录。

项目特有匹配放入专用预设。可用 `bash hlkb-hooks/install.sh --preset=/path/to/my-preset.json` 安装自定义配置。修改预设后以同一选项重新运行安装器。

## 路径验证工具:verify-paths.sh

`hlkb-hooks/verify-paths.sh` 是**独立**合规检查脚本,跟 install.sh / hooks 解耦:

```bash
# 当前项目
bash hlkb-hooks/verify-paths.sh

# 其他项目
bash hlkb-hooks/verify-paths.sh /path/to/project

# CI / PR 检查:任何违规就失败
bash hlkb-hooks/verify-paths.sh . --strict
```

默认模式列出路径笔误，扫描完成后返回 0。严格模式下，前四项任一命中即返回 1。参数、目录访问或扫描错误返回 2。

| # | 检查项 | 不通过时 |
|---|---|---|
| 1 | `.hl/knowledge/` 笔误(经典 ehr ADR-0002 案例) | 默认警告，严格模式失败 |
| 2 | `src/knowledge/` 笔误(知识库塞 src) | 默认警告，严格模式失败 |
| 3 | `docs/knowledge/` 笔误(迁到 docs 子目录) | 默认警告，严格模式失败 |
| 4 | `.knowledge/` 笔误(npm 风格误用) | 默认警告，严格模式失败 |
| 5 | `knowledge/` 真路径存在(13 类知识库归处) | 仅警告 |
| 6 | `.hl/memory/` 项目记忆保留(避免误伤真路径) | 仅信息 |

**排除规则**(避免误报):
- `knowledge/adr/{NNNN}-*.md`(ADR 文件讲决策本身,必然含旧路径证据)
- `knowledge/adr/README.md`(ADR 索引含 ADR 标题)
- `CLAUDE.md` / `AGENTS.md`(项目约束文件本身讲历史)
- `hlkb/SKILL.md` 或 `hlkb-hooks/SKILL.md`(规范文档反模式表必须含错误路径作反例)
- `hlkb-hooks/verify-paths.sh`(脚本自身输出含路径名)

**实测案例**:ehr 项目在 ADR-0002 通过此脚本验证 0 违规,把"修改效果"机械化。

---

## 不在本技能范围

- ❌ **不接管 hlpm / hldev / hlchain 流程** —— 本技能只装 hooks,不调其他子技能
- ❌ **不改 `hlhooks/SKILL.md`** —— hooks 协议说明单一可信源在根 `hlhooks/SKILL.md`,本文件只引用不重复
- ❌ **不替你写 knowledge 条目** —— hook 只检查"改 src/** 有没有同时改 knowledge/**",内容质量靠 executor / analyst / architect 各自负责
- ❌ **不做 Codex / Cursor 适配** —— 那些平台没 hooks,需用 `AGENTS.md` 铁律（见 README「平台支持分级」）

---

## 验收 checklist(自己装完跑一遍)

- [ ] `.hlskills` 文件在项目根
- [ ] 原先有设置文件时，确认首次备份仍存在
- [ ] `.claude/settings.local.json` 的 `hooks` 节含 `PreToolUse` + `PostToolUse`
- [ ] 真实跑漏同步 commit,**harness 真输出** `🚨 知识库未同步`
- [ ] 同步后 commit 成功
- [ ] `--no-verify` 跳过成功
- [ ] `[skip-kb-sync]` 在 message 里成功跳过
- [ ] (可选)把 `.hlskills` 加进 `.gitignore`(哨兵文件建议不跟 commit)

---

## 与 hlkb 主技能的关系

| 项 | `hlkb`(项目知识库 SOP) | `hlkb-hooks`(本技能) |
|---|---|---|
| 职责 | 定义 13 类知识库 / 同步触发矩阵 / 模板 | 把触发矩阵**机械化**进 hooks |
| 形式 | Markdown 文档 | `install.sh` + 真实 hooks |
| 调用 | `Skill hlkb` | `Skill hlkb-hooks` + `bash install.sh` |
| 配套 | 自己 | 引用 hlkb 的同步触发矩阵 |

**配套使用**:`Skill hlkb` 看规范 → `Skill hlkb-hooks` 装 hooks → 日常开发 hooks 兜底。

---

## 关联

- 上游:`hlkb/SKILL.md`(知识库总规范)
- 协议:`hlhooks/SKILL.md`(Claude Code hooks 真实协议,本文件不重复)
- 配套:`hl-permission`(一键授权,装完本 hooks 后可一起用)
- 写作规范:`hlwrite-skill/SKILL.md`(本文件按其规范写)