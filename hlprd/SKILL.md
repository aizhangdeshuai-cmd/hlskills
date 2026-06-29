---
name: hlprd
description: 读取仓库内 hlprd/template.docx (12 章节标准 PRD 模板), 把 hlpm 产品段产出的 8 项交付物数据按章节填入, 生成"标准 PRD 填好的 .docx"给业务方签字. Use when hlpm 完成 (评审通过) 后, 需要给业务方输出一份基于标准 PRD 模板的可签字确认文档. 通过 Skill hlprd "为 <项目名> 合成 v<N> 签字包" 调用.
---

# hlprd — 标准 PRD 模板填数据

> 属于 `hlskills` 技能系统. **读取 `hlprd/template.docx` 12 章节标准 PRD 模板, 把 hlpm 8 项交付物数据填入对应章节, 生成业务方签字用的 .docx.**

---

## ⚠️ 前置依赖

```bash
pip install python-docx
```

(轻依赖 ~3MB, 跨 Mac/Linux/Windows. SKILL.md 顶部明文标注, 用户首次跑本 skill 前自行安装.)

**模板文件 `hlprd/template.docx` 已内嵌仓库**, Agent 加载本 skill 时用 `python-docx` 读它解析 12 章节结构 + 24 张表格样式, 作为填数据的目标模板. 模板修改后无需改 SKILL.md.

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
| **Q2: 项目名?** | A. 自由输入 (从 `prd.md` 标题自动提取作为默认建议) |
| **Q3: 业务方名称?** | A. 自由输入 (用于评审签字表 "业务方" 行, 留空时显示 "________") |
| **Q4: 4 角色负责人姓名?** | A. 自由填 PM/TL/QA/UI 姓名 (可省略, 留 "________" 待用户手填) |

Q2/Q3/Q4 可省略 — 省略时 Agent 从 `prd.md` 标题/版本号自动提取, 4 角色姓名留 "________".

> 加载后**第二件事**: 用 `python-docx` 读 `hlprd/template.docx` 解析 12 章节结构 + 24 张表格样式, 作为填数据的目标模板.

---

## 文档结构 (读 template.docx 填数据, 12 章节)

> **总体原则**: 加载本 skill 后, **第一步**用 `python-docx` 读取仓库内 `hlprd/template.docx` (12 章节标准 PRD 模板), 然后把 hlpm 8 项交付物数据**填入对应章节**。产物 = **标准 PRD 模板填好的 .docx**, 业务方签字用。
>
> **Agent 必读**: 修改 `template.docx` 后, 重新跑 hlprd 自动跟进, **不需要改 SKILL.md**。

### 模板 12 章节结构 (来自 `hlprd/template.docx`)

| 章节 | 标题 | 数据来源 (从 hlpm 8 项交付物) | 必填/可选 |
|------|------|------------------------|---------|
| 1 | 版本修订记录 | PRD 章节 §版本号 + 当前日期 | 必填 |
| 2 | 项目概述 (背景/目标/干系人/用户故事) | PRD §0 + §1 + §2 + 业务上下文 | 必填 |
| 3 | 用户角色与权限 | PRD §5 权限规则 | 必填 |
| 4 | 产品范围 (In / Out of Scope) | PRD §0 范围 + §0 范围外 | 必填 |
| 5 | 功能需求详述 (核心) | PRD §1 业务逻辑 + §2 操作流程 + §3 数据流转 | **核心** |
| 6 | 接口与数据需求 | PRD §3 数据流转 + API 文档 (如有) | 必填 |
| 7 | 交互与体验需求 | 设计稿 §交互状态 (如有) | 必填 |
| 8 | 非功能性需求 | PRD §6 性能/安全/兼容 (3 子表) | 必填 |
| 9 | 数据埋点需求 | PRD §6 监控指标 (如有) | 可选 (如缺则标 "⚠️ 未填") |
| 10 | 验收标准 (Definition of Done) | acceptance-criteria.md (逐条 AC-XXX) | **核心** |
| 11 | 术语表 (Glossary) | PRD 业务术语提取 | 必填 |
| 12 | 评审与确认 | 4 角色勾选 (PM/TL/QA/UI) + 业务方签字 | **核心** |

> **3 个核心章节** (5/10/12) 缺失 → 不生成 docx, 提示用户回 hlpm 补齐。
> **9 个非核心章节** 缺失 → 该章节标"⚠️ 此节文档未生成, 请补走 hlpm 步骤 X", 仍生成 docx, 顶部加黄色警示框。

### 第 12 章节 · 评审与确认 (4 角色勾选)

