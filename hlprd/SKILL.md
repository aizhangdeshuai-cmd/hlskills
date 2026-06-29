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

### ⚠️ 已知 4 类格式问题（必避）

按用户实际使用 hlprd 跑出的 `sign-off-package.docx` 反馈, 4 类问题必须避免:

1. **页脚页码是空文本** ("第 页 / 共 页") — 必须用 Word 的 PAGE / NUMPAGES 域, 不要拼字符串
2. **签字区横线无下划线** ("_____" 打印后看不出) — 必须用 `run.font.underline = True`, 不要用纯文本
3. **设计稿截图段 0 张图** (核心内容缺失) — `add_picture()` 必须真实插入, 不能漏
4. **正文字体/字号/行距全默认** (与规范不符) — `Normal` 段落必须显式设 字体=宋体, 字号=11pt, 行距=1.5 倍

下面 4 段代码片段是修复参考. 完整实现见 "Python 实现骨架" 段.

### ⚠️ 页脚页码域 (修复"第 页 / 共 页"空文本)

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_page_number_field(paragraph):
    """插入 Word PAGE 域, 自动渲染为当前页码"""
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

def add_total_pages_field(paragraph):
    """插入 NUMPAGES 域, 自动渲染为总页数"""
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

# 完整页脚
footer = doc.sections[0].footer
p = footer.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("第 ")
add_page_number_field(p)
p.add_run(" 页 / 共 ")
add_total_pages_field(p)
p.add_run(" 页")
```

### ⚠️ 签字区下划线 (修复"_____"纯文本问题)

```python
def add_underline(paragraph, text):
    """添加带下划线的文字 (替代纯文本横线)"""
    run = paragraph.add_run(text)
    run.font.underline = True  # WD_UNDERLINE.SINGLE
    run.font.size = Pt(11)
    return run

# 完整签字区 (替代之前 6 段空白 + "_____"拼接)
doc.add_heading("七、业务方签字", 1)

p = doc.add_paragraph()
p.add_run("项目名: ")
add_underline(p, "____________________")
doc.add_paragraph()

p = doc.add_paragraph()
p.add_run("版本号: ")
p.add_run("v")
add_underline(p, "____")
doc.add_paragraph()

p = doc.add_paragraph()
p.add_run("业务方签字: ")
add_underline(p, "________________________")
p.add_run("    签字日期: ")
add_underline(p, "____ 年 ____ 月 ____ 日")
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
p.add_run("(或)  ")
add_underline(p, "____ - ____ - ____")
doc.add_paragraph()

p = doc.add_paragraph()
p.add_run("业务方对以上需求交付包 (PRD / 测试用例 / 验收标准 / 设计原型) 已确认, 同意进入开发阶段.")
```

### ⚠️ 设计稿截图插入 (修复"总图片数 0"问题)

```python
from docx.oxml.ns import qn
import os
from PIL import Image  # pip install pillow (python-docx 依赖)

def add_screenshot(doc, png_path, original_html_name):
    """插入设计稿截图 + caption"""
    # 检查截图文件大小 (< 1MB, 否则压缩)
    if os.path.getsize(png_path) > 1 * 1024 * 1024:
        img = Image.open(png_path)
        # 等比缩放到宽度 1200 像素
        if img.width > 1200:
            ratio = 1200 / img.width
            new_size = (1200, int(img.height * ratio))
            img.thumbnail(new_size)
            compressed_path = png_path.replace('.png', '-compressed.png')
            img.save(compressed_path, optimize=True, quality=85)
            png_path = compressed_path

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(png_path, width=Inches(6))

    # caption
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_run = cap.add_run(f"图: {original_html_name}")
    cap_run.font.size = Pt(9)
    cap_run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

# 批量插入 docs/vN/design/ 所有 screenshot*.png
screenshot_dir = f"docs/{ver}/design"
if os.path.isdir(screenshot_dir):
    screenshots = sorted(glob.glob(f"{screenshot_dir}/screenshot*.png"))
    for i, png in enumerate(screenshots, 1):
        # 从 PNG 文件名映射回原 HTML 文件名
        original_html = os.path.basename(png).replace('screenshot', '').replace('.png', '.html')
        if original_html == '.html':  # 单个文件
            original_html = 'page.html'
        add_screenshot(doc, png, original_html)
