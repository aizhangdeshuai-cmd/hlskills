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

| 失败情形 | 处理 |
|---------|------|
| `docs/{ver}` 目录不存在 | 告知用户: 「该版本还没跑过 hlpm, 无交付物可合成」 |
| python-docx 未装 | 告知用户: 「请先 `pip install python-docx`」 |
| 无 `screenshot*.png` | 第 5 段显示 "暂无截图" 占位, 仍生成 .docx |
| PRD / 一致性矩阵 缺失 | 跳过该段, 在 .docx 末尾加 "⚠️ 缺失文档: X.md" |
| .docx 体积 > 10MB | 提示用户: 「考虑压缩截图, 或拆成多页 .docx」 |

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

