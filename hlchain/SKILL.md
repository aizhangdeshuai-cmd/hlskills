---
name: hlchain
description: 全流程编排技能,按顺序依次加载 hlpm(产品段)→ hldev(开发段)→ hlrelease(发布)→ hldeploy(部署), 过程中可调用 hlbug(事故修复) + hltest(独立测试)。Use when 用户想"一次跑完需求→开发→测试→发布→部署"全链路, 而不是手动一次次调各技能。通过 /hlchain 调用。
---

# hlchain — 全流程编排

> 属于 `hlskills` 技能系统。**编排器**(orchestrator)类型技能, 不包含新流程, 而是**依次加载其他 6 个子技能**完成端到端。

> ## ⚠️ 编排器的诚实声明
>
> 本技能**没有真正的编排器 runtime**——不是 hook / 不是状态机 / 不是自动门禁。Agent 加载本 SKILL.md 后**按文档顺序自觉**依次调 `Skill hlpm` → `Skill hldev` → ...。**所有"阶段门禁"靠 Agent 自觉 + 用户手动打断**。
>
> 详细能力边界见仓库 `README.md` 「⚠️ 能力边界声明」段。

---

## 编排的 6 个子技能

| 阶段 | 调用 Skill | 阶段输出物 | 默认跳过？ |
|------|-----------|------------|----------|
| 1 | `Skill hlpm "..."` | `docs/vN/` 8 项产品交付物 | 否(必经) |
| 2 | `Skill hldev "..."` | 完成开发 + 内置测试/审计/发布 | 否(必经) |
| 3 | `Skill hlrelease "..."` | 生成 CHANGELOG + git tag + push | **可选**(hldev 步骤 14 已内置) |
| 4 | `Skill hldeploy "..."` | 部署到生产环境 | **可选**(用户可手动部署) |
| 5 | `Skill hltest "..."` | 独立测试阶段补充 | **可选**(hldev 步骤 10-11 已内置) |
| 6 | `Skill hlbug "..."` | 任何阶段遇到 bug 时调用 | **条件**(仅在测试/审计发现问题) |

---

## 模式 C (A+B 结合): Agent 自觉顺序 + 显式交接段

### A: Agent 自觉顺序
加载本 SKILL.md 后, Agent 按上述表格顺序逐阶段加载, 每完成一阶段**检查输出物是否存在**再进入下一阶段。

### B: 显式交接段
**每个被编排的子技能 SKILL.md 末尾都有"## 交接段"**, 提示 Agent 完成该技能后**调 `Skill hlchain "进入下一阶段: <下一阶段名>"` 继续**。

---

## 用户调用示例

### 完整全链路

```
用户: Skill hlchain "为订单列表加导出 CSV 按钮"

Agent:
  1. 加载 hlpm (23 步产品段)
     输出: docs/v1/ 下 8 项交付物 (prd.md / test-cases.md / 设计稿 HTML 等)
  2. 询问用户: "产品段完成, 是否进入开发段?"
     用户: "继续"
  3. 加载 hldev (15 步开发段)
     输出: 提交记录 + 通过的测试
  4. 询问用户: "开发段完成, 是否发布?"
     用户: "发布"
  5. 加载 hlrelease
     输出: CHANGELOG.md + git tag v1.0.0 + push
  6. 询问用户: "是否部署到生产?"
     用户: "先不, 我自己部署"
  7. (跳过 hldeploy) 链结束
```

### 跳过/替换/终止

用户可在任意阶段说:
- **"跳过 hlrelease"** → 跳过发布阶段
- **"在这里停"** → 终止编排, 不调下一个
- **"改用 hlbug"** → 当前阶段挂起, 调 hlbug 修, 修完回到原阶段

---

## Agent 加载本技能后的执行规范

### 第一步: 用 AskUserQuestion 问 3 个问题

```
问题 1: 全链路范围?
  A. 完整 6 阶段 (hlpm + hldev + hlrelease + hldeploy + hltest + hlbug)
  B. 仅核心 4 阶段 (hlpm + hldev + hlrelease + hldeploy, 跳 hltest/hlbug)
  C. 仅到开发段 (hlpm + hldev, 后面用户手动接力)
  D. 自定义 (用户指定)

问题 2: 是否启用集中评审模式 (替代分阶段评审)?
  (此问题在 hlpm 步骤 0.5 也会问, 如已在 hlchain 问过则跳)

问题 3: 部署目标环境?
  (此问题在 hldeploy 也会问, 如已在 hlchain 问过则跳)
```

### 第二步: 按用户回答展开链路

- 如果选 A: 完整跑 6 个阶段
- 如果选 B: 跑 hlpm → hldev → hlrelease → hldeploy, hltest 和 hlbug 仅在 bug 出现时调用
- 如果选 C: 跑到 hldev 结束, 后面的让用户手动
- 如果选 D: 按用户指令展开

### 第三步: 每阶段完成后检查输出物

每个阶段完成时, Agent **必须验证**输出物是否存在:

| 阶段 | 验证输出物 |
|------|----------|
| hlpm 完成 | `docs/vN/` 存在 + 8 项交付物文件非空 |
| hldev 完成 | git log 有新 commit + 测试报告 |
| hlrelease 完成 | `CHANGELOG.md` 更新 + git tag 存在 |
| hldeploy 完成 | 部署日志有成功标记 |

### 第四步: 每阶段完成后询问用户是否继续

```
hlpm 完成。输出物已生成于 docs/v1/。
下一步: 加载 Skill hldev 开始开发?

[选项]
- A. 继续 (加载 hldev)
- B. 暂停 (我先看看产品段产出, 之后再继续)
- C. 跳过 hldev, 直接到 hlrelease (罕见, 仅适合仅文档化场景)
```

---

## 与其他子技能的关系

### 互补关系 (本技能编排的)
- **hlpm** → 产出 `docs/vN/` 8 项产品交付物
- **hldev** → 接手 `docs/vN/` 8 项交付物, 完成开发
- **hlrelease** → 接手 git 历史, 生成 CHANGELOG + tag
- **hldeploy** → 接手 tag, 部署到环境
- **hltest** → 补充独立测试阶段 (hldev 内部测试不够时)
- **hlbug** → 任意阶段发现问题, 修复后回到原阶段

### 不被本技能编排的 (独立可用)
- `hlquickstart` / `hlsetup` / `hlpermission` / `hlhooks` 等是工具型技能, hlchain 不自动调

---

## 强制约束

1. **不修改任何子技能的核心流程**: hlpm / hldev / hlrelease / hldeploy / hltest / hlbug 的步骤不变, 仅在每个 SKILL.md 末尾加"## 交接段"段
2. **不做覆盖: hlchain 不替代上述 6 个技能, 只是顺序加载它们**
3. **所有"自动门禁"靠 Agent 自觉**: Agent 不会因 hlchain 缺失某阶段而拒绝继续
4. **失败处理**: 任一阶段失败 (如 hlpm 被拒收), hlchain 应建议回到前一阶段或终止

---

## 路径规范

本文件不涉及 `docs/` 路径, 无需引用 `path-conventions.md`。