```

### ⚠️ 段落样式统一 (修复"字体=None 字号=None"问题)

```python
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_paragraph_style(p, font_name='宋体', font_size=11, bold=False, line_spacing=1.5):
    """统一段落样式: 字体 + 字号 + 粗体 + 行距"""
    p.style.font.name = font_name
    p.style.font.size = Pt(font_size)
    p.style.font.bold = bold
    # 中文字体设置 (Word 需要 rFonts/eastAsia)
    r = p.style.element.rPr if p.style.element.rPr is not None else OxmlElement('w:rPr')
    rFonts = r.find(qn('w:rFonts')) if r.find(qn('w:rFonts')) is not None else OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), font_name)
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    if r.find(qn('w:rFonts')) is None:
        r.append(rFonts)
    p.style.element.get_or_add_rPr()
    # 行距
    p.paragraph_format.line_spacing = line_spacing

# 文档默认 Normal 样式
from docx.styles.style import _ParagraphStyle
normal = doc.styles['Normal']
normal.font.name = '宋体'
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
normal.paragraph_format.line_spacing = 1.5

# 标题样式
for level, size in [(1, 16), (2, 14), (3, 12)]:
    style = doc.styles[f'Heading {level}']
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.name = '宋体'
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
```

### 页面设置 (基础)
- 纸张: A4 (210×297mm)
- 边距: 上 2.5cm / 下 2.5cm / 左 2.5cm / 右 2.5cm

### 页眉
- 左 "项目名" + 右 "v{ver}" (字体 9pt, 宋体)

### 表格样式
- 业务规则覆盖矩阵 / 状态机覆盖矩阵 / 权限覆盖矩阵 / 自检报告表
- 边框: 1pt 黑色实线
- 表头: 加粗 + 浅灰底色 (RGB F2F2F2)

### 图片
- 设计稿截图: 6 英寸宽, 居中
- 限制: 单张图最大 6 英寸, 总文档 < 10MB (避免 .docx 体积爆炸)
- 压缩: 截图 > 1MB 时用 Pillow 等比缩放到 1200px 宽再插入

### 标题层级
- **不要硬写 "1." "2." "3."** — 用 Heading 1/2/3 样式, Word 自动编号
- 实际: 一级用 H1, 二级用 H2, 三级用 H3, 4 级以下用普通加粗段 (别滥用 H4)

---

## Python 实现骨架 (完整可运行)

下面代码是**完整可运行**的 Python 脚本, 集成上面 4 类问题修复. 直接 `python build_signoff.py v2 "项目名"` 可生成合规 .docx.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hlprd · 合成 v{N} 签字包
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
            pass  # 无 Pillow 也能跑, 只不压缩

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

# === 主流程 ===
def extract_project_name(prd_path):
    with open(prd_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                import re
                return re.sub(r"^PRD\s*[·•]\s*", "", line[2:].strip())
    return "项目"

def build_signoff(ver, project_name=None, signer=None):
    docs_dir = f"docs/{ver}"
    prd_path = f"{docs_dir}/prd.md"
    if not os.path.exists(docs_dir):
        print(f"❌ docs/{ver}/ 不存在, 请先跑 Skill hlpm 跑通 v{ver}")
        return False
    if not os.path.exists(prd_path):
        print(f"❌ docs/{ver}/prd.md 缺失, 核心文件不全, 不生成 .docx")
        return False

    project_name = project_name or extract_project_name(prd_path) or "项目"
    signer = signer or "________"

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

    # 页脚: 第 X 页 / 共 Y 页 (用域)
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("第 ")
    add_page_field(p)
    p.add_run(" 页 / 共 ")
    add_numpages_field(p)
    p.add_run(" 页")

    # 第 1 段: 封面
    doc.add_heading(f"{project_name} - 需求交付包 {ver}", 0)
    doc.add_paragraph(f"文档生成日期: {date.today().isoformat()}")
    doc.add_paragraph(f"文档类型: 业务方签字确认")
    doc.add_paragraph()
    doc.add_paragraph(f"本文件包含: PRD 全文 / 测试用例摘要 / 验收标准 / 设计原型 / 一致性矩阵 / 自检报告 / 业务方签字区.")
    doc.add_paragraph(f"请业务方重点关注: 测试用例主流程 + 验收标准 + 设计原型, 其他为辅助参考.")

    # 第 2 段: PRD 全文 (strip dev-not-for-prod 注释 + dev-only HTML/JSON)
    doc.add_heading("一、PRD 全文", 1)
    in_code_block = False
    with open(prd_path, encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            if stripped.startswith('<!--'):
                continue
            if stripped.startswith('# '):
                doc.add_heading(line[2:].strip(), 2)
            elif stripped.startswith('## '):
                doc.add_heading(line[3:].strip(), 3)
            elif stripped.startswith('### '):
                doc.add_heading(line[4:].strip(), 4)
            elif stripped.startswith('#### '):
                doc.add_paragraph(line[5:].strip()).runs[0].font.bold = True
            elif stripped:
                doc.add_paragraph(line.rstrip())

    # 第 3 段: 测试用例摘要 (top-20)
    doc.add_heading("二、测试用例摘要", 1)
    tc_path = f"{docs_dir}/test-cases.md"
    if os.path.exists(tc_path):
        # 简化: 全文嵌入 + 优先标记
        with open(tc_path, encoding='utf-8') as f:
            content = f.read()
        for line in content.split('\n')[:100]:
            doc.add_paragraph(line)
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/test-cases.md 缺失")

    # 第 4 段: 验收标准 (全文)
    doc.add_heading("三、验收标准", 1)
    ac_path = f"{docs_dir}/acceptance-criteria.md"
    if os.path.exists(ac_path):
        with open(ac_path, encoding='utf-8') as f:
            for line in f:
                doc.add_paragraph(line.rstrip())
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/acceptance-criteria.md 缺失")

    # 第 5 段: 设计原型 (嵌入截图, 修复"0 张图"问题)
    doc.add_heading("四、设计原型", 1)
    screenshot_dir = f"{docs_dir}/design"
    if os.path.isdir(screenshot_dir):
        screenshots = sorted(glob.glob(f"{screenshot_dir}/screenshot*.png"))
        if screenshots:
            for png in screenshots:
                # 从 PNG 文件名映射回原 HTML 文件名
                base = os.path.basename(png)
                # screenshot.png / screenshot-1.png / screenshot-page.html.png
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

    # 第 6 段: 一致性矩阵摘要
    doc.add_heading("五、一致性矩阵摘要", 1)
    cm_path = f"{docs_dir}/consistency-matrix.md"
    if os.path.exists(cm_path):
        with open(cm_path, encoding='utf-8') as f:
            content = f.read()
        for line in content.split('\n')[:80]:
            doc.add_paragraph(line)
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/consistency-matrix.md 缺失")

    # 第 7 段: 自检报告
    doc.add_heading("六、自检报告", 1)
    hs_path = f"{docs_dir}/handoff-self-check.md"
    if os.path.exists(hs_path):
        with open(hs_path, encoding='utf-8') as f:
            content = f.read()
        for line in content.split('\n')[:30]:
            doc.add_paragraph(line)
    else:
        doc.add_paragraph("⚠️ 此段文档未生成 — docs/{ver}/handoff-self-check.md 缺失")

    # 第 8 段: 签字区 (修复"_____"无下划线问题)
    doc.add_heading("七、业务方签字", 1)

    p = doc.add_paragraph()
    p.add_run("项目名: ")
    add_underline(p, "____________________")
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.add_run("版本号: ")
    p.add_run("v")
    add_underline(p, "____")
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.add_run("业务方签字: ")
    add_underline(p, "________________________")
    p.add_run("    签字日期: ")
    add_underline(p, "____ 年 ____ 月 ____ 日")
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run("(或)  ")
    add_underline(p, "____ - ____ - ____")
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.add_run("业务方对以上需求交付包 (PRD / 测试用例 / 验收标准 / 设计原型) 已确认, 同意进入开发阶段.")
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run(f"如有疑问, 请联系: 产品经理 (见 docs/{ver}/handoff-self-check.md 评审结论).")

    # 保存
    out_path = f"{docs_dir}/sign-off-package.docx"
    doc.save(out_path)
    print(f"✅ 生成 {out_path}")
    return True

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    build_signoff(ver, project_name)
```

**注意**: 这段代码集成上面 4 类修复. 拷贝到 `docs/{ver}/build_signoff.py` 即可跑.

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

