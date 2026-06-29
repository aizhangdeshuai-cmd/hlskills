---
name: hlprd
description: 将 hlpm 产品段产出的 8 项交付物 (PRD/测试用例/验收标准/设计原型/一致性矩阵/自检报告/非功能需求等) 融合成 1 份 Word (.docx) 业务方签字包, 含设计稿截图 + 4 角色评审勾选表 + 业务方签字区. Use when hlpm 完成 (评审通过) 后, 需要给业务方输出一份可签字确认的文档. 通过 Skill hlprd "为 <项目名> 合成 v<N> 签字包" 调用.
---

# hlprd — 业务方签字文档合成

> 属于 `hlskills` 技能系统. **读 hlpm 8 项交付物融合成 1 份 .docx, 含设计稿截图 + 4 角色评审表 + 业务方签字区.**

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
| **Q3: 业务方名称?** | A. 自由输入 (用于签字区"业务方签字"行, 留空时显示 "________") |
| **Q4: 4 角色负责人姓名?** | A. 自由填 PM/TL/QA/UI 姓名 (可省略, 留 "________" 待用户手填) |

Q2/Q3/Q4 可省略 — 省略时 Agent 从 `prd.md` 标题/版本号自动提取, 4 角色姓名留 "________".

---

## 文档结构 (8 段 + 签字区)

> **总体原则**: 业务方关心"要做什么 / 验收什么 / UI 长什么样 / 我签了就走", 不关心技术细节. **不嵌入** `<!-- dev-not-for-prod -->` 注释或 `data-prd` 属性, 一律 strip.

| 段 | 标题 | 来源 | 缺失处理 |
|----|------|------|---------|
| 1 | 封面 | 项目名 + 版本 + 日期 | 必填 |
| 2 | PRD 摘要 | `prd.md` 提取业务逻辑 + 数据流转 + 状态机 + 权限 | 核心, 缺失不生成 |
| 3 | 测试用例摘要 | `test-cases.md` 摘要 (主流程 + 边界 + 权限) | 非核心, 缺失占位 |
| 4 | 验收标准 | `acceptance-criteria.md` 全文 + AC 编号 | 核心, 缺失不生成 |
| 5 | 设计原型 | `design/screenshot*.png` 嵌入 | 非核心, 缺失占位 |
| 6 | 一致性矩阵摘要 | `consistency-matrix.md` 关键表 | 非核心, 缺失占位 |
| 7 | 自检报告 | `handoff-self-check.md` 摘要 (8 项齐全 + 矩阵通过) | 非核心, 缺失占位 |
| 8 | 评审与确认 | **4 角色勾选表 (PM/TL/QA/UI)** + 业务方签字区 | 核心, 必填 |

> **3 个核心段** (2 / 4 / 8) 缺失 → 不生成 docx, 提示用户回 hlpm 补齐.
> **5 个非核心段** 缺失 → 该段标"⚠️ 此段文档未生成, 请补走 hlpm 步骤 X", 仍生成 docx, 顶部加黄色警示框.

---

## 输出文件

- 路径: `docs/{ver}/sign-off-package.docx`
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
- 标题 1 (段标题): 14pt 加粗, 黑体
- 标题 2 (子节): 12pt 加粗
- 标题 3 (子子节): 11pt 加粗

### 表格样式
- 4 角色评审表: 边框 1pt 黑色实线, 表头加粗浅灰底色
- 业务方签字: 5 行下划线横线 (项目名 / 版本号 / 业务方签字+日期 / 日期数字格式 / 确认句)

### 图片
- 设计稿截图: 6 英寸宽, 居中, caption 字体 9pt 灰色
- 压缩: > 1MB 时用 Pillow 等比缩放到 1200px 宽

### 修复 4 类已知问题 (必避)
1. **页脚页码空文本** → 用 Word PAGE/NUMPAGES 域, 不要拼字符串
2. **签字区横线无下划线** → `run.font.underline = True`, 不要用纯文本 "_____"
3. **设计稿 0 张图** → `add_picture()` 真实插入, 不能漏
4. **正文字体全默认** → `setup_default_styles()` 显式设 宋体/11pt/1.5 倍

---

