---
name: hlkb-hooks
description: 一键把"代码改动→knowledge/ 同步"的 PreToolUse+PostToolUse hooks 装进项目。装后改接口/数据库/枚举/错误码/测试时改完提示,提交时漏同步会真阻断(PreToolUse exit 2)。提供 .hlskills 哨兵(只对 hlskills 涉及的项目生效,其他项目零干扰),--uninstall 一键卸载,含 --dry-run 模拟安装。Use when 希望 hooks 层面强制知识库同步、想机械化兜底"代码+文档同 commit"、或要在新项目复用 hlkb 同步策略。通过 Skill hlkb-hooks 调用。
---

# hlkb-hooks ── 知识库强同步 hooks

> 属于 `hlskills` 技能系统。配套 `hlkb`(项目知识库)使用,**单文件、单职责**:把同步检查机械化进 Claude Code 的 PreToolUse / PostToolUse,**不接管** hlpm / hldev / hlchain 流程。

> ## ⚠️ 能力边界声明(先读)
>
> 本技能**只在 Claude Code 真生效** —— PreToolUse 阻断靠 harness 真实执行 `exit 2 + stderr`,PostToolUse 提示靠 harness 真实执行 stdout。Codex CLI / Cursor **不解析 hooks**(根 README 第 137-144 行原话),需要走 `AGENTS.md` 铁律。
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
1. 放 `.hlskills` 哨兵(空文件)
2. 备份 `<项目>/.claude/settings.local.json` 到 `.claude/settings.local.json.hlkb-hooks.bak`
3. 注入 hooks(具体正则见 `presets.json` 当前选中的 preset,本节只列 default):
   - **PreToolUse(Bash)** ── `git commit` 时检查 `git diff --cached --name-only`,若有 src/api|controllers|routes|endpoints|hlpm|hldev|hlapi|hl-flow 改动但没对应 `knowledge/api|tests` 条目 → exit 2 阻断
   - **PostToolUse(Write|Edit|MultiEdit)** ── 改完文件立即 stdout 提示「🔔 接口/数据库/枚举/错误码/测试 请同步 knowledge/」

### 第 2 步:验证

装完会自动跑 6 项验证:
- ✅ JSON 格式合法
- ✅ PreToolUse matcher = `Bash`
- ✅ PostToolUse matcher = `Write|Edit|MultiEdit`
- ✅ 两条 command 字节数合理(1381 + 500)
- ✅ `.hlskills` 哨兵已放
- ✅ 备份存在

**真实拦截测试**(强烈建议跑一次):

```bash
echo stub > hlpm/_tmp_kb_test.md
git add hlpm/_tmp_kb_test.md
git commit -m "test"
# 预期:Claude Code harness 输出 🚨 知识库未同步: api:hlpm/_tmp_kb_test.md
# commit 失败

# 清理
git reset HEAD hlpm/_tmp_kb_test.md
rm hlpm/_tmp_kb_test.md
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

**单一可信源**:`install.sh` 同目录的 `presets.json`。当前内置 2 个 preset(default + java),表格仅供快速参考:

| 改动模式(default preset) | 期望同步 |
|---|---|
| `src/api/**`、`**/controllers/**`、`**/routes/**`、`**/endpoints/**` | `knowledge/api/` |
| `**/schema.sql`、`**/migrations/**`、`**/models/**`、`**/entities/**` | `knowledge/db/` |
| `**/Enum*`、`**/enums/**` | `knowledge/enums/` |
| `**/ErrorCode*`、`**/errors.*`、`hlerror/**` | `knowledge/error-codes/` |
| `*.test.*`、`**/__tests__/**`、`hltest/**` | `knowledge/tests/` |
| `hlpm/**`、`hldev/**`、`hlapi/**`、`hl-flow/**` | `knowledge/{api,tests,adr}`(产品/开发/接口段交文档) |
| `hldb/**`、`hladr/**` | `knowledge/{db,adr}`(数据库/架构决策) |
| 架构决策 / 术语新增 / 状态机变化 | hook 模式匹配不到,靠 `CLAUDE.md` 铁律 + 人工把关 |

**java preset** 见 `presets.json` → `java` 节点,核心差异:
- `*/controller/*Controller.java` 识别 Spring Boot Controller
- `*Mapper.java` / `*Repository.java` 触发 db 同步检查
- `*Test.java` / `*/test/**` 替代 `*.test.*` 触发 tests 同步检查

### Preset 选择

`install.sh` 支持 `--preset={default|java|路径}`,覆盖不同项目类型:

| Preset | 适用项目 | 关键差异 |
|---|---|---|
| **default**(默认) | 通用 Web:`src/api/**`、`controllers/**`、`routes/**` | 默认推荐,大部分前端/全栈项目 |
| **java** | Spring Boot / Java EE:`{module}/**/Controller.java`、`{module}/**/Mapper.java`、`migrations/*.sql` | 加 java 特定文件类型识别 |
| **ehr** | ehr 项目专用 | java preset + `ehr-report` / `report-admin-ui` 项目特定根目录 |

> **不要把项目特定目录名加进 `java` preset** —— 应该新建 `xxx` preset 复用 java 的 patterns。`ehr` preset 即为此模式:用 `--preset=ehr` 而不是污染通用 java。

```bash
# 通用项目
bash hlkb-hooks/install.sh

# Java/Spring Boot 项目
bash hlkb-hooks/install.sh --preset=java

# 自定义 preset(传 JSON 文件路径)
bash hlkb-hooks/install.sh --preset=/path/to/my-preset.json
```

**调正则**:编辑 `install.sh` 同目录下的 `presets.json`,增加自定义 preset,改完重跑 `bash hlkb-hooks/install.sh`(幂等)。

---

## 不在本技能范围

- ❌ **不接管 hlpm / hldev / hlchain 流程** —— 本技能只装 hooks,不调其他子技能
- ❌ **不改 `hlhooks/SKILL.md`** —— hooks 协议说明单一可信源在根 `hlhooks/SKILL.md`,本文件只引用不重复
- ❌ **不替你写 knowledge 条目** —— hook 只检查"改 src/** 有没有同时改 knowledge/**",内容质量靠 executor / analyst / architect 各自负责
- ❌ **不做 Codex / Cursor 适配** —— 那些平台没 hooks,需用 `AGENTS.md` 铁律(README 第 137-144 行)

---

## 验收 checklist(自己装完跑一遍)

- [ ] `.hlskills` 文件在项目根
- [ ] `.claude/settings.local.json` 备份存在(`.bak`)
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
| 职责 | 定义 11 类知识库 / 同步触发矩阵 / 模板 | 把触发矩阵**机械化**进 hooks |
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