---
name: hlbrowse
description: 浏览器实时交互QA技能，完整集成 gstack 浏览器引擎提供70+浏览器命令（导航/交互/快照/截图/视觉对比/Cookie导入）。支持交互式QA和仅报告QA两种模式。Use when 需要在浏览器中实时探索页面、做交互式QA测试、截图对比、Cookie导入。通过 /hlbrowse 调用。
---

# 浏览器实时交互 QA

> 属于 `hlskills` 技能系统。基于 gstack browse 编译二进制，提供比纯 Playwright 脚本更强的实时交互能力。

---

## 依赖检测

**第一步：检测 gstack browse 是否可用。**

```bash
# 优先：gstack 已通过 Skill 体系安装
B=$(find ~/.claude/skills/gstack/browse/dist -name "browse" -type f 2>/dev/null | head -1)
# Fallback: 旧版安装路径
[ -z "$B" ] && B=$(find ~/.gstack -name "browse" -type f 2>/dev/null | head -1)
[ -z "$B" ] && B=$(find ~/.gstack-repo -name "browse" -type f 2>/dev/null | head -1)
[ -z "$B" ] && B=$(command -v browse 2>/dev/null)

if [ -n "$B" ]; then
  echo "✅ gstack browse 已安装: $B"
else
  echo "❌ gstack browse 未安装，请运行: /gstack-upgrade 或 /hlsetup"
fi
```

### 如果已安装

直接进入下方"命令参考"使用。

### 如果未安装

gstack browse 未安装时，通过以下任一方式安装：

1. **Skill 安装（推荐）**：运行 `/hlsetup`
2. **gstack 技能**：在终端执行 `Skill gstack` 加载 gstack 技能体系
3. **手动安装（**仅当方式 1/2 不可用时**）**:克隆并固定到已知 commit,避免供应链攻击面。
   ```bash
   # 1. 克隆
   git clone https://github.com/garrytan/gstack ~/.gstack-repo
   cd ~/.gstack-repo
   # 2. 固定到已知稳定 commit(查 https://github.com/garrytan/gstack/releases 取最新稳定 SHA)
   git checkout <known-stable-commit-sha>
   # 3. (可选但推荐)验证 SHA256
   sha256sum setup | grep <expected-hash-from-release-notes>
   # 4. 执行 setup
   ./setup
   ```

---

## 快速开始

```bash
B=~/.claude/skills/gstack/browse/dist/browse   # gstack Skill 安装路径

$B goto https://example.com            # 打开页面
$B snapshot -i                         # 获取交互元素引用（@e1, @e2...）
$B click @e3                           # 点击引用元素
$B fill @e2 "hello"                    # 填充输入框
$B screenshot /tmp/page.png            # 截图
$B text                                # 获取页面纯文本
```

---

## 命令参考

### 导航
| 命令 | 说明 |
|------|------|
| `goto <url>` | 导航到 URL |
| `load-html <file>` | 加载本地 HTML |
| `back` / `forward` / `reload` | 标准导航 |
| `url` | 当前页面 URL |
| `wait <sel\|--networkidle\|--load>` | 等待元素/网络空闲/页面加载 |

### 读取/提取
| 命令 | 说明 |
|------|------|
| `text [sel]` | 页面纯文本 |
| `html [sel]` | innerHTML 或完整 HTML |
| `links` | 所有链接 text→href |
| `forms` | 表单字段 JSON |
| `accessibility` | 完整 ARIA 无障碍树 |
| `media [--images\|--videos\|--audio]` | 媒体元素及 URL |
| `data [--jsonld\|--og\|--meta\|--twitter]` | 结构化数据 |

### 交互
| 命令 | 说明 |
|------|------|
| `click <sel\|@ref>` | 点击元素 |
| `fill <sel> <val>` | 填充输入框 |
| `select <sel> <val>` | 选择下拉框 |
| `hover <sel>` | 悬停元素 |
| `type <text>` | 键盘输入到聚焦元素 |
| `press <key>` | 按下键盘按键（Enter, Tab, Escape, Arrow* 等） |
| `scroll [sel\|@ref]` | 滚动元素到可见区域 |
| `upload <sel> <file>` | 上传文件 |
| `dialog-accept [text]` | 接受弹窗 |
| `dialog-dismiss` | 关闭弹窗 |

### 快照（核心）
| 命令 | 说明 |
|------|------|
| `snapshot` | 完整页面无障碍树 |
| `snapshot -i` | 仅交互元素，配 @e 引用 |
| `snapshot -c` | 紧凑模式（无空结构节点） |
| `snapshot -s <sel>` | 限定到 CSS 选择器范围 |
| `snapshot -D` | 与上次快照的统一差异 |
| `snapshot -a -o <path>` | 注释截图（@e 标签叠加在元素上） |
| `snapshot -C` | 扫描无障碍树遗漏的可点击元素（@c 引用） |

### 视觉
| 命令 | 说明 |
|------|------|
| `screenshot [path]` | 全页截图 |
| `screenshot --viewport [path]` | 视口截图 |
| `screenshot @e3 [path]` | 元素截图 |
| `screenshot --base64` | Base64 截图 |
| `responsive [prefix]` | 三屏截图（移动 375×812 / 平板 768×1024 / 桌面 1280×720） |
| `diff <url1> <url2>` | 两个 URL 的文本差异 |
| `pdf [path] [--format]` | 生成 PDF |
| `prettyscreenshot [--cleanup] [--scroll-to] [--hide] [path]` | 清理后截图 |

### 检查
| 命令 | 说明 |
|------|------|
| `js <expr>` | 执行 JS 表达式 |
| `css <sel> <prop>` | 获取计算后的 CSS 值 |
| `attrs <sel\|@ref>` | 元素属性 JSON |
| `console [--errors]` | 控制台消息 |
| `network` | 网络请求 |
| `perf` | 页面加载性能 |
| `ux-audit` | 页面结构分析 |
| `inspect [sel] [--all]` | CDP 深度 CSS 检查 |

### Cookie 与状态
| 命令 | 说明 |
|------|------|
| `cookies` | 所有 Cookie JSON |
| `cookie <name>=<value>` | 设置 Cookie |
| `cookie-import <json>` | 从 JSON 文件导入 Cookie |
| `cookie-import-browser [--domain d]` | 从真实浏览器导入 Cookie |
| `storage` | localStorage + sessionStorage |

### 标签页
| 命令 | 说明 |
|------|------|
| `tabs` | 列出所有标签页 |
| `tab <id>` | 切换标签页 |
| `newtab [url]` | 打开新标签页 |
| `closetab [id]` | 关闭标签页 |
| `tab-each <cmd>` | 在每个标签页执行命令 |

### 服务器
| 命令 | 说明 |
|------|------|
| `status` | 守护进程状态 |
| `stop` | 停止守护进程 |
| `restart` | 重启守护进程 |
| `connect` | 切换到 headed 模式（可见窗口） |
| `disconnect` | 切回 headless 模式 |

---

## QA 工作流

### 交互式探索模式

```
1. $B goto <目标URL>
2. $B snapshot -i            → 获取 @e 引用
3. $B click @eN              → 交互式点击
4. $B snapshot -D            → 验证操作效果
5. $B screenshot ./before/   → 操作前截图
6. $B screenshot ./after/    → 操作后截图
```

### 响应式检查

```bash
$B responsive myapp          # 一键生成三屏截图
# → myapp-mobile-375x812.png
# → myapp-tablet-768x1024.png
# → myapp-desktop-1280x720.png
```

### Cookie 导入流程

```bash
# 方式1：从 JSON 导入
$B cookie-import /tmp/session.json

# 方式2：从真实浏览器导入
$B cookie-import-browser          # 交互式选择浏览器
$B cookie-import-browser --domain myapp.com  # 直接指定域名

# 验证导入
$B cookies | grep myapp
```

---

## QA 模式

hlbrowse 支持两种 QA 模式：

### 交互式 QA（默认）

边探索边修复，适合开发过程中的实时验证：

```
1. $B goto <目标URL>
2. $B snapshot -i            → 获取 @e 引用
3. $B click @eN              → 交互式点击
4. $B snapshot -D            → 验证操作效果
5. $B console                → 检查 JS 错误
6. 发现问题 → 修复 → 重新验证
```

### 仅报告 QA（对应 gstack /qa-only）

只产出结构化 Bug 报告，不修复任何问题。适合独立测试人员、用户验收测试：

```bash
# 1. 系统探索页面
$B goto <目标URL>
$B responsive /tmp/qa-layout      # 三屏截图

# 2. 逐功能交互验证
$B snapshot -i                    # 基准快照
$B click @e3                      # 操作
$B snapshot -D                    # 差异对比
$B snapshot -a -o /tmp/qa-evidence.png  # 注释截图证据
$B console --errors               # 收集 JS 错误

# 3. 产出结构化报告
# 报告格式（保存到 docs/qa/）：
# - 问题标题 + 严重性（Critical/Major/Minor）
# - 复现步骤
# - 预期行为 vs 实际行为
# - 截图证据（snapshot -a 注释截图）
# - 控制台错误日志
```

---

## 安全约束

- Cookie 导入仅在本地 headless/headed 模式下允许
- 不得通过任何隧道/远程连接执行 Cookie 导入
- **Cookie 导入前须用户确认**：执行 `cookie-import-browser` 前明确提示用户"将从真实浏览器读取所有已登录站点的 Cookie"，等待用户确认后再执行
- 敏感截图中不得包含 Token/密码等凭据
- 截图保存到项目 `.gstack/qa-reports/` 而非 `/tmp`

---

## 与 hlskills 集成

| hlskills 技能 | 如何使用 hlbrowse |
|-------------|-----------------|
| `hltest` | 交互式探索替代预写 Playwright 脚本，`snapshot -D` 验证 |
| `hlbug` | Bug 截图 → Read 工具分析，交互式复现 |
| `hllegacy` | 旧项目页面截图 → `responsive` 三屏分析 → 提取设计规范 |
| `hldesign` | 参考页面截图 → `css` / `attrs` / `inspect` 提取样式变量 |
| `hlpm` | 交付前 QA：`$B` 全功能测试 + `snapshot -a` 注释证据 |

---

## 自检

每次使用前运行：

```bash
$B status    # 应返回 "running"
$B goto about:blank && $B text   # 应返回空
```

如守护进程未运行，`$B` 自动启动。首次启动 ~3 秒，后续调用 ~100ms。

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
