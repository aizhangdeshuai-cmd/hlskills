---
name: hla11y
description: 无障碍规范（WCAG 2.2 AA），跨设计→开发→测试三阶段。设计阶段（对比度4.5:1 / 目标24x24px / 文本替代）、开发阶段（语义化HTML / ARIA标签 / 键盘导航 / 焦点指示器）、测试阶段（屏幕阅读器 / 键盘导航 / 焦点陷阱检查）。Use when 用户需要遵循 WCAG 2.2 AA 无障碍规范（设计/开发/测试任一阶段）时调用。
---

# 无障碍规范（WCAG 2.2 AA）

> 属于 `project-dev-workflow` 技能系统的一部分。完整规范见 `accessibility` 技能。

---

## 设计阶段

- **色彩对比度** — 正文文本 >= 4.5:1，大文本/UI组件 >= 3:1
- **交互目标** — 最小尺寸 24x24px
- **文本替代** — 所有非文本内容（图片、图标、图表）提供文本替代
- **信息传达** — 不仅依赖颜色传达信息，配合图标/文字/形状

---

## 开发阶段

### 语义化 HTML
```html
<!-- 好 -->
<button onclick="submit()">提交</button>

<!-- 差 -->
<div onclick="submit()">提交</div>
```

### ARIA 标签
- 交互元素配备 `aria-label`、`aria-describedby`
- 动态内容使用 `aria-live` 区域

### 键盘导航
- 完整 Tab/Shift+Tab/Enter/Escape 支持
- 焦点顺序合理（按视觉顺序）
- 焦点状态有明显视觉指示器（outline/ring）

### 焦点管理
- 模态框打开时，焦点移入模态框
- 模态框关闭时，焦点返回触发元素
- 弹出菜单不得困住焦点

---

## 测试阶段

| 测试项 | 工具/方法 |
|--------|---------|
| 屏幕阅读器 | VoiceOver (Mac) / NVDA (Windows) |
| 键盘导航 | Tab/Shift+Tab 遍历全页面 |
| 焦点陷阱 | 模态框/弹出菜单需焦点闭环 |
| 对比度 | 浏览器开发者工具 Axe 插件 |

---

## 常见反模式（Code Review 必标）

| 反模式 | 正确做法 |
|--------|---------|
| `<div>` 作为按钮 | 使用 `<button>` |
| 仅用颜色表示含义 | 配合文字/图标 |
| `onclick` 无键盘处理 | 使用语义元素或添加 `onKeyDown` |
| 无焦点样式 | 添加可见的 `:focus-visible` 样式 |
| 图片无 alt | 添加有意义的 alt 属性 |

---

## 关联命令
- `/hldesign` — UI/UX设计规范
- `/hltest` — 测试规范

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm-product/path-conventions.md` 中央规范。
