# v15 多视角深度审计(2026-06-26)

## 评审方法

4 个独立只读 sub agent 并行深度探查:
1. **工程结构与可维护性视角** — 长期漂移源、commit 史、frontmatter 健康度
2. **提示词质量与可执行性视角** — 文档作为 AI Agent 提示词的可执行性
3. **安全与隐私风险视角** — 凭据泄露、危险命令模板、prompt injection 面
4. **代表性子技能试跑视角** — 模拟 3 个真实场景,验证实际可跑通性

## 综合发现(按严重度 × 共识度排序)

### 🔴 P0(2 项, 应立刻修)

#### 1. agent description 24 处中文占位符未替换(提示词质量 + 试跑)
`agents/*.md` 中 `类型检查·构建` / `类型检查·构建命令(项目自带)` / `类型检查（针对改动文件）` 是未替换的中文占位文本——9 个 agent 文件共 24 次命中。
- 来源:之前清理 OMC 残留时 sed 替换不当
- 影响:Agent 加载时收到"24 处未知工具说明",行为不可预测
- 修法:改为 `<具体命令>` (按项目实际工具),或给出 3-5 个常见栈的具体示例

#### 2. `hlhooks/SKILL.md` hook 模板协议错配(安全)
第 25-49 行配置示例 (用 `"matcher": "Bash"` + `"hook": "danger-commands"`) 结构错误——直接 copy-paste 到 `~/.claude/settings.json` 会静默失效。
第 119-143 行模板输出 `{"hook_status": "blocked", "reason": "..."}` 但真实协议是退出码 0/2 + stdout JSON。
- 影响:用户以为有保护,实际无拦截 = 裸跑,但获得"已部署 hooks"的虚假心智模型
- 这比"知道没 hooks"更危险

### 🟡 P1(4 项, 结构性, 长期漂移)

#### 3. README 顶部加"能力边界声明"(试跑核心结论)
仓库是 markdown 工作流 SOP 库,不是带 hook 的运行时。 "角色边界铁律" / "硬性关卡" / "会签" 是文字纪律,Claude Code 实际不强制。陌生用户期望与现实错位。
- 修法:README 顶部明确"这是 SOP 库, 不是带 hook 的运行时" + "角色约束靠提示词自觉,非工具隔离"

#### 4. agent frontmatter `disallowedTools` 与正文描述不一致(提示词 + 工程)
`hlpm-product/SKILL.md:96-100` 明确把 `verifier` / `analyst` 列为只读,但 `agents/verifier.md` / `agents/designer.md` / `agents/qa-tester.md` / `agents/executor.md` / `agents/planner.md` 的 frontmatter **没有** `disallowedTools: Write, Edit`。
- 注意:不是"11 个都缺就该补 11 个"——需要按角色实际意图逐个判断(verifier 需写报告, executor 需改代码)
- 修法:逐 agent 判断, frontmatter 与文档角色边界对齐

#### 5. `request_user_input` → `AskUserQuestion` 工具名错配(试跑)
仓库反复用 `request_user_input`,但 Claude Code 实际工具名是 `AskUserQuestion`。
- 影响:Agent 按仓库指引调用 `request_user_input` 会失败
- 修法:全仓 grep + 替换

#### 6. `.gitignore` 加 `.dev-rejected` / `.product-archived` (工程)
`path-conventions.md:75-76` 明确定义了这 2 类标记文件, `.gitignore` 没覆盖。
- 影响:真实跑流程时 `git status` 会立刻看到一堆 0 字节空文件报警

### 🟢 P2(10 项, 一次性清理)

| # | 问题 | 来源 |
|---|------|------|
| 7 | "交付物数量"在 5 个文件里有 5 种说法(5/6/8/15) | 工程 |
| 8 | "流程总览"在 4 处独立陈述,子技能清单改一处要同步 4 处 | 工程 |
| 9 | SKILL.md description 含未经验证的 13+ 关键词路由 | 工程 |
| 10 | `hlhooks` "提交前检查" hook 只 echo 不阻塞 commit | 安全 |
| 11 | `hlbrowse` 引入 gstack 二进制走 `git clone ... && ./setup` 无 checksum/版本固定 | 安全 |
| 12 | `hl-permission` 默认全开 4 条权限,缺强警告 + 与 hlhooks 协同说明 | 安全 |
| 13 | 6 处 SKILL.md 教 Agent 读取"用户提供的截图/PDF"作为输入,无"外部内容不可信"提示 | 安全 |
| 14 | `hlbrowse` Cookie 导入功能无脱敏提示 | 安全 |
| 15 | `hlpm-product/consistency-rules.md` 模板代码块内嵌业务示例,Agent 复制时可能把示例当成真实规则 | 工程 |
| 16 | `agents/planner.md:38` 引用未定义的 `RALPLAN-DR` / `deliberate consensus mode` | 提示词 |
| 17 | `agents/designer.md:33` 硬编码特定模型版本"Opus 4.7" | 提示词 |
| 18 | `hlpm-product/SKILL.md:213` "核心模块 100% 无豁免"——LLM 没法机械判定 | 提示词 |

## 关键判断

仓库根本定位问题: **它是"写得极好的开发工作流 SOP 手册",不是"可执行的运行时"**。铁律 / 角色 / 门禁都是文字纪律不是 hook / agent / 状态机。

作为 SOP 库是**优秀**的;作为"AI 编码工作流运行时"它**未达宣传**。这是仓库根本定位问题,不是某条具体修复能解决的。

P3 修复建议(能力边界声明)就是把宣传与现实重新对齐。