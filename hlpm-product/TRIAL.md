---
name: hlpm-product-trial
description: hlpm-product 试用说明(10 分钟跑通版)。用 1 个真实小需求,step-by-step 演示"启动 → 回答 3 问题 → 看到交付物 → 准备交接给开发"。Use when 用户问"试用一下 hlpm-product"/"能不能跑个 demo"/"先看个例子"。
---

# hlpm-product 试用说明(10 分钟跑通)

> **跟着做,就能跑通一个完整流程**
> 正式使用见 [`README.md`](./README.md),技能概览见 [`INTRO.md`](./INTRO.md)

---

## 这个试用做什么

我们用一个**真实小需求**走一遍 `hlpm-product`:

> **需求**:为主入口 SKILL.md 加 1 行 v13 状态徽章

预计耗时:10-15 分钟
预计产出:7 个文档,全部在 `docs/v1/`

---

## 试用前置

**你需要的**:
- 一个 `hlpm-product` 可用的环境(Claude Code / Codex / Cursor)
- 一个空项目目录(没有 `.hl/` 也没有 `docs/`,模拟全新项目)
- 不需要写任何代码

**不需要的**:
- 不需要已有项目
- 不需要设计规范
- 不需要 git 知识

---

## 试用流程(跟着做)

### Step 1: 准备空项目(2 分钟)

打开终端:

```bash
mkdir -p ~/hlpm-product-trial
cd ~/hlpm-product-trial
git init
```

在 IDE 中打开这个目录(`code ~/hlpm-product-trial` 或 `cursor ~/hlpm-product-trial`)。

### Step 2: 启动 hlpm-product(30 秒)

在 AI 对话框中输入:

```
启动 hlpm-product。我有个新需求:为主入口 SKILL.md 加 1 行 v13 状态徽章(顶部加一行显示当前版本 + 评审模式)
```

AI 会回应启动检查清单 + 3 个问题。

### Step 3: 回答 3 个问题(1 分钟)

AI 会问:

**Q1 需求规模**
- 选 A(轻量需求) — 业务规则 1 条,改 1 个模块

**Q2 涉及设计**
- 选 A(涉及) — 加徽章是 UI 变化

**Q3 评审模式**
- 选 B(3 合 1) — 轻量需求默认,跑得快

### Step 4: 等待 AI 跑流程(3-5 分钟)

AI 会自动执行(不需要你做什么):

```
✓ 扫描项目上下文(无 memory,无 docs)
✓ 0.6 步:扫描历史版本 → 无 → 自动建 docs/v1/
✓ 步骤 1:需求分析
✓ 步骤 2:竞品分析 → 轻量模式跳过
✓ 步骤 4:PRD 编写(6 大模块)
✓ 步骤 6a.1:设计规范检查 → 未发现,继续
✓ 步骤 6a.2:保真度咨询 → 中保真(默认)
✓ 步骤 6b:设计稿(中保真 HTML)
✓ 步骤 8:测试用例
✓ 步骤 9a:集中评审(3 角色自审)
✓ 步骤 9.5:一致性终检(2 矩阵 ✅)
✓ 步骤 10/11:验收标准 + 自检报告
✓ 步骤 12:打包交付
```

**AI 可能会在某些步骤问你**(正常):
- "PRD 里这条业务规则是不是这样?" → 确认 / 修正
- "设计稿里徽章用这个颜色可以吗?" → 确认
- "测试用例覆盖这些场景够吗?" → 确认 / 补充

### Step 5: 查看产出物(2 分钟)

完成后,AI 会告诉你产出在 `docs/v1/`。打开看:

```bash
cd ~/hlpm-product-trial
ls -la docs/v1/
```

你应该看到:
```
docs/v1/
├── prd.md                              # 你的 PRD
├── test-cases.md                       # 你的测试用例
├── acceptance-criteria.md              # 验收标准
├── non-functional-requirements.md      # 非功能需求
├── consistency-matrix.md               # 一致性矩阵
├── handoff-self-check.md               # 自检报告
├── design/
│   └── version-badge.html              # 设计稿
└── analysis/                           # 轻量模式可能空
```

**快速检查**:
- [ ] 7 个文件都在
- [ ] `prd.md` 里有"v13 状态徽章"业务规则
- [ ] `test-cases.md` 里有 TC-001/TC-002 这种编号
- [ ] `consistency-matrix.md` 全部 ✅

### Step 6: 模拟开发接手(2 分钟)

虽然我们这次不实际改代码,但可以**模拟 hlpm-dev 步骤 0 的验证**:

```bash
# 模拟开发段 0 步验证
echo "=== 验证交付物齐全 ==="
for f in prd.md test-cases.md acceptance-criteria.md non-functional-requirements.md consistency-matrix.md handoff-self-check.md; do
  if [ -f "docs/v1/$f" ]; then
    echo "✅ docs/v1/$f"
  else
    echo "❌ docs/v1/$f 缺失"
  fi
done

echo ""
echo "=== 验证版本一致性 ==="
grep "v1" docs/v1/prd.md | head -1
grep "v1" docs/v1/test-cases.md | head -1
grep "v1" docs/v1/consistency-matrix.md | head -1

echo ""
echo "=== 验证一致性矩阵 ==="
if grep -q "全部" docs/v1/consistency-matrix.md && ! grep -q "❌" docs/v1/consistency-matrix.md; then
  echo "✅ 一致性矩阵全部通过"
else
  echo "❌ 一致性矩阵有 ❌ 项"
fi
```

