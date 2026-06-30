---
name: hlprd
description: 将 hlpm 产品段产出的 8 项交付物 (PRD/测试/验收/设计/矩阵/自检/非功能) 融合成 1 份传统 PRD 文档 (.docx): 封面 + 业务背景 + In-Scope + Out-of-Scope + 验收标准 + 参考资料, 不含签字区. Use when hlpm 完成后, 需要 1 份"业务方 + 开发都看"的传统产品需求文档. 通过 Skill hlprd "为 <项目名> 合成 v<N> PRD 文档" 调用.
---

# hlprd — 传统 PRD 文档合成

> 属于 `hlskills` 技能系统. **读 hlpm 8 项交付物融合成 1 份传统 PRD 文档 (.docx).**

---

## ⚠️ 前置依赖

```bash
pip install python-docx pillow
```

(轻依赖 ~3MB, 跨 Mac/Linux/Windows. SKILL.md 顶部明文标注, 用户首次跑本 skill 前自行安装. Pillow 用于截图压缩.)

---

## ⚠️ 流程纪律的执行机制

本 skill **没有真编排器**, 完全靠 Agent 按本 SKILL.md 自觉执行. 如 Agent 模型弱或 prompt 冲突, 拼装顺序/字段映射可能错位.

**真实约束**: 文档 + Agent 自觉 + 用户手动打断.
**不是**: Claude Code runtime hook 拦截.

如发现输出 .docx 缺段 / 字段错位, 请**手动打断**让 Agent 重读本 SKILL.md.

---

## 输入参数 (Agent 加载本 skill 后第一步用 AskUserQuestion 问)

| 问题 | 选项 |
|------|------|
| **Q1: 哪个版本?** | A. v1 / v2 / ... (用户说数字, Agent 校验 `docs/v1` 目录存在) |
| **Q2: 项目名?** | A. 自由输入 (从 `prd.md` 标题自动提取作为默认建议) |

Q2 可省略 — 省略时 Agent 从 `prd.md` 标题自动提取.

---

## 文档结构 (6 段传统 PRD)

> **总体原则**: 这是**业务方 + 开发团队都看的传统产品需求文档**, 不是签字包. **不嵌入** `<!-- dev-not-for-prod -->` 注释或 `data-prd` 属性, 一律 strip.

| 段 | 标题 | 来源 | 缺失处理 |
|----|------|------|---------|
| 0 | 封面 | 项目名 + 版本 + 日期 + 导读 | 必填 |
| 1 | 业务背景与目标 | `prd.md` §0 (上下文/依据) + §1 (业务逻辑) 摘要 | 核心, 缺失不生成 |
| 2 | 本次要做的 (In-Scope) | `prd.md` §4 (范围) + §1 (业务逻辑) 摘要 | 核心, 缺失不生成 |
| 3 | 本次不做的 (Out-of-Scope) | `prd.md` §4 (范围外) + §8 (不在范围) 摘要 | 核心, 缺失不生成 |
| 4 | 验收标准 | `acceptance-criteria.md` 全文 + AC 编号 | 核心, 缺失不生成 |
| 5 | 参考资料 | 8 项交付物名称 + 路径 (1 页索引) | 非核心, 缺失占位 |

> **4 个核心段** (1/2/3/4) 缺失 → 不生成 docx, 提示用户回 hlpm 补齐.
> **1 个非核心段** (5 参考资料) 缺失 → 占位提示, 仍生成 docx.

---

## 输出文件

- 路径: `docs/{ver}/prd-summary.docx`
- 格式: Microsoft Word 2007+ (.docx)
- 生成工具: python-docx (`from docx import Document`)

---

## 实施细节 (.docx 排版规范)

### 页面设置
- 纸张: A4 (210×297mm)
- 边距: 上 2.5cm / 下 2.5cm / 左 2.5cm / 右 2.5cm
- 页眉: "项目名    v{ver}" (字体 9pt, 宋体, 居中)
- 页脚: "第 X 页 / 共 Y 页" (字体 9pt, **用 Word PAGE/NUMPAGES 域**, 不要拼字符串)