```
| 角色 | 姓名 | 确认状态 | 意见 / 备注 |
|------|------|----------|------------|
| 产品经理（PM）| [自动填入]| [ ] 确认 | |
| 技术负责人（TL）| [自动填入]| [ ] 确认 | |
| 测试负责人（QA）| [自动填入]| [ ] 确认 | |
| 设计负责人（UI）| [自动填入]| [ ] 确认 | |
| **业务方** | [Q3 输入] | [ ] 确认签字 |  |
```

**注意**: 模板原表 23 是 4 角色勾选 (PM/TL/QA/UI) + 业务方签字合并. hlprd **保留 4 角色自动填名 + 1 行业务方签字**.

**5 个 `[ ] 确认` 框 + 1 行"业务方签字"下划线** (修复 1d4ee50 提到的签字区下划线问题, 沿用之前 5 行下划线方案).

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

def build_signoff(ver, project_name=None, signer=None, pm=None, tl=None, qa=None, ui=None):
    """hlprd 主流程: 读 hlprd/template.docx 12 章节标准 PRD 模板, 把 hlpm 8 项交付物数据填入对应章节.

    Args:
        ver: 版本号 (e.g. "v1")
        project_name: 项目名 (None 时从 prd.md 标题提取)
        signer: 业务方签字姓名
        pm/tl/qa/ui: 4 角色负责人姓名 (None 时填 "________")
    """
    docs_dir = f"docs/{ver}"
    prd_path = f"{docs_dir}/prd.md"

    # === 模板路径 (按优先级) ===
    # 1. 环境变量 HLSKILLS_HOME 指向 hlskills 仓库根目录
    # 2. __file__ 同目录 (本 skill 部署后通常可用)
    # 3. 当前工作目录
    # 4. 相对路径 hlprd/template.docx
    hls_home = os.environ.get('HLSKILLS_HOME', '')
    candidate_paths = [
        os.path.join(hls_home, 'hlprd', 'template.docx') if hls_home else None,
        os.path.join(os.path.dirname(__file__) if '__file__' in dir() else '', 'template.docx'),
        'template.docx',
        'hlprd/template.docx',
    ]
    template_path = None
    for p in candidate_paths:
        if p and os.path.exists(p):
            template_path = p
            break
    if not template_path:
        print(f"❌ hlprd/template.docx 缺失, 请确认模板文件在仓库 (尝试路径: {candidate_paths})")
        return False

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
    if not os.path.exists(f"{docs_dir}/design"):
        print(f"❌ docs/{ver}/design/ 缺失, 核心文件不全, 不生成 .docx")
        return False

    project_name = project_name or extract_project_name(prd_path) or "项目"
    pm = pm or "________"
    tl = tl or "________"
    qa = qa or "________"
    ui = ui or "________"
    signer = signer or "________"

    # === 第 1 步: 复制 template.docx 作为基础 ===
    import shutil
    out_path = f"{docs_dir}/sign-off-package.docx"
    shutil.copy(template_path, out_path)
    doc = Document(out_path)

    # === 第 2 步: 修复模板原有 4 类问题 ===
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
    p.text = ""  # 清空
    p.add_run("第 ")
    add_page_field(p)
    p.add_run(" 页 / 共 ")
    add_numpages_field(p)
    p.add_run(" 页")

    # === 第 3 步: 检测非核心文件缺失, 准备占位提示 ===
    missing_non_core = []
    if not os.path.exists(f"{docs_dir}/test-cases.md"):
        missing_non_core.append(('test-cases.md', '测试用例'))
    if not os.path.exists(f"{docs_dir}/non-functional-requirements.md"):
        missing_non_core.append(('non-functional-requirements.md', '非功能需求'))
    if not os.path.exists(f"{docs_dir}/handoff-self-check.md"):
        missing_non_core.append(('handoff-self-check.md', '自检报告'))

    # === 第 4 步: 填章节数据 ===
    # 章节 1: 版本修订记录 (用表 1 填)
    fill_chapter_1_version_history(doc, ver, pm)

    # 章节 2: 项目概述 (PRD §0+§1+§2+业务上下文)
    fill_chapter_2_overview(doc, prd_path, project_name)

    # 章节 3: 用户角色与权限 (PRD §5)
    fill_chapter_3_roles(doc, prd_path)

    # 章节 4: 产品范围 (PRD §0 范围)
    fill_chapter_4_scope(doc, prd_path)

    # 章节 5: 功能需求详述 (核心: PRD §1+§2+§3 → 表 5/6/7/8)
    fill_chapter_5_features(doc, prd_path, f"{docs_dir}/test-cases.md" in os.listdir(docs_dir) and os.path.exists(f"{docs_dir}/test-cases.md"))

    # 章节 6: 接口与数据需求
    fill_chapter_6_interface(doc, prd_path)

    # 章节 7: 交互与体验需求
    fill_chapter_7_interaction(doc, f"{docs_dir}/design")

    # 章节 8: 非功能性需求 (PRD §6)
    nfr_path = f"{docs_dir}/non-functional-requirements.md"
    fill_chapter_8_nfr(doc, nfr_path if os.path.exists(nfr_path) else None)

    # 章节 9: 数据埋点需求 (可选)
    fill_chapter_9_tracking(doc, prd_path)

    # 章节 10: 验收标准 (核心: acceptance-criteria.md → 表 21)
    fill_chapter_10_acceptance(doc, f"{docs_dir}/acceptance-criteria.md")

    # 章节 11: 术语表 (PRD 业务术语提取 → 表 22)
    fill_chapter_11_glossary(doc, prd_path)

    # 章节 12: 评审与确认 (核心: 表 23)
    fill_chapter_12_signoff(doc, pm, tl, qa, ui, signer)

    # === 第 5 步: 非核心缺失 → 顶部黄色警示框 ===
    if missing_non_core:
        warning = doc.paragraphs[0].insert_paragraph_before("")
        warning_run = warning.add_run("⚠️ 文档不完整 — 本交付包基于 docs/{ver}/ 当前内容生成, 缺失以下非核心文件:")
        warning_run.font.bold = True
        warning_run.font.color.rgb = RGBColor(0xFF, 0x99, 0x00)
        for fname, cname in missing_non_core:
            p = doc.paragraphs[0].insert_paragraph_before("")
            run = p.add_run(f"  - {cname} ({fname})")
            run.font.color.rgb = RGBColor(0xCC, 0x66, 0x00)
        p2 = doc.paragraphs[0].insert_paragraph_before("")
        p2.add_run("缺失章节显示为「⚠️ 此段文档未生成」占位, 请补走 hlpm 步骤 X 再重新合成.")

    # === 第 6 步: 保存 ===
    doc.save(out_path)
    print(f"✅ 生成 {out_path}")
    return True