## Python 实现骨架 (完整可运行)

下面代码是**完整可运行**的 Python 脚本, 集成上面 4 类问题修复. 直接 `python build_signoff.py v2 "项目名"` 可生成合规 .docx.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hlprd · 融合 v{N} 签字包
读 hlpm 8 项交付物 → 输出 docs/{ver}/sign-off-package.docx
修复: 4 类已知问题
  1. 页脚页码用 Word PAGE / NUMPAGES 域
  2. 签字区横线用下划线而非纯文本
  3. 设计稿截图真实插入
  4. 段落 Normal 字体/字号/行距显式设置
"""
import os, sys, glob
from datetime import date
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# === 修复 1: 页脚页码用 Word 域 (避免空文本) ===
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


# === 修复 2: 签字区下划线 (替代纯文本"_____") ===
def add_underline(paragraph, text, font_size=11):
    run = paragraph.add_run(text)
    run.font.underline = True
    run.font.size = Pt(font_size)
    return run


# === 修复 4: 段落样式统一 ===
def setup_default_styles(doc):
    from docx.shared import Pt
    # Normal 默认样式
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

    # 标题样式
    for level, size in [(1, 14), (2, 12), (3, 11)]:
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


# === 修复 3: 设计稿截图 (压缩 + 居中 + caption) ===
def add_screenshot(doc, png_path, original_html_name):
    if not os.path.exists(png_path):
        return False
    # 压缩: > 1MB 时用 Pillow 等比缩放到 1200px 宽
    if os.path.getsize(png_path) > 1 * 1024 * 1024:
        try:
            from PIL import Image
            img = Image.open(png_path)
            if img.width > 1200:
                ratio = 1200 / img.width
                new_size = (1200, int(img.height * ratio))
                img.thumbnail(new_size)
                compressed = png_path.replace('.png', '-compressed.png')
                img.save(compressed, optimize=True, quality=85)
                png_path = compressed
        except ImportError:
            pass

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(png_path, width=Inches(6))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_run = cap.add_run(f"图: {original_html_name}")
    cap_run.font.size = Pt(9)
    cap_run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    return True


# === 通用 markdown 段落+表格解析器 (修复"表格 0 个"问题) ===
def render_markdown_to_docx(doc, md_content, max_lines=None):
    """解析 markdown 内容, 段落和表格分别渲染到 docx.
    支持: 标题 H1-H4 / 段落 / 引用 / 表格
    """
    lines = md_content.split('\n')
    if max_lines:
        lines = lines[:max_lines]
    i = 0
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            t = doc.add_table(rows=len(table_rows), cols=max(len(r) for r in table_rows))
            t.style = 'Table Grid'
            for r_idx, row in enumerate(table_rows):
                for c_idx in range(len(table_rows[0])):
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
            elif line.startswith('> '):
                p = doc.add_paragraph(line[2:].strip())
                p.runs[0].italic = True
                p.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
            elif line.strip():
                doc.add_paragraph(line)
            i += 1
    flush_table()


# === 主流程 ===
def extract_project_name(prd_path):
    with open(prd_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                return line[2:].strip()
    return "项目"


def build_signoff(ver, project_name=None, signer=None, pm=None, tl=None, qa=None, ui=None):
    """hlprd 主流程: 读 hlpm 8 项交付物, 融合成 docs/{ver}/sign-off-package.docx

    Args:
        ver: 版本号 (e.g. "v1")
        project_name: 项目名 (None 时从 prd.md 标题提取)
        signer: 业务方签字姓名
        pm/tl/qa/ui: 4 角色负责人姓名 (None 时填 "________")
    """
    docs_dir = f"docs/{ver}"
    prd_path = f"{docs_dir}/prd.md"

    # === 前置检查 (按核心/非核心分级) ===
    if not os.path.exists(docs_dir):
        print(f"❌ docs/{ver}/ 不存在, 请先跑 Skill hlpm 跑通 v{ver}")
        return False
    if not os.path.exists(prd_path):
        print(f"❌ docs/{ver}/prd.md 缺失, 核心文件不全, 不生成 .docx")
        return False
    if not os.path.exists(f"{docs_dir}/acceptance-criteria.md"):
        print(f"❌ docs/{ver}/acceptance-criteria.md 缺失, 核心文件不全, 不生成 .docx")
        return False

    project_name = project_name or extract_project_name(prd_path) or "项目"
    pm = pm or "________"
    tl = tl or "________"
    qa = qa or "________"
    ui = ui or "________"
    signer = signer or "________"

    # === 修复 4 类已知问题: 段落样式 + 页脚页码 + 签字区下划线 + 截图 ===
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

    # 页眉: 项目名 + v{ver}
    section.header.paragraphs[0].text = f"{project_name}    v{ver}"
    section.header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 页脚: 第 X 页 / 共 Y 页 (用 Word 域)
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.text = ""
    p.add_run("第 ")
    add_page_field(p)
    p.add_run(" 页 / 共 ")
    add_numpages_field(p)
    p.add_run(" 页")

    # === 第 1 段: 封面 ===
    doc.add_heading(f"{project_name} - 业务方签字包 {ver}", 0)
    doc.add_paragraph(f"文档生成日期: {date.today().isoformat()}")
    doc.add_paragraph(f"文档类型: 业务方签字确认 (基于 hlpm 产品段交付物)")
    doc.add_paragraph()
    doc.add_paragraph(f"本文件包含: PRD 摘要 / 测试用例摘要 / 验收标准 / 设计原型截图 / 一致性矩阵摘要 / 自检报告摘要 / 4 角色评审表 + 业务方签字区.")
    doc.add_paragraph(f"请业务方重点关注: 验收标准 + 设计原型, 其他为辅助参考.")

    # === 第 2 段: PRD 摘要 (核心) ===
    doc.add_heading("一、PRD 摘要", 1)
    with open(prd_path, encoding='utf-8') as f:
        content = f.read()
    # strip dev-not-for-prod 注释 + 提取 H1/H2 部分
    prd_lines = []
    in_code = False
    for line in content.split('\n'):
        s = line.strip()
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s.startswith('<!--'):
            continue
        prd_lines.append(line)
    prd_text = '\n'.join(prd_lines)
    # 用 render_markdown_to_docx 渲染
    render_markdown_to_docx(doc, prd_text, max_lines=200)

    # === 第 3 段: 测试用例摘要 (非核心) ===
    doc.add_heading("二、测试用例摘要", 1)
    tc_path = f"{docs_dir}/test-cases.md"
    if os.path.exists(tc_path):
        with open(tc_path, encoding='utf-8') as f:
            tc_text = f.read()
        render_markdown_to_docx(doc, tc_text, max_lines=80)
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/test-cases.md 缺失, 请补走 hlpm 步骤 8 (测试用例编写)")

    # === 第 4 段: 验收标准 (核心) ===
    doc.add_heading("三、验收标准", 1)
    ac_path = f"{docs_dir}/acceptance-criteria.md"
    if os.path.exists(ac_path):
        with open(ac_path, encoding='utf-8') as f:
            ac_text = f.read()
        render_markdown_to_docx(doc, ac_text, max_lines=120)
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/acceptance-criteria.md 缺失, 请补走 hlpm 步骤")

    # === 第 5 段: 设计原型 (非核心) ===
    doc.add_heading("四、设计原型", 1)
    screenshot_dir = f"{docs_dir}/design"
    if os.path.isdir(screenshot_dir):
        screenshots = sorted(glob.glob(f"{screenshot_dir}/screenshot*.png"))
        if screenshots:
            for png in screenshots:
                base = os.path.basename(png)
                original_html = base.replace('screenshot', '').replace('.png', '.html')
                if original_html == '.html':
                    original_html = 'page.html'
                elif original_html.startswith('-'):
                    original_html = original_html[1:]
                add_screenshot(doc, png, original_html)
        else:
            doc.add_paragraph("⚠️ 暂无截图 — 请确保 hlpm 步骤 6b.5 已生成 design/screenshot*.png")
    else:
        doc.add_paragraph("⚠️ 暂无设计稿目录 — 请确保 hlpm 已生成 docs/{ver}/design/")

    # === 第 6 段: 一致性矩阵摘要 (非核心) ===
    doc.add_heading("五、一致性矩阵摘要", 1)
    cm_path = f"{docs_dir}/consistency-matrix.md"
    if os.path.exists(cm_path):
        with open(cm_path, encoding='utf-8') as f:
            cm_text = f.read()
        render_markdown_to_docx(doc, cm_text, max_lines=100)
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/consistency-matrix.md 缺失")

    # === 第 7 段: 自检报告 (非核心) ===
    doc.add_heading("六、自检报告", 1)
    hs_path = f"{docs_dir}/handoff-self-check.md"
    if os.path.exists(hs_path):
        with open(hs_path, encoding='utf-8') as f:
            hs_text = f.read()
        render_markdown_to_docx(doc, hs_text, max_lines=60)
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/handoff-self-check.md 缺失")

    # === 第 8 段: 评审与确认 (核心) ===
    doc.add_heading("七、评审与确认", 1)
    doc.add_paragraph("以下由各角色负责人评审后签字 / 勾选确认.")

    # 4 角色勾选表
    table = doc.add_table(rows=5, cols=4)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = "角色"
    table.rows[0].cells[1].text = "姓名"
    table.rows[0].cells[2].text = "确认状态"
    table.rows[0].cells[3].text = "意见 / 备注"
    roles_data = [("产品经理 (PM)", pm), ("技术负责人 (TL)", tl),
                  ("测试负责人 (QA)", qa), ("设计负责人 (UI)", ui)]
    for i, (role, name) in enumerate(roles_data, 1):
        table.rows[i].cells[0].text = role
        table.rows[i].cells[1].text = name
        table.rows[i].cells[2].text = "[ ] 确认"
        table.rows[i].cells[3].text = ""
    # 表头加粗
    for cell in table.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True

    # 业务方签字 (修复 1d4ee50 提到的下划线问题)
    doc.add_paragraph()
    heading = doc.add_paragraph()
    heading.add_run("业务方签字").bold = True
    heading.runs[0].font.size = Pt(14)

    p = doc.add_paragraph()
    p.add_run("项目名: ")
    add_underline(p, "____________________")

    p = doc.add_paragraph()
    p.add_run("版本号: ")
    p.add_run("v")
    add_underline(p, "____")

    p = doc.add_paragraph()
    p.add_run("业务方签字: ")
    add_underline(p, "________________________")
    p.add_run("    签字日期: ")
    add_underline(p, "____ 年 ____ 月 ____ 日")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run("(或)  ")
    add_underline(p, "____ - ____ - ____")

    p = doc.add_paragraph()
    p.add_run("业务方对以上需求交付包 (PRD / 测试用例 / 验收标准 / 设计原型) 已确认, 同意进入开发阶段.")
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run(f"如有疑问, 请联系: 产品经理 (见 docs/{ver}/handoff-self-check.md 评审结论).")

    # === 非核心缺失 → 顶部黄色警示框 ===
    missing_non_core = []
    if not os.path.exists(tc_path): missing_non_core.append(('test-cases.md', '测试用例'))
    if not os.path.exists(f"{docs_dir}/non-functional-requirements.md"):
        missing_non_core.append(('non-functional-requirements.md', '非功能需求'))
    if not os.path.exists(hs_path): missing_non_core.append(('handoff-self-check.md', '自检报告'))
    if not os.path.isdir(screenshot_dir) or not screenshots:
        if screenshot_dir not in [m[0] for m in missing_non_core]:
            missing_non_core.append(('design/(含 screenshot*.png)', '设计原型截图'))
    if not os.path.exists(cm_path): missing_non_core.append(('consistency-matrix.md', '一致性矩阵'))

    if missing_non_core:
        # 在最前插入警示段落
        warning = doc.paragraphs[0].insert_paragraph_before("")
        run = warning.add_run("⚠️ 文档不完整 — 本交付包基于 docs/{ver}/ 当前内容生成, 缺失以下非核心文件:")
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0x99, 0x00)
        for fname, cname in missing_non_core:
            p = doc.paragraphs[0].insert_paragraph_before("")
            r = p.add_run(f"  - {cname} ({fname})")
            r.font.color.rgb = RGBColor(0xCC, 0x66, 0x00)
        p = doc.paragraphs[0].insert_paragraph_before("")
        p.add_run("缺失章节显示为「⚠️ 此段文档未生成」占位, 请补走 hlpm 步骤 X 再重新合成.")

    # === 保存 ===
    out_path = f"{docs_dir}/sign-off-package.docx"
    doc.save(out_path)
    print(f"✅ 生成 {out_path}")
    return True


if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    signer = sys.argv[3] if len(sys.argv) > 3 else None
    pm = sys.argv[4] if len(sys.argv) > 4 else None
    tl = sys.argv[5] if len(sys.argv) > 5 else None
    qa = sys.argv[6] if len(sys.argv) > 6 else None
    ui = sys.argv[7] if len(sys.argv) > 7 else None
    build_signoff(ver, project_name, signer, pm, tl, qa, ui)
```

**注意**: 这段代码集成 4 类修复. 拷贝到 `docs/{ver}/build_signoff.py` 即可跑.

---

## 失败处理

### 文档获取失败的分级处理

**核心文件** (2 项, 缺一不可): `prd.md` / `acceptance-criteria.md`
**非核心文件** (5 项, 可缺): `test-cases.md` / `consistency-matrix.md` / `handoff-self-check.md` / `non-functional-requirements.md` / `design/` (含 `screenshot*.png`)

| 情况 | 严重度 | 处理 |
|------|--------|------|
| `docs/{ver}` 目录缺失 | 🔴 致命 | 仅对话警示, **不生成** docx |
| 版本 ver 不存在 (如 `docs/v5/` 不存在) | 🔴 致命 | 仅对话警示, **不生成** docx |
| 核心文件缺失 (PRD / 验收 任一缺失) | 🟡 核心不全 | 仅对话警示 + 列缺哪些, **不生成** docx |
| 非核心文件缺失 (测试/矩阵/自检/非功能/设计 任一缺失) | 🟢 非核心不全 | 仍生成 docx, 缺失段用 "⚠️ 此段未生成" 占位, 顶部加黄色警示框 |
| 文件存在但内容为空 (0 字节或仅标题) | 🟡 视为缺失 | 按"核心/非核心"分级 |
| 全部齐全 | ✅ 正常 | 生成完整 docx |

### 对话提示统一格式

Agent 加载本 skill 后, **第一步**用 Read 工具读所有 8 项交付物, 检测完整性. 如有缺失, 立即向用户报告:

```
⚠️ hlprd 文档获取不完整

版本: vN
状态: [致命/核心不全/非核心不全]

缺失的核心文件 (2 项):
  ❌ docs/vN/prd.md
  ❌ docs/vN/acceptance-criteria.md

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

### 缺失段占位格式 (各非核心章节)

当某非核心章节对应的文件缺失, Agent 不跳过该章节, 而是在 .docx 章节标题下插入占位提示:

```
## 测试用例摘要 (缺源文件)

⚠️ 此段文档未生成 — docs/vN/test-cases.md 缺失或为空.
请补走 hlpm 步骤 8 (测试用例编写) 后, 重新运行 Skill hlprd 合成.
```

### 致命情况不生成 docx (避免误发)

**核心文件缺失时不生成任何 docx**, 原因: 业务方拿到一份"PRD / 验收标准"全空的 docx 会产生严重误解. Agent 引导用户先回 hlpm 补齐再合成, 避免产生不可用的签字包.

### 其他异常

| 失败情形 | 处理 |
|---------|------|
| python-docx 未装 | 告知用户: 「请先 `pip install python-docx pillow`」 |
| `screenshot*.png` 缺失 (但 design/ 存在) | 第 5 段显示 "暂无截图" 占位, 仍生成 .docx |
| .docx 体积 > 10MB | 提示用户: 「考虑压缩截图, 或拆成多页 .docx」 |
| 读取某 .md 抛异常 (编码错误等) | 该段用"⚠️ 文档读取失败"占位, 继续生成其他段 |

---

> **路径规范**: 输出文件 `docs/{ver}/sign-off-package.docx`. 来源 8 项交付物位于 `docs/{ver}/` (来自 hlpm 步骤 11-12).