### 段落样式
- Normal 段落: 字体宋体 + 11pt + 行距 1.5 倍
- 标题 1 (段标题): 16pt 加粗, 黑体
- 标题 2 (子节): 14pt 加粗
- 标题 3 (子子节): 12pt 加粗

### 表格样式
- 参考资料表: 边框 1pt 黑色实线, 表头加粗浅灰底色

### 修复 4 类已知问题 (必避)
1. **页脚页码空文本** → 用 Word PAGE/NUMPAGES 域, 不要拼字符串
2. **表格 0 个** → `render_markdown_to_docx()` 解析 markdown 表格 → 真实 docx 表格
3. **正文字体全默认** → `setup_default_styles()` 显式设 宋体/11pt/1.5 倍
4. **README/SKILL.md 文档堆叠无逻辑** → 业务背景/范围/验收分段, 不堆全 8 段

---

## Python 实现骨架 (完整可运行)

下面代码是**完整可运行**的 Python 脚本, 集成 4 类修复 + 6 段 PRD 结构. 直接 `python build_prd.py v2 "项目名"` 可生成合规 .docx.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hlprd · 融合 v{N} 传统 PRD 文档
读 hlpm 8 项交付物 → 输出 docs/{ver}/prd-summary.docx
修复 4 类已知问题
1. 页脚页码用 Word PAGE / NUMPAGES 域
2. 表格用通用 markdown 解析器
3. 段落 Normal 字体/字号/行距显式设置
4. 6 段 PRD 结构, 不堆 8 段
"""
import os, sys, glob
from datetime import date
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# === 修复 1: 页脚页码用 Word 域 ===
def add_page_field(paragraph):
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    run._r.append(instrText)
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar2)


def add_numpages_field(paragraph):
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'NUMPAGES'
    run._r.append(instrText)
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar2)


# === 修复 3: 段落样式 ===
def setup_default_styles(doc):
    from docx.shared import Pt
    normal = doc.styles['Normal']
    normal.font.name = '宋体'
    normal.font.size = Pt(11)
    if normal.element.rPr is None:
        rPr = OxmlElement('w:rPr')
        normal.element.append(rPr)
    rFonts = normal.element.rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        normal.element.rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), '宋体')
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    normal.paragraph_format.line_spacing = 1.5

    for level, size in [(1, 16), (2, 14), (3, 12)]:
        style = doc.styles[f'Heading {level}']
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.name = '宋体'
        if style.element.rPr is None:
            rPr = OxmlElement('w:rPr')
            style.element.append(rPr)
        rFonts = style.element.rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            style.element.rPr.append(rFonts)
        rFonts.set(qn('w:eastAsia'), '黑体')


# === 修复 2: markdown 段落+表格解析器 ===
def render_markdown_to_docx(doc, md_content, max_lines=None):
    """解析 markdown 内容, 段落和表格分别渲染到 docx."""
    lines = md_content.split('\n')
    if max_lines:
        lines = lines[:max_lines]
    i = 0
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            max_cols = max((len(r) for r in table_rows), default=1)
            t = doc.add_table(rows=len(table_rows), cols=max_cols)
            t.style = 'Table Grid'
            for r_idx, row in enumerate(table_rows):
                for c_idx in range(max_cols):
                    if c_idx < len(row):
                        t.rows[r_idx].cells[c_idx].text = row[c_idx]
            table_rows = []

    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith('|') and line.endswith('|'):
            if '---' in line and set(line.replace('|', '').replace(':', '').replace('-', '').strip()) == set():
                i += 1
                continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            table_rows.append(cells)
            in_table = True
            i += 1
        elif in_table and line.strip() == '':
            peek = lines[i+1].strip() if i+1 < len(lines) else ''
            if not peek.startswith('|'):
                flush_table()
                in_table = False
            i += 1
        else:
            flush_table()
            in_table = False
            if line.startswith('#### '):
                p = doc.add_paragraph(line[5:].strip())
                p.runs[0].font.bold = True
                p.runs[0].font.size = Pt(11)
            elif line.startswith('### '):
                doc.add_heading(line[4:].strip(), 4)
            elif line.startswith('## '):
                doc.add_heading(line[3:].strip(), 3)
            elif line.startswith('# '):
                doc.add_heading(line[2:].strip(), 2)
            elif line.strip():
                doc.add_paragraph(line)
            i += 1
    flush_table()


# === 通用: 从 markdown 提取特定章节内容 ===
def extract_section(prd_path, section_keyword, max_chars=600):
    """从 prd.md 提取包含 section_keyword 的 ## 章节, 返回内容字符串.
    遇下一个 ## 章节 或 连续 3 行以 | 开头 (markdown 表格) 停止. 限制 max_chars 防溢出.
    """
    if not prd_path or not os.path.exists(prd_path):
        return ""
    with open(prd_path, encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    in_section = False
    result = []
    char_count = 0
    table_streak = 0
    for line in lines:
        s = line.strip()
        if s.startswith('## ') and section_keyword in s:
            in_section = True
            continue
        if in_section and s.startswith('## ') and section_keyword not in s:
            break
        if in_section:
            if s.startswith('|'):
                table_streak += 1
                if table_streak >= 3:
                    break
            else:
                table_streak = 0
            if not s.startswith('<!--'):
                if s.startswith('`') and s.count('`') >= 3:
                    continue
                result.append(line)
                char_count += len(line)
                if char_count > max_chars:
                    result.append('...(内容过长, 省略)')
                    break
    return '\n'.join(result)


# === 主流程 ===
def extract_project_name(prd_path):
    with open(prd_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                title = line[2:].strip()
                # 去掉 "PRD · " 前缀
                import re
                return re.sub(r'^(PRD|PRD ·|产品需求文档)\s*[·:]?\s*', '', title).strip()
    return "项目"


def build_prd(ver, project_name=None):
    """hlprd 主流程: 读 hlpm 8 项交付物, 融合成 docs/{ver}/prd-summary.docx (传统 PRD 6 段)"""
    docs_dir = f"docs/{ver}"
    prd_path = f"{docs_dir}/prd.md"
    ac_path = f"{docs_dir}/acceptance-criteria.md"

    # === 前置检查: 4 个核心段 (PRD + AC 必须存在) ===
    if not os.path.exists(docs_dir):
        print(f"❌ docs/{ver}/ 不存在, 请先跑 Skill hlpm 跑通 v{ver}")
        return False
    if not os.path.exists(prd_path):
        print(f"❌ docs/{ver}/prd.md 缺失, 核心段 1 (业务背景) 无法生成, 不生成 .docx")
        return False
    if not os.path.exists(ac_path):
        print(f"❌ docs/{ver}/acceptance-criteria.md 缺失, 核心段 4 (验收标准) 无法生成, 不生成 .docx")
        return False

    project_name = project_name or extract_project_name(prd_path) or "项目"

    # === 创建文档 ===
    doc = Document()
    setup_default_styles(doc)

    # 页面设置 A4
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # 页眉
    section.header.paragraphs[0].text = f"{project_name} - 产品需求文档 (PRD)    v{ver}"
    section.header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 页脚 (PAGE/NUMPAGES 域)
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.text = ""
    p.add_run("第 ")
    add_page_field(p)
    p.add_run(" 页 / 共 ")
    add_numpages_field(p)
    p.add_run(" 页")

    # === 段 0: 封面 ===
    doc.add_heading(f"{project_name}", 0)
    doc.add_paragraph(f"产品需求文档 (PRD) - v{ver}")
    doc.add_paragraph(f"文档生成日期: {date.today().isoformat()}")
    doc.add_paragraph()

    doc.add_heading("导读", 1)
    doc.add_paragraph("本文件是基于 hlpm 阶段产出的 8 项交付物融合的传统产品需求文档 (PRD), 供业务方 + 开发团队共同评审使用.")
    doc.add_paragraph("文档结构 (6 段):")
    items = [
        "1. 业务背景与目标: 这个项目要解决什么问题? 为什么做?",
        "2. 本次要做的 (In-Scope): 包含哪些功能?",
        "3. 本次不做的 (Out-of-Scope): 不包含哪些? 避免范围蔓延.",
        "4. 验收标准: 怎么算做完了?",
        "5. 参考资料: 8 项交付物索引 (测试用例/设计/矩阵/自检等)",
    ]
    for item in items:
        doc.add_paragraph(f"  • {item}")
    doc.add_paragraph()
    doc.add_paragraph("阅读建议: 业务方重点关注 1/2/3/4 节, 技术团队补充 5 节了解全貌.")

    # === 段 1: 业务背景与目标 ===
    doc.add_heading("一、业务背景与目标", 1)
    doc.add_paragraph("📌 本节来源: prd.md §0 上下文与依据, §1 业务逻辑", style='Intense Quote' if 'Intense Quote' in [s.name for s in doc.styles] else None)
    bg = extract_section(prd_path, '上下文')
    if bg:
        render_markdown_to_docx(doc, bg, max_lines=80)
    else:
        bg2 = extract_section(prd_path, '业务背景')
        if bg2:
            render_markdown_to_docx(doc, bg2, max_lines=80)
        else:
            doc.add_paragraph("⚠️ 此段内容缺失: prd.md 中未找到「上下文」或「业务背景」章节")
    target = extract_section(prd_path, '目标')
    if target:
        doc.add_paragraph()
        render_markdown_to_docx(doc, target, max_lines=40)
    else:
        target2 = extract_section(prd_path, '业务目标')
        if target2:
            doc.add_paragraph()
            render_markdown_to_docx(doc, target2, max_lines=40)

    # === 段 2: 本次要做的 (In-Scope) ===
    doc.add_heading("二、本次要做的 (In-Scope)", 1)
    doc.add_paragraph("📌 本节来源: prd.md §4 范围, §1 业务逻辑, §2 操作流程", style='Intense Quote' if 'Intense Quote' in [s.name for s in doc.styles] else None)
    in_scope = extract_section(prd_path, '范围')
    if in_scope:
        render_markdown_to_docx(doc, in_scope, max_lines=100)
    else:
        doc.add_paragraph("⚠️ 此段内容缺失: prd.md 中未找到「范围」章节")
    # 补充: 业务逻辑 (In-Scope 的功能列表)
    bl = extract_section(prd_path, '业务逻辑')
    if bl:
        doc.add_paragraph()
        doc.add_heading("功能详细说明", 2)
        render_markdown_to_docx(doc, bl, max_lines=120)

    # === 段 3: 本次不做的 (Out-of-Scope) ===
    doc.add_heading("三、本次不做的 (Out-of-Scope)", 1)
    doc.add_paragraph("📌 本节来源: prd.md §4 范围外, §8 不在产品段范围", style='Intense Quote' if 'Intense Quote' in [s.name for s in doc.styles] else None)
    doc.add_paragraph("⚠️ 这一节业务方最关心 — 避免后续范围蔓延. 任何 PRD 未列出的功能, 不在本次范围.")
    out_scope = extract_section(prd_path, '范围外')
    if out_scope:
        render_markdown_to_docx(doc, out_scope, max_lines=60)
    else:
        out_scope2 = extract_section(prd_path, '不在')
        if out_scope2:
            render_markdown_to_docx(doc, out_scope2, max_lines=60)
        else:
            doc.add_paragraph("⚠️ prd.md 中未找到「范围外」章节, 业务方如对范围有疑问需向 PM 确认")

    # === 段 4: 验收标准 ===
    doc.add_heading("四、验收标准", 1)
    doc.add_paragraph("📌 本节来源: acceptance-criteria.md (AC 列表)", style='Intense Quote' if 'Intense Quote' in [s.name for s in doc.styles] else None)
    with open(ac_path, encoding='utf-8') as f:
        ac_text = f.read()
    render_markdown_to_docx(doc, ac_text, max_lines=200)

    # === 段 5: 参考资料 ===
    doc.add_heading("五、参考资料", 1)
    doc.add_paragraph("📌 本节来源: docs/{ver}/ 目录下 8 项交付物索引. 供技术团队补充阅读, 业务方可跳过.")
    doc.add_paragraph()

    ref_table = doc.add_table(rows=9, cols=3)
    ref_table.style = 'Table Grid'
    # 表头
    ref_table.rows[0].cells[0].text = "#"
    ref_table.rows[0].cells[1].text = "交付物"
    ref_table.rows[0].cells[2].text = "路径"
    for cell in ref_table.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True

    artifacts = [
        ("1", "PRD (产品需求文档原文)", "prd.md"),
        ("2", "测试用例", "test-cases.md"),
        ("3", "验收标准 (全文已嵌入段 4)", "acceptance-criteria.md"),
        ("4", "设计稿 (HTML 原型 + 截图)", "design/"),
        ("5", "一致性矩阵", "consistency-matrix.md"),
        ("6", "自检报告", "handoff-self-check.md"),
        ("7", "非功能需求", "non-functional-requirements.md"),
        ("8", "本 PRD 摘要文档 (本文件)", "prd-summary.docx"),
    ]
    for i, (num, name, path) in enumerate(artifacts, 1):
        ref_table.rows[i].cells[0].text = num
        ref_table.rows[i].cells[1].text = name
        ref_table.rows[i].cells[2].text = f"docs/{ver}/{path}"

    # === 段尾说明 ===
    doc.add_paragraph()
    doc.add_paragraph("📝 本文档由 hlprd 技能自动生成, 基于 hlpm 阶段产出. 修改建议:")
    doc.add_paragraph("  • PRD 内容: 回到 Skill hlpm '为 <项目> 跑 v{N} 完整流程' 修改")
    doc.add_paragraph("  • 本文档结构 / 排版: 修改 hlprd/SKILL.md")

    # === 保存 ===
    out_path = f"{docs_dir}/prd-summary.docx"
    doc.save(out_path)
    print(f"✅ 生成 {out_path}")
    return True


if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    build_prd(ver, project_name)
```

**注意**: 这段代码集成 4 类修复 + 6 段 PRD 结构. 拷贝到 `docs/{ver}/build_prd.py` 即可跑.

---

## 失败处理

### 文档获取失败的分级处理

**核心文件** (2 项, 缺一不可): `prd.md` / `acceptance-criteria.md`
**可选文件** (5 项, 缺一不致命): `test-cases.md` / `consistency-matrix.md` / `handoff-self-check.md` / `non-functional-requirements.md` / `design/`

| 情况 | 严重度 | 处理 |
|------|--------|------|
| `docs/{ver}` 目录缺失 | 🔴 致命 | 仅对话警示, **不生成** docx |
| 版本 ver 不存在 (如 `docs/v5/` 不存在) | 🔴 致命 | 仅对话警示, **不生成** docx |
| 核心文件缺失 (PRD / 验收 任一缺失) | 🟡 核心不全 | 仅对话警示 + 列缺哪些, **不生成** docx |
| 可选文件缺失 (测试/矩阵/自检/非功能/设计 任一缺失) | 🟢 可选不全 | 仍生成 docx, 缺失段用 "⚠️ 此节内容缺失" 占位 |
| 文件存在但内容为空 (0 字节或仅标题) | 🟡 视为缺失 | 按"核心/可选"分级 |
| 全部齐全 | ✅ 正常 | 生成完整 docx |

### 对话提示统一格式

Agent 加载本 skill 后, **第一步**用 Read 工具读 8 项交付物, 检测完整性. 如有缺失, 立即向用户报告:

```
⚠️ hlprd 文档获取不完整

版本: vN
状态: [致命/核心不全/可选不全]

缺失的核心文件 (2 项):
  ❌ docs/vN/prd.md
  ❌ docs/vN/acceptance-criteria.md

缺失的可选文件 (5 项):
  - docs/vN/test-cases.md
  - docs/vN/consistency-matrix.md
  ...

建议: 回到 Skill hlpm "为 <项目名> 跑 vN 完整流程" 补齐后再合成.
```

### 致命情况不生成 docx (避免误发)

**核心文件缺失时不生成任何 docx**, 原因: 业务方拿到"PRD / 验收标准"全空的 docx 会产生严重误解. Agent 引导用户先回 hlpm 补齐再合成, 避免产生不可用的 PRD 摘要文档.

### 其他异常

| 失败情形 | 处理 |
|---------|------|
| python-docx 未装 | 告知用户: 「请先 `pip install python-docx pillow`」 |
| 读取某 .md 抛异常 (编码错误等) | 该段用"⚠️ 文档读取失败"占位, 继续生成其他段 |

---

> **路径规范**: 输出文件 `docs/{ver}/prd-summary.docx`. 来源 8 项交付物位于 `docs/{ver}/` (来自 hlpm 步骤 11-12).