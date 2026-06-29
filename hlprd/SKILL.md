---
name: hlprd
description: 将 hlpm 产品段产出的 8 项交付物(PRD/测试用例/验收标准/设计原型/一致性矩阵/自检报告等)合并成 Word (.docx) 标准交付包, 含项目名 + 业务方签字区. Use when hlpm 完成 (评审通过) 后, 需要给业务方输出一份可签字确认的文档. 通过 Skill hlprd "为 <项目名> 合成 v<N> 签字包" 调用.
---

# hlprd — 业务方签字文档合成

> 属于 `hlskills` 技能系统. **将 hlpm 8 项交付物合成 1 份 .docx, 含极简签字区.**

---

## ⚠️ 前置依赖

```bash
pip install python-docx
```

(轻依赖 ~3MB, 跨 Mac/Linux/Windows. SKILL.md 顶部明文标注, 用户首次跑本 skill 前自行安装.)

---

## ⚠️ 流程纪律的执行机制

本 skill **没有真编排器**, 完全靠 Agent 按本 SKILL.md 自觉执行. 如 Agent 模型弱或 prompt 冲突, 拼装顺序/字段映射可能错位.

**真实约束**: 文档 + Agent 自觉 + 用户手动打断.
**不是**: Claude Code runtime hook 拦截.

如发现输出 .docx 缺段/字段错位, 请**手动打断**让它重读本 SKILL.md 对应章节.

---

## 输入参数 (Agent 加载本 skill 后第一步用 AskUserQuestion 问)

| 问题 | 选项 |
|------|------|
| **Q1: 哪个版本?** | A. v1 / v2 / ... (用户说数字, Agent 校验 `docs/v1` 目录存在) |
| **Q2: 项目名?** | A. 自由输入 (从 PRD 标题自动提取作为默认建议) |
| **Q3: 业务方名称?** | A. 自由输入 (用于签字区"业务方签字"行) |

Q2/Q3 可省略 — 省略时 Agent 从 `prd.md` 标题自动提取项目名, 业务方名称留 "________".

---

## 文档结构 (6 大段 + 极简签字区)

> **总体原则**: 业务方不关心技术细节, 只关心 "要做什么 / 验收什么 / UI 长什么样 / 我签了就走".

### 第 1 段 · 封面
- 项目名 (Q2 输入或从 PRD 提取)
- 需求版本号 (vX)
- 文档生成日期 (`date "+%Y-%m-%d"`)
- 文档类型: 「需求交付包 vX」

### 第 2 段 · PRD 全文
读 `docs/{ver}/prd.md` 全文嵌入.

包含 6 大模块 (hlpm 默认输出):
- 业务逻辑 / 操作流程 / 数据流转 / 状态机 / 权限规则 / 非功能需求

> 用 .docx 标题 2 级 ("## XX"). 仅保留 6 大模块标题 + 文字, **不**嵌入任何 `<!-- dev-not-for-prod -->` 注释或 `data-prd` 属性 (PRD md 里若有, 在拼装时 strip 掉).

### 第 3 段 · 测试用例摘要
读 `docs/{ver}/test-cases.md` 全文嵌入.

业务方关注**优先级**:
- **主流程**: TC-001 ~ TC-020 (用户主链路, 取前 20 条)
- **边界**: TC 中所有 "边界" "最大值" "最小值" "空" "超时" 关键字相关
- **权限**: TC 中 "权限" "游客" "管理员" "无权限" 关键字相关

**不展开**技术细节 (步骤前置条件 / 测试数据 / 期望值), 仅保留:
- TC 编号 + 一句话描述
- (如 PRD 有标注优先级) 高/中/低标签

如测试用例总数 < 30 条, 全部嵌入.

### 第 4 段 · 验收标准
读 `docs/{ver}/acceptance-criteria.md` 全文嵌入, 逐条编号.

业务方逐条签认:
```
AC-1: 订单状态显示 5 种颜色徽章 — 待支付(灰)/ 已支付(蓝)/ 已完成(绿)/ 已取消(红)/ 退款中(橙)
AC-2: 列表默认仅显示 ACTIVE, 显示已移除开关开后显示全部
...
```

### 第 5 段 · 设计原型 (截图嵌入)
读 `docs/{ver}/design/screenshot*.png`:
- 每个 PNG 嵌入为 .docx 图片, **居中**, 宽度 6 英寸
- 图片下方加一行 caption: 「图 N: <原 HTML 文件名, 自动从同一目录版本匹配>」
- 如未截图 (步骤 6b.5 跳过或失败), 显示 "暂无截图 (查看 docs/{ver}/design/*.html)"

> **截图源自 hlpm 步骤 6b.5**. 本 skill 不自行截图 (依赖文档已明示).

### 第 6 段 · 一致性矩阵摘要
读 `docs/{ver}/consistency-matrix.md`:

**展示**:
- 业务规则覆盖矩阵 (表格)
- 状态机覆盖矩阵 (表格)
- 权限覆盖矩阵 (表格)

**不展示**:
- 非功能需求覆盖矩阵 (性能/安全/兼容 3 子表) — 业务方不关心
- 第 5 矩阵 (代码实现追踪矩阵) — 业务方不关心

### 第 7 段 · 自检报告 (轻量)
读 `docs/{ver}/handoff-self-check.md`:

**只展示**:
- 8 项交付物是否齐全 (✅/❌ 表格)
- 一致性矩阵是否全通过 (✅/❌)
- (其余明细不展示, 业务方不关心)

### 第 8 段 · 极简签字区
```
## 业务方签字

项目名: ____________________
版本号: v____

业务方签字: ________________________   签字日期: ____ 年 ____ 月 ____ 日
                (或)              签字日期: ____ - ____ - ____
```

**5 行横线 + 中文标签**, 打印后手写.
**日期双格式**: 业务方选填中文 "____ 年 ____ 月 ____ 日" 或数字 "____ - ____ - ____".

---

## 输出文件

- 路径: `docs/{ver}/sign-off-package.docx`
- 格式: Microsoft Word 2007+ (.docx)
- 生成工具: python-docx (`from docx import Document`)

---

## 实施细节 (.docx 排版规范)

### 页面设置
- 纸张: A4 (210×297mm)
- 边距: 上 2.5cm / 下 2.5cm / 左 2.5cm / 右 2.5cm (默认)
- 页眉: 左 "项目名" + 右 "v{ver}" (字体 9pt, 宋体)
- 页脚: 居中 "第 X 页 / 共 Y 页" (字体 9pt, 自动域)

### 段落样式
- 标题 1 (H1): 16pt 加粗, 黑体
- 标题 2 (H2): 14pt 加粗
- 标题 3 (H3): 12pt 加粗
- 正文: 11pt, 宋体, 行距 1.5 倍

### 表格样式
- 业务规则覆盖矩阵 / 状态机覆盖矩阵 / 权限覆盖矩阵 / 自检报告表
- 边框: 1pt 黑色实线
- 表头: 加粗 + 浅灰底色 (RGB F2F2F2)

### 图片
- 设计稿截图: 6 英寸宽, 居中
- 限制: 单张图最大 6 英寸, 总文档 < 10MB (避免 .docx 体积爆炸)

---

## Python 实现骨架

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import os, sys
from datetime import date

ver = sys.argv[1] or "v1"
project_name = sys.argv[2] or "项目"
docs_dir = f"docs/{ver}"
screenshots = sorted(glob(f"{docs_dir}/design/screenshot*.png"))

doc = Document()

# 页眉页脚
section = doc.sections[0]
section.header.paragraphs[0].text = f"{project_name}    v{ver}"
section.footer.paragraphs[0].text = "第 X 页 / 共 Y 页"

# 第 1 段: 封面
doc.add_heading(f"{project_name} - 需求交付包 {ver}", 0)
doc.add_paragraph(f"文档生成日期: {date.today().isoformat()}")
doc.add_paragraph(f"文档类型: 业务方签字确认")

# 第 2 段: PRD 全文
for line in open(f"{docs_dir}/prd.md", encoding="utf-8"):
    if line.startswith("# "): doc.add_heading(line[2:].strip(), 1)
    elif line.startswith("## "): doc.add_heading(line[3:].strip(), 2)
    elif line.startswith("### "): doc.add_heading(line[4:].strip(), 3)
    elif line.startswith("<!--"): continue   # strip dev-not-for-prod 注释
    elif line.strip(): doc.add_paragraph(line.rstrip())

# 第 3 段: 测试用例摘要 (top-20 by priority)
# 第 4 段: 验收标准 (全文)
# 第 5 段: 设计原型 (嵌入截图)
for i, png in enumerate(screenshots, 1):
    doc.add_picture(png, width=Inches(6))
    doc.add_paragraph(f"图 {i}: {os.path.basename(png.replace('.png', '.html'))}")
# 第 6 段: 一致性矩阵 (3 个表的过滤)
# 第 7 段: 自检报告 (轻量版)
# 第 8 段: 签字区
doc.add_paragraph("项目名: ____________________")
doc.add_paragraph("版本号: v____")
doc.add_paragraph("业务方签字: ________________________   签字日期: ____ 年 ____ 月 ____ 日")
doc.add_paragraph("                       (或)           签字日期: ____ - ____ - ____")