如果全 ✅,模拟开发接手成功。

### Step 7: (可选)实际改代码

如果你想真做这一步(需要 git 知识):

```bash
# 在 main 分支加徽章
echo "" >> SKILL.md
echo "![version](https://img.shields.io/badge/hlpm--product-v13-blue)" >> SKILL.md
git add SKILL.md docs/v1/
git commit -m "v1: 加 v13 状态徽章"
```

然后在 `docs/v1/` 创建标记文件:
```bash
touch docs/v1/.dev-completed
git add docs/v1/.dev-completed
git commit -m "v1: 标记为已开发"
```

---

## 试用结束

**你刚才体验了**:
- ✅ 启动产品段(0 阶段)
- ✅ 回答 3 个阻塞问题
- ✅ 看到 AI 自动跑 12 步(轻量 + 3 合 1)
- ✅ 拿到 7 个交付物
- ✅ 模拟开发接手验证

**总耗时**:10-15 分钟
**代码量**:0 行(产品段不写代码)
**产出文档**:7 个

---

## 试完后你可以

| 想做什么 | 看哪里 |
|---------|-------|
| 了解技能定位 | [`INTRO.md`](./INTRO.md) |
| 正式使用(完整规则) | [`README.md`](./README.md) |
| 改其他文件 | `hlpm-dev` 流程 |
| 试用其他技能 | `hlpm` / `hlpmnew` / `hlbug` 等 |

---

## 进阶试用(可选,20 分钟)

如果上面跑得太顺,想试个**复杂需求**:

### 试 2: 加 1 个完整功能(标准规模)

需求:为主入口加"子技能搜索"功能(顶部搜索框,实时筛选 25 个子技能)

按上面同样流程启动,但 Q1 选 B(标准)、Q3 选 A(联合评审)。

**会多跑**:
- 完整竞品分析(2b/2c)
- 完整设计阶段(6a.1/6a.2/6b/7)
- 3 场独立评审(5/7/9)
- 7 个一致性矩阵

**预计耗时**:20-30 分钟
**预计产出**:10+ 个文档,3000+ 行

### 试 3: 多需求并发(进阶)

跑完试 1 后,在不结束产品段的情况下,启动一个新需求:"把 SKILL.md 的描述加 1 行:包含 26 项子技能"(实际还是 25,故意设计为冲突需求)。

AI 会怎么处理?
- 选项 1:发现是同一项目的延续 → 在 v1 上修改
- 选项 2:发现是独立需求 → 建 v2
- 选项 3:你明确告诉它"新建版本" → 建 v2

**这是 v12 版本目录的实战应用**。

---

## 试用常见问题

### Q1: AI 答错了怎么办?

试用中 AI 可能犯错(如 PRD 写错业务规则)。**直接告诉它修正**:

```
"PRD 里 BR-1 应该是 xxx,不是 yyy,改一下"
```

它会回到对应步骤修改,触发强同步(自动重走后续评审)。

### Q2: AI 卡在某一步不动了?

3 步排查:
1. 看 AI 的最后一条消息 — 是不是在等你回答?
2. 主动问 AI:"你卡在哪个步骤?需要我做什么?"
3. 必要时重新启动产品段

### Q3: 想换路径(轻量→标准)?

告诉 AI:
```
"这个需求实际比我想的复杂,升级到标准需求 + 联合评审"
```

它会:
- 已完成的步骤不重做
- 补齐跳过的步骤(竞品/中间评审)
- 后续按新路径走

### Q4: 想跳过某些步骤?

试用中**不推荐跳过** — 流程完整跑一遍才能理解全貌。
正式用时,根据 0.5 步骤选择。

### Q5: 试用中遇到 bug?

这是试用,**欢迎反馈**! 记录以下信息:
- 你用的是什么 AI(Claude Code / Codex / Cursor)
- 你的需求原文
- AI 的哪一步出问题
- AI 的错误输出

在主仓库开 issue 反馈。

---

## 试用清单(勾选)

跑完一遍后,勾选确认你体验了:

- [ ] 启动产品段(看到启动检查清单)
- [ ] 回答 3 个问题
- [ ] 看到自动建版本目录
- [ ] 看到 PRD 生成
- [ ] 看到设计稿生成
- [ ] 看到测试用例生成
- [ ] 看到集中评审(3 角色自审)
- [ ] 看到一致性矩阵(全部 ✅)
- [ ] 看到自检报告
- [ ] 7 个交付物都在 `docs/v1/`
- [ ] 模拟开发接手验证全部 ✅

**全勾了** → 试用成功!可以正式用了。
**有未勾** → 哪个步骤出问题?反馈给 AI 或主仓库。

---

## 试用结束语

恭喜你跑通了 `hlpm-product`! 🎉

记住几个关键点:
1. **3 个问题决定一切** — 规模 / 设计 / 评审模式
2. **产品段不改代码** — 这是铁律
3. **3 场评审是 1 场** — 选 3 合 1 时
4. **版本目录自动建** — 不需要你操心
5. **交付物在 docs/v{ver}/** — 8 项交给开发

后续:
- 想正式用 → [`README.md`](./README.md)
- 想深入了解 → [`INTRO.md`](./INTRO.md)
- 想看硬性规则 → [`SKILL.md`](./SKILL.md)
