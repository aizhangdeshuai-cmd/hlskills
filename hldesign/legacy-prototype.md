# 维护历史五区块设计稿

以下清单适用于[历史档二格式](../hlpm/design-spec.md)的存量文件。

设计稿可能含以下元信息,**全部不进生产代码**:

| 类别 | 例子 | 为什么不能搬 |
|------|------|------|
| diff 三件套 | 区块 1(原页面代码 / diff 基线)+ 区块 2(改动清单) | 仅评审用,生产代码无意义 |
| 弹窗状态演示 | 区块 3.2-3.5(4 个弹窗的打开状态截图) | 仅评审用,生产代码按需弹窗 |
| 逻辑说明层 | `🔗 角标` + 抽屉 + `<script id="logic-data">` JSON | 设计稿内嵌的 PRD/TC 引用,运行时不需要 |
| 悬浮元信息面板 | 右下角 `📋 元信息` 按钮 + 展开面板 | 仅评审用,运行时是 UI 噪音 |
| `data-prd` / `data-state` / `data-tc` / `data-matrix` / `data-diff-mode` 属性 | 任何挂载的逻辑指针属性 | 元信息载体,运行时无用且污染 DOM |
| diff 视觉辅助 | `.diff-add` / `.diff-mod` / `.diff-del` 选择器 | 评审视觉辅助,生产无需 |

## 历史生产代码搬运白名单

dev 拿到设计稿时,**只搬以下内容到生产代码**:

- ✅ **真实页面 DOM**:区块 3(含 3.1 默认 ACTIVE 状态)的所有元素
- ✅ **关联 CSS**:但**排除**以下类名/属性/选择器:
  - 类名:`.logic-*` / `.floating-meta-*` / `.logic-badge`
  - 属性:`[data-prd]` / `[data-state]` / `[data-tc]` / `[data-matrix]` / `[data-diff-mode]`
  - 选择器:`.diff-add` / `.diff-mod` / `.diff-del`
  - ID/脚本:`#logicPanel` / `#floatingMetaToggle` / `#floatingMetaPanel` / `#logic-data`
- ❌ 不搬区块 1-2-3.2-3.5-4-5 任何元信息
- ❌ 不搬右下角悬浮框
- ❌ 不搬 `<!-- DEV-NOT-FOR-PROD -->` 注释包裹的内容

## 5 区块扩展识别

如设计稿含 5 区块扩展(区块 3.2-3.5 弹窗在悬浮框 tab 内),**仅保留区块 3 + 3.1 DOM** 作为生产代码,其余 4 个区块禁止搬到生产。

## 历史格式自查清单

设计稿交付前,`designer` 需自查:
- [ ] 顶部有 `<!-- DEV-NOT-FOR-PROD -->` 注释 + 明确搬运白名单
- [ ] 区块 1-5 / 悬浮框外层有 `<!-- ⚠️ DEV-NOT-FOR-PROD -->` 围栏注释
- [ ] `data-*` 属性仅挂在真实页面元素上(元信息面板内部不算)
- [ ] 右下角悬浮框可正常展开/收起,不影响真实页面交互

dev 拿到设计稿时,需自查:
- [ ] 真实页面 DOM 完整可搬
- [ ] 元信息(区块 1-5 / 悬浮框 / `data-*` / `.logic-*` / `.diff-*` / `#floatingMeta*` / `#logic-data`)已剥离
- [ ] 运行时无 "📋 元信息" 按钮 / 🔗 角标 / logic-data 残留