doc.save(f"{docs_dir}/sign-off-package.docx")
print(f"✅ 生成 {docs_dir}/sign-off-package.docx")
```

---

## 失败处理

### 文档获取失败的分级处理

**核心文件** (3 项, 缺一不可): `prd.md` / `acceptance-criteria.md` / `design/` (含 `screenshot*.png`)
**非核心文件** (5 项, 可缺): `test-cases.md` / `consistency-matrix.md` / `handoff-self-check.md` / `non-functional-requirements.md` / 一致性矩阵 第 5 矩阵 (代码实现追踪)

| 情况 | 严重度 | 处理 |
|------|--------|------|
| 整目录缺失 (`docs/vN/` 不存在) | 🔴 致命 | 仅对话警示, **不生成** docx |
| 版本 ver 不存在 (如 `docs/v5/` 不存在) | 🔴 致命 | 仅对话警示, **不生成** docx |
| 核心文件缺失 (PRD/验收/设计稿 任一缺失) | 🟡 核心不全 | 仅对话警示 + 列具体缺哪些文件, **不生成** docx |
| 非核心文件缺失 (5 项任一缺失) | 🟢 非核心不全 | 仍生成 docx, **缺失段用 "⚠️ 此段未生成" 占位**, docx **顶部加黄色警示框** |
| 文件存在但内容为空 (0 字节或仅标题) | 🟡 视为缺失 | 按"核心/非核心"分级 |
| 全部齐全 | ✅ 正常 | 生成完整 docx |

### 对话提示统一格式

Agent 加载本 skill 后, **第一步**用 Read 工具读所有 8 项交付物, 检测完整性. 如有缺失, 立即向用户报告:

```
⚠️ hlprd 文档获取不完整

版本: vN
状态: [致命/核心不全/非核心不全]

缺失的核心文件 (3 项):
  ❌ docs/vN/prd.md
  ❌ docs/vN/acceptance-criteria.md
  ❌ docs/vN/design/

缺失的非核心文件 (5 项):
  - docs/vN/test-cases.md
  - docs/vN/consistency-matrix.md
  ...

建议: 回到 Skill hlpm "为 <项目名> 跑 vN 完整流程" 补齐后再合成.
```

### docx 顶部黄色警示框 (仅"非核心不全"时生成)

当 Agent 决定仍生成 docx, 在文档第 1 页顶部插入 1 个黄色警告框 (1pt 黄色边框, 浅黄底色 FFFFB0):

```
⚠️ 文档不完整 — 本交付包基于 docs/vN/ 当前内容生成, 缺失以下非核心文件:
  - test-cases.md
  - consistency-matrix.md
  ...

缺失的章节显示为"⚠️ 此段文档未生成"占位, 请补走 hlpm 步骤 X 再重新合成.
版本: vN
生成时间: YYYY-MM-DD
```

> 警示框用 python-docx 的 `add_paragraph` + 自定义 RGB 颜色实现, 不依赖 docxtpl 模板.

### 缺失段占位格式 (各非核心章节)

当某非核心章节对应的文件缺失, Agent 不跳过该章节, 而是在 .docx 章节标题下插入占位提示:

```
## 测试用例摘要 (缺源文件)

⚠️ 此段文档未生成 — docs/vN/test-cases.md 缺失或为空.
请补走 hlpm 步骤 8 (测试用例编写) 后, 重新运行 Skill hlprd 合成.
```

### 致命情况不生成 docx (避免误发)

**核心文件缺失时不生成任何 docx**, 原因: 业务方拿到一份"PRD / 验收标准 / 设计稿"全空的 docx 会产生严重误解. Agent 引导用户先回 hlpm 补齐再合成, 避免产生不可用的签字包.

### 其他异常

| 失败情形 | 处理 |
|---------|------|
| python-docx 未装 | 告知用户: 「请先 `pip install python-docx`」 |
| `screenshot*.png` 缺失 (但 design/ 存在) | 第 5 段显示 "暂无截图" 占位, 仍生成 .docx |
| .docx 体积 > 10MB | 提示用户: 「考虑压缩截图, 或拆成多页 .docx」 |
| 读取某 .md 抛异常 (编码错误等) | 该段用"⚠️ 文档读取失败"占位, 继续生成其他段 |

---

## ⚠️ 流程纪律 (再次强调)

本 skill **没有真编排器**. Agent 加载后**自觉**:
1. 问 3 问题 (Q1/Q2/Q3)
2. 读 8 项交付物
3. 按 6 大段拼装
4. 生成 .docx

如 Agent 漏段 / 字段错位, 用户必须**手动打断**让 Agent 重读本 SKILL.md.

---

## 路径规范

- 输出文件: `docs/{ver}/sign-off-package.docx`
- 设计稿截图: `docs/{ver}/design/screenshot*.png` (来自 hlpm 步骤 6b.5)
- 8 项交付物来源: `docs/{ver}/` (来自 hlpm 步骤 11-12)

本文件不涉及 `path-conventions.md` 中央规范的变更, 仅作为 hlpm 流程的下游消费者.