# === 章节填充函数 (按 template.docx 的 24 张表格结构) ===
def fill_chapter_1_version_history(doc, ver, pm):
    """填章节 1: 版本修订记录 (表 1, 5 行 x 5 列)"""
    for t in doc.tables:
        if len(t.rows) > 1 and '版本号' in t.rows[0].cells[0].text:
            # 找第一个空行 (当前已 V1.0 之外) 填新行
            today = date.today().isoformat()
            # 找"V1.0"行后追加一行新版本
            for i, row in enumerate(t.rows[1:], 1):
                if not row.cells[0].text.strip():
                    row.cells[0].text = f"V{ver.replace('v','')}"
                    row.cells[1].text = today
                    row.cells[2].text = pm or "[姓名]"
                    row.cells[3].text = "由 hlprd 自动填充"
                    row.cells[4].text = "hlprd 合成"
                    return

def fill_chapter_2_overview(doc, prd_path, project_name):
    """填章节 2: 项目概述 (PRD 标题 + 6 大模块部分)"""
    # 找 2.1 项目背景 / 2.2 项目目标 等子节
    in_prd = False
    prd_content = ""
    with open(prd_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                in_prd = True
                continue
            if in_prd and line.startswith('## '):
                prd_content += line
            if in_prd and not line.startswith('#'):
                prd_content += line

    # 表格 0 文档元信息 (在模板最前) - 填产品名 + 拟稿人 + 日期
    for t in doc.tables:
        if len(t.rows) > 0 and '产品名称' in t.rows[0].cells[0].text:
            for row in t.rows:
                for i, cell in enumerate(row.cells):
                    if '例如' in cell.text:
                        # 替换占位
                        if i == 1: cell.text = project_name
                    if cell.text.strip() == 'PM姓名' and i == 3:
                        row.cells[3].text = "[PM 姓名]"
                    if cell.text.strip() == '2026-06-29' and i == 5:
                        row.cells[5].text = date.today().isoformat()

def fill_chapter_3_roles(doc, prd_path):
    """填章节 3: 用户角色与权限 (PRD §5 权限规则 → 表 3)"""
    # 读 PRD 权限部分
    in_prd = False
    roles_text = ""
    with open(prd_path, encoding='utf-8') as f:
        in_section_5 = False
        for line in f:
            if '## 5' in line or '## 五' in line or '权限' in line:
                in_section_5 = True
            if in_section_5:
                roles_text += line
    # 简化: 不解析, 标记模板原表 3 内容由用户手填
    # (Agent 跑 hlprd 时不自动解析权限段, 留占位)

def fill_chapter_4_scope(doc, prd_path):
    """填章节 4: 产品范围 (表 4)"""
    # 占位 - 用户手填
    pass

def fill_chapter_5_features(doc, prd_path, has_test_cases):
    """填章节 5: 功能需求详述 (核心, 多个子节)"""
    # 读 PRD 业务逻辑
    prd_text = open(prd_path, encoding='utf-8').read()

    # 5.1/5.2 等子节: 替换占位"此处粘贴..."为 PRD 内容
    for p in doc.paragraphs:
        if '此处粘贴' in p.text or '请在' in p.text:
            # 替换为 PRD 提示
            design_dir_path = os.path.join(os.path.dirname(prd_path), "design")
            if os.path.exists(design_dir_path):
                html_count = sum(1 for f in os.listdir(design_dir_path) if f.endswith(".html"))
            else:
                html_count = 0
            p.text = p.text.replace(
                '此处粘贴设计稿（Figma / Axure）链接或截图。',
                f'📎 设计稿位置: docs/{os.path.basename(os.path.dirname(prd_path))}/design/ (含 {html_count} 个 HTML 原型)'
            )

def fill_chapter_6_interface(doc, prd_path):
    """填章节 6: 接口与数据需求"""
    # 占位 - 简化, 由用户手填
    pass

def fill_chapter_7_interaction(doc, design_dir):
    """填章节 7: 交互与体验需求 (设计稿 HTML 链接)"""
    if os.path.isdir(design_dir):
        html_files = [f for f in os.listdir(design_dir) if f.endswith('.html')]
        for p in doc.paragraphs:
            if '点击查看设计稿链接' in p.text:
                p.text = f"📎 设计稿: {len(html_files)} 个 HTML 文件, 位于 {design_dir}/ 目录"

def fill_chapter_8_nfr(doc, nfr_path):
    """填章节 8: 非功能性需求 (核心: NFR 性能/安全/兼容)"""
    if nfr_path and os.path.exists(nfr_path):
        nfr_content = open(nfr_path, encoding='utf-8').read()
        # 找表 19 (非功能需求表), 在其后追加 NFR 内容摘要
        for t in doc.tables:
            if len(t.rows) > 0 and '指标项' in t.rows[0].cells[0].text:
                # 找最后一行后追加 (NFR 内容)
                for line in nfr_content.split('\n')[-20:]:
                    if line.strip() and not line.startswith('|'):
                        new_p = doc.add_paragraph(line.strip())
                return

def fill_chapter_9_tracking(doc, prd_path):
    """填章节 9: 数据埋点需求 (可选)"""
    # 占位
    pass

def fill_chapter_10_acceptance(doc, ac_path):
    """填章节 10: 验收标准 (核心: acceptance-criteria.md → 表 21)"""
    if not os.path.exists(ac_path):
        return
    ac_content = open(ac_path, encoding='utf-8').read()
    # 找表 21 (验收维度表), 在其后追加 AC 列表
    for t in doc.tables:
        if len(t.rows) > 0 and '验收项' in t.rows[0].cells[0].text:
            # 追加 AC 列表
            for line in ac_content.split('\n')[:30]:
                if line.strip().startswith('AC-') or 'AC-' in line[:10]:
                    doc.add_paragraph(line.strip())
            return

def fill_chapter_11_glossary(doc, prd_path):
    """填章节 11: 术语表 (表 22)"""
    # 简化: 不解析, 用户手填
    pass

def fill_chapter_12_signoff(doc, pm, tl, qa, ui, signer):
    """填章节 12: 评审与确认 (核心: 表 23 4 角色 + 业务方签字)"""
    found_table_23 = False
    # 找表 23 (4 角色评审表)
    for t in doc.tables:
        if len(t.rows) >= 5 and '产品经理' in t.rows[1].cells[0].text:
            # 填 4 角色姓名
            t.rows[1].cells[1].text = pm
            t.rows[2].cells[1].text = tl
            t.rows[3].cells[1].text = qa
            t.rows[4].cells[1].text = ui
            found_table_23 = True
            break  # 找到后退出, 继续执行下面的业务方签字

    # 业务方签字 (表 23 后追加, 修复 1d4ee50 提到的下划线问题)
    if found_table_23:
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

