---
name: hlpm-design-spec
description: hlpm 设计阶段实施规范(档一/档二设计稿产出细则,v23 起 DEPRECATED,仅供历史追溯,不得用于新设计稿)。原含 6a.1 规范遵循、6a.2 两档保真度定义、6b 微调/全新页面产出规则、6b.5 截图策略、6b.5.1 交互验证、6b.6 评审把关 + 档二活文档 5 区块扩展(悬浮框/角标/logic-data/联动脚本/框架场景 mounted 绑定/sticky header)。v23 前曾被 SKILL.md §第二阶段步骤 6a-6b.6 引用;v23 起档二活文档(5 区块悬浮框)已被 `templates/bl-marker/` 钉点系统取代。Use when 仅历史追溯——查询旧档二活文档/悬浮框写法的历史规范时;新设计稿一律使用 `templates/bl-marker/` 钉点系统。
---

# hlpm 设计阶段实施规范

> ⚠️ **v23 起 DEPRECATED**:5 区块悬浮框/档二活文档已被 `templates/bl-marker/` 钉点系统取代,本文件仅供历史追溯,不得用于新设计稿。

> 本文件从 `SKILL.md` 第二阶段拆出,承载设计稿产出的**实施细节**(尤其档二活文档的 HTML/JS/CSS 模板)。
> SKILL.md 第二阶段只保留**流程关卡 + 触发条件 + 指向本文件**;具体怎么写见此。
> 配套示例:`examples/order-list-with-export-csv.html`(v21 起已被 `templates/bl-marker/bl-marker-template.html` 取代,冻结存档)

   ### 🆕 5 区块扩展（仅当 6a.2 选"档二:高保真 + 逻辑说明活文档"时强制）

   > **触发条件**：6a.2 选了"档二:高保真 + 逻辑说明活文档" → 3 区块扩为 5 区块；选"档一:高保真 HTML(生产态)"维持 3 区块原结构。
   >
   > **目的**：让设计稿成为"活文档"——交付时附带该页面每个交互元素对应的 PRD/测试用例/状态机/一致性矩阵逻辑，**评审人员点右下角悬浮框即可看到该页面所有逻辑上下文**。
   >
   > **🚨🚨 v18 拆 2 文件适配(本段全部内容据此重读)**:v18 起档二**必须物理拆 2 文件**(见 6a.2 档二):
   > - **`<page>.html`(生产态)**:只含区块 3 + 3.1 的真实 DOM,**不挂任何 `data-prd`/`data-tc`/`data-state`/`data-matrix`、无 🔗 角标、无悬浮框、无 logic-data、无区块 1/2/3.2-3.5**
   > - **`<page>.demo.html`(活文档)**:承载本段描述的**全部 DEV-NOT-FOR-PROD 元素**——区块 1/2/3.2-3.5/4/5 + 悬浮框 + 🔗 角标 + logic-data + data-* 属性
   > - **本段下文出现的"这个 HTML""区块 3 真实元素上挂 data-*""顶部 DEV-NOT-FOR-PROD 白名单注释",一律指 `.demo.html`**;生产态 `.html` 不含这些元素,因此无需白名单区分(v18 前的"单文件靠注释白名单区分"做法已废)
   >
   > **🚨 DEV-NOT-FOR-PROD**:区块 1 / 2 / 3.2-3.5 / 4 / 5 全部是**设计稿元信息**,**只存在于 `.demo.html`,禁止进生产代码**。dev 从生产态 `.html` 直接搬(该文件已无这些元素);若历史上是单文件档二遗留,则**只搬区块 3(含 3.1)整个 DOM** + 关联 CSS。**完整搬运白名单(DOM 排除/属性排除/CSS 排除/保留)见 `hldesign` 技能 §设计与实现分离(单一可信源),本段不重复定义**。

   #### 输出结构：`.demo.html` 内的页面流 + 悬浮框

   - **页面流主体**：`.demo.html` 里放区块 3(真实页面)+ 区块 3.1(默认 ACTIVE 状态),**这份与生产态 `.html` 的区块 3 保持一致**(区别仅在 `.demo.html` 的区块 3 元素额外挂了 `data-*` 属性 + 🔗 角标供联动)。
   - **右下角悬浮框**：所有元信息（区块 1 / 2 / 3.2-3.5 / 4 / 5）收纳到 `.demo.html` 右下角悬浮按钮 + 展开面板。
     - **按钮**：右下角圆形按钮 `#floatingMetaToggle`,显示"📋 元信息 (7)"(7 = 7 个 tab)
     - **面板**：点击按钮展开 `#floatingMetaPanel`,**单页全显 7 个 tab**,垂直滚动查看(不折叠不隐藏)
     - **7 个 tab 顺序**:
       1. 区块 1: 原页面代码 (diff 基线)
       2. 区块 2: diff 标注 (改动清单)
       3. 区块 3.2: 新增弹窗
       4. 区块 3.3: 移除确认弹窗
       5. 区块 3.4: 导入 Excel 弹窗
       6. 区块 3.5: 导入结果反馈
       7. 区块 4+5: 逻辑说明层 (🔗 角标逻辑数据)

   #### 区块 3.2-3.5 实现规范(弹窗状态)

   每个区块 3.x 弹窗在悬浮框 tab 内**真实画出对应 DOM**,默认隐藏,tab 顶部放"📦 展示/隐藏 X 弹窗"开关。点开关→对应弹窗 `display: block`,让评审人真看到弹窗样式,**不是 Mock 按钮**。

   **🚨 弹窗概要默认展开(防主流程漏评审)**: 弹窗在悬浮框 tab 内**仅作为隐藏的二级细节**,主流程评审人打开设计稿时**容易漏掉**。

   > **硬性实现**: 悬浮框 tab 顶部加 **"弹窗概要"section**, 默认展开, 用缩略图 + 1 行说明列出本设计稿涉及的所有弹窗:

   ```html
   <div id="floatingMetaPanel">
     <!-- 弹窗概要(默认展开) -->
     <details open>
       <summary>📦 弹窗概要(本设计稿共 4 个弹窗)</summary>
       <ul>
         <li>📦 区块 3.2 新增弹窗 — <a href="#modal-3-2">查看</a> | 触发:点击"新建"按钮</li>
         <li>📦 区块 3.3 移除确认弹窗 — <a href="#modal-3-3">查看</a> | 触发:点击"删除"按钮</li>
         <li>📦 区块 3.4 导入 Excel 弹窗 — <a href="#modal-3-4">查看</a> | 触发:工具栏"导入"按钮</li>
         <li>📦 区块 3.5 导入结果反馈 — <a href="#modal-3-5">查看</a> | 触发:导入完成回调</li>
       </ul>
     </details>
     <!-- 7 个 tab 内容照旧 -->
   </div>
   ```

   - **概要默认 `open`**: 评审人打开悬浮框立即看到所有弹窗存在性,**不能漏**
   - **概要加"触发"列**: 让评审人不进 tab 就知道"什么场景会触发这个弹窗"
   - **概要加锚链接**: 点击概要的"查看"→ tab 切到对应区块 + 平滑滚动

   #### 区块 4 + 5 实现规范(逻辑说明层)

   - **区块 4 改造**:从原 "在页面 `<body>` 末尾追加抽屉" 改为"**抽屉放悬浮框 tab 7**"。`🔗 角标` 保留在区块 3 真实元素上,**点击角标不弹页面右侧抽屉,而是同步展开悬浮框 + 切到 tab 7 + 高亮对应条目**。
   - **区块 5**:仍以 `<script type="application/json" id="logic-data">` 形式存在,但放进悬浮框 tab 7 内部(默认 display: none 或在悬浮框内,反正不暴露给生产代码扫描)。

   #### 字段约定(不变)

   - `data-prd` / `data-state` / `data-tc` / `data-matrix` 属性挂在 **`.demo.html` 的区块 3 元素上**(这些属性是元信息载体,是 demo 文件专属;生产态 `.html` 的区块 3 不含这些属性)
   - **缺失某属性 = 该元素无该维度逻辑**

   #### 🚨 角标 → 悬浮框联动脚本(必出物,非可选)

   **问题**: agent 按上面规范生成设计稿时,通常会**漏抄** `examples/order-list-with-export-csv.html` 第 630-658 行那段 click handler JS。结果就是页面上 `?` 角标看起来存在,但点击**完全没反应**(没有打开悬浮框、没有切到 tab 7、没有高亮)。**这是个高频 bug**。

   **修复后的必出清单**(agent 生成 5 区块扩展设计稿时,**以下 4 个产物全部必须存在,缺一即视为设计稿不合格**):

   | # | 产物 | 关键标识 | 不存在的后果 |
   | --- | --- | --- | --- |
   | 1 | 角标 HTML | `<sup class="logic-badge" data-prd="...">?</sup>` | 评审看不到逻辑说明入口 |
   | 2 | data-* 属性 | 角标所在元素挂 `data-prd` / `data-tc` / `data-state` / `data-matrix` | 找不到 PRD 关联,无法定位 logic-data |
   | 3 | logic-data JSON | `<script type="application/json" id="logic-data">` | 悬浮框 tab 7 没内容 |
   | 4 | **联动脚本(JS)** | `<script>` 内含 `querySelectorAll('.logic-badge').forEach(badge => { badge.addEventListener('click', ... })` | **角标点了没反应——本 bug 的根因** |

   **参考脚本模板(必须照搬结构,只改 BR-/TC- 等数据)**:

   ```html
   <script>
   (function () {
     'use strict';
     // ⚠️ DEV-NOT-FOR-PROD: 整个 <script> 块不进生产代码

     // ================== 悬浮框开关 ==================
     const toggle = document.getElementById('floatingMetaToggle');
     const panel = document.getElementById('floatingMetaPanel');
     const closeBtn = document.getElementById('floatingMetaClose');

     function openPanel(targetTabId) {
       panel.classList.add('open');
       if (targetTabId) {
         const target = document.getElementById(targetTabId);
         if (target) {
           setTimeout(() => target.scrollIntoView({ behavior: 'smooth', block: 'start' }), 250);
         }
       }
     }
     function closePanel() { panel.classList.remove('open'); }

     toggle.addEventListener('click', () => {
       if (panel.classList.contains('open')) closePanel();
       else openPanel();
     });
     closeBtn.addEventListener('click', closePanel);
     document.addEventListener('keydown', (e) => {
       if (e.key === 'Escape' && panel.classList.contains('open')) closePanel();
     });

     // ================== 🔗 角标 → 悬浮框切到 tab 7 高亮 ==================
     const logicData = JSON.parse(document.getElementById('logic-data').textContent);

     document.querySelectorAll('.logic-badge').forEach(badge => {
       badge.addEventListener('click', (e) => {
         e.stopPropagation();
         e.preventDefault();

         // 找挂载 data-* 的最近祖先
         const host = badge.closest('[data-prd],[data-tc],[data-state],[data-matrix]') || badge.parentElement;
         const prdIds = (host.dataset.prd || '').split(',').filter(Boolean);
         if (prdIds.length === 0) return;

         const firstPrdId = prdIds[0].trim();

         // 高亮目标 logic-item
         document.querySelectorAll('.logic-item.highlight').forEach(el => el.classList.remove('highlight'));
         const target = document.getElementById('logic-' + firstPrdId);
         if (target) target.classList.add('highlight');

         // 角标自身也高亮 0.5s
         badge.classList.add('highlight');
         setTimeout(() => badge.classList.remove('highlight'), 500);

         // 打开面板并滚动到 tab 7
         openPanel('meta-tab-7');
       });
     });
   })();
   </script>
   ```

   #### 设计稿自检(防漏抄脚本)

   **触发时机**: 步骤 6b 设计稿生成后 + 6b.5 截图前,**主 agent 必须执行以下自检**:

   ```bash
   # 1. 角标 HTML 存在
   grep -c 'class="logic-badge"' docs/{ver}/design/*.html
   # 期望: ≥ 1

   # 2. data-* 属性存在
   grep -cE 'data-(prd|tc|state|matrix)=' docs/{ver}/design/*.html
   # 期望: ≥ 1

   # 3. logic-data JSON 存在
   grep -c 'id="logic-data"' docs/{ver}/design/*.html
   # 期望: = 1

   # 4. 🚨 联动脚本存在(关键检查)
   grep -c "addEventListener('click'" docs/{ver}/design/*.html
   grep -c "querySelectorAll('.logic-badge')" docs/{ver}/design/*.html
   # 期望: 各 ≥ 1

   # 5. 联动脚本能引用到 logic-data
   grep -c "getElementById('logic-data')" docs/{ver}/design/*.html
   # 期望: ≥ 1
   ```

   **任一检查失败** → 标 🔴 + 阻塞 6b.5 截图 + 必须补齐,**不得"先截图后补脚本"**(脚本未生效时截图无法反映交互能力)。

   **`verifier` 二次验证**: 设计评审时(默认模式 6b.6 立即评审 / 旧分阶段模式步骤 7),`verifier` 调 `Skill hlbrowse` 打开设计稿(档二用 `.demo.html`),**实际点击 1 个角标**(选最大块的 PR-XXX),**必须看到悬浮框展开 + 切到 tab 7 + 对应 logic-item 高亮**。否则评审不通过。

   #### 🚨 框架场景: 脚本必须在 mounted 回调内执行(高频坑)

   **问题根因** (真实案例 `ehr/docs/v2/design/blacklist.html`): 设计稿引入了 Vue 2 (`new Vue({el: '.page', ...})`)。Vue 在挂载期间**重排 `.page` 子树**,导致 `<script>(function(){ querySelectorAll('.logic-badge').forEach(badge => badge.addEventListener('click', ...)) })()</script>` 在 script 顶层阶段绑的 listener **被 Vue 重排 DOM 时丢掉**。控制台零报错,看似正常,但点击角标**毫无反应**(panel 不开,无高亮)。

   **`examples/order-list-with-export-csv.html` 没引入任何框架,所以示例能跑 ≠ v16 设计稿能跑**。

   **触发条件**(命中任一 → 必须按框架/UI 库场景处理):

   ```bash
   grep -cE "new Vue|new app|createApp|createElement|useEffect|new ReactDOM|\\\$\\(.+?\\)\\.ready|\\\$\\(.+?\\)\\.on\\(|el-form|el-table|el-button|ant-table|ant-form|antd|element-plus|naive-ui|ELEMENT\\.|ElementUI" docs/{ver}/design/*.html
   # 期望: 命中即进入框架/UI 库场景
   ```

   | 命中 | 场景 | 修复方式 |
   | --- | --- | --- |
   | `new Vue\|createApp` | Vue 2/3 | `new Vue({ mounted() { /* 在此绑事件 */ } })` 或 `Vue.createApp(...).mount(...)` 后**追加**事件绑定脚本 |
   | `useEffect\|createElement\|ReactDOM` | React | `useEffect(() => { /* 在此绑事件 */ }, [])` |
   | `$(...).ready\|$(...).on` | jQuery | `$(function() { /* 在此绑事件 */ })` 或 `$(document).ready(...)` |
   | **`el-form\|el-table\|el-button\|ant-form\|antd`** | **ElementUI / Element Plus / Ant Design Vue / Naive UI 等** | **即使没显式 `new Vue`,UI 库内部用 Vue/React 接管 el-form 子树 → 必须用 `mounted` / `useEffect` / `setTimeout(fn, 0)` 延迟绑定** |

   **修复模板** (Vue 2,以 blacklist.html 为例):

   ```html
   <script src="https://cdn.jsdelivr.net/npm/vue@2.7.16/dist/vue.min.js"></script>
   <script>
   // ⚠️ DEV-NOT-FOR-PROD: 框架 + 元信息, 整体不进生产代码

   // 业务 Vue 实例先挂载
   new Vue({
     el: '.page',
     data: () => ({ /* ... */ }),
     methods: { /* ... */ },
     mounted() {
       // ===== 🔗 角标事件必须在 mounted 内绑 =====
       // 原因: Vue 挂载期间重排 .page 子树,顶层 script 绑的 listener 会丢失
       document.querySelectorAll('.logic-badge').forEach(badge => {
         badge.addEventListener('click', (e) => {
           e.stopPropagation();
           e.preventDefault();
           const host = badge.closest('[data-prd],[data-tc],[data-state],[data-matrix]') || badge.parentElement;
           const prdIds = (host.dataset.prd || '').split(',').filter(Boolean);
           if (prdIds.length === 0) return;
           const firstPrdId = prdIds[0].trim();
           document.querySelectorAll('.logic-item.highlight').forEach(el => el.classList.remove('highlight'));
           const target = document.getElementById('logic-' + firstPrdId);
           if (target) {
             target.classList.add('highlight');
             target.scrollIntoView({ behavior: 'smooth', block: 'center' });
           }
           const panel = document.getElementById('floatingMetaPanel');
           panel.classList.add('open');
           const tab7 = document.getElementById('meta-tab-7');
           if (tab7) {
             setTimeout(() => tab7.scrollIntoView({ behavior: 'smooth', block: 'start' }), 250);
           }
         });
       });

       // ===== 悬浮框开关也要在 mounted 内绑 =====
       const toggle = document.getElementById('floatingMetaToggle');
       const panel = document.getElementById('floatingMetaPanel');
       const closeBtn = document.getElementById('floatingMetaClose');
       if (toggle) toggle.addEventListener('click', () => panel.classList.toggle('open'));
       if (closeBtn) closeBtn.addEventListener('click', () => panel.classList.remove('open'));
     }
   });
   </script>
   ```

   **自检 grep 加 1 条**(命中即警告必须用 mounted 回调):

   ```bash
   # 6. 🚨 框架检测 — 命中即必须用 mounted/useEffect/$(document).ready 回调
   grep -cE "new Vue\(|createApp\(|useEffect\(|new ReactDOM|createElement\(|\\\$\(.+?\\)\\.ready" docs/{ver}/design/*.html
   # 命中 ≥ 1 → 必须验证事件绑定脚本在回调内,不在 <script> 顶层
   ```

   **关联校验**: 框架场景下,主脚本内 `querySelectorAll('.logic-badge').forEach` **必须出现在 `mounted() {` / `useEffect(` / `$(function(` 等回调体内部**,而非顶层 IIFE。检查方式:

   ```bash
   # 找 mounted/useEffect 回调位置
   awk '/mounted\(\)\s*{|useEffect\(|\\\$\(function/{found=NR; depth=0} found && NR>=found {if (/{/) depth++; if (/}/) depth--; if (depth>0 && /logic-badge/) {print "OK: 角标绑定在回调内 第"NR"行"; exit}}' docs/{ver}/design/*.html
   # 期望: 输出 "OK: 角标绑定在回调内 第N行"
   ```

   **`verifier` 框架场景二次验证**: 设计评审时(默认 6b.6 / 旧分阶段 7),`verifier` 不仅点击角标验证交互,**还必须在控制台跑 `document.querySelectorAll('.logic-badge')[0].onclick !== null || getEventListeners`** 的等价检查(用 `dispatchEvent` 看是否触发)。Vue 场景下还需确认 listener 绑在 `mounted` 后,而不是 Vue 挂载前的同一 DOM 节点。

   **真实案例参考**:`ehr/docs/v2/design/blacklist.html` —— 已按本规范修复,详见该文件 `new Vue({ mounted() { ... } })` 段。

   #### 🚨 悬浮框标题栏滚出视口(高频 UI bug)

   **问题现象**: 弹框打开后点击角标 → 自动滚到 tab 7 → **标题栏(设计稿元信息 + 副标题 + × 关闭按钮)被滚出视口**。评审人看不到自己在看什么、不知道怎么关。

   **根因** (双 bug 叠加):
   1. `.floating-meta-panel-header` 设了 `position: sticky; top: 0;` 但 panel 自身有 `padding: 24px;`——sticky 实际粘在 panel **padding 内边**顶端,视觉上跟"panel 顶端"差 24px
   2. JS 用 `target.scrollIntoView({ block: 'start' })` 把 tab 7 推到 panel 顶部,**sticky header 被推出视口**——`scrollIntoView` 不考虑 sticky 元素

   **修复**(必须 2 处都改):

   **CSS**(panel 加 `scroll-padding-top`):

   ```css
   .floating-meta-panel {
     /* ...原有... */
     padding: 24px;
     /* 🚨 关键: scroll-padding-top 让 scrollIntoView 跳过 sticky header */
     /* 数值 = header 高度(约 70px) + 顶部 padding(24px) */
     scroll-padding-top: 96px;
   }
   ```

   **JS**(`scrollIntoView` 保持 `block: 'start'`,靠 CSS 的 `scroll-padding-top` 自动让位):

   ```js
   // ✅ 正确: 配合 scroll-padding-top, 目标跳到 header 下方,header 始终可见
   tab7.scrollIntoView({ behavior: 'smooth', block: 'start' });

   // ❌ 仅用 block: 'center' 也可,但 tab 7 会到视口中段,
   //    评审人看不到 tab 1-6 的位置,上下文不足
   // tab7.scrollIntoView({ block: 'center' });
   ```

   **真实案例**: `ehr/docs/v2/design/blacklist.html` 第 103-115 行 panel CSS + 第 920 行 `scrollIntoView({ block: 'center' })`。

   **`verifier` 必查项**: 设计评审时(默认 6b.6 / 旧分阶段 7),`verifier` 点击角标后**必须截图**,**截图里能看到标题栏 + × 按钮**才算通过。看不到 → 评审不通过。

   **🚨 JS 兜底**(环境兼容终极保险): 某些浏览器 + ElementUI/Antd 组合会让 `position: sticky` 失效,加 JS 监听强制把 header 钉在 panel 顶部:

   ```js
   const header = document.querySelector('.floating-meta-panel-header');
   const panelEl = document.getElementById('floatingMetaPanel');
   if (header && panelEl) {
     const padTop = parseInt(getComputedStyle(panelEl).paddingTop, 10) || 24;
     const stickHeader = () => {
       const rect = header.getBoundingClientRect();
       const panelRect = panelEl.getBoundingClientRect();
       const expectedTop = panelRect.top + padTop;
       if (Math.abs(rect.top - expectedTop) > 1) {
         header.style.transform = `translateY(${expectedTop - rect.top}px)`;
       } else {
         header.style.transform = '';
       }
     };
     panelEl.addEventListener('scroll', stickHeader, { passive: true });
     window.addEventListener('resize', stickHeader);
     new MutationObserver(stickHeader).observe(panelEl, { childList: true, subtree: false });
   }
   ```

   **CSS 三重保险**:
   ```css
   .floating-meta-panel-header {
     position: -webkit-sticky;  /* Safari */
     position: sticky;          /* 现代浏览器 */
     top: 0;
     background: #fff;          /* 不透明,否则内容会透过来 */
     z-index: 2;                /* 必须比 meta-section 高 */
     flex-shrink: 0;            /* 不被 flex 压缩 */
   }
   ```

   **自检 grep** (1 条):
   ```bash
   # 7. 🚨 panel 必须有 scroll-padding-top (跳过 sticky header)
   grep -c "scroll-padding-top" docs/{ver}/design/*.html
   # 命中 ≥ 1 → 通过;= 0 → 标 🔴
   ```

   #### 顶部注释模板(强制)

   ```html
   <!--
     设计与实现分离(v18): 本注释模板用于 `.demo.html`(活文档) = 区块 3 真实页面 + 悬浮框元信息面板
     生产态 `.html` 无需本注释(它只含区块 3,不含任何 DEV-NOT-FOR-PROD 元素)
   
     🚨 DEV-NOT-FOR-PROD: 下面 4 个区块是设计稿元信息,禁止搬到生产代码:
       ❌ 区块 1 (原页面代码 / diff 基线)
       ❌ 区块 2 (改动清单)
       ❌ 区块 3.2-3.5 (4 个弹窗状态演示)
       ❌ 区块 4 + 5 (逻辑说明层: 🔗 角标 + 抽屉 + logic-data JSON)
       ❌ 悬浮框本身 (右下角 📋 按钮 + 展开面板)
   
     ✅ 生产代码可搬:
       - 区块 3 + 区块 3.1 整个 DOM
       - 关联 CSS(排除 .logic-* / .floating-meta-* / [data-prd|state|tc|matrix] / .logic-badge / #logicPanel / #floatingMeta* / #logic-data)
   
     详情: docs/review/v15-multi-angle-audit.md "设计稿元信息不进生产代码" 段

     **🚨 与 hldev 端对齐(白名单镜像)**: 本节列出的白名单同步写入 `hldev/SKILL.md` 第 0 步"设计稿搬移白名单"段。任何开发与产品对搬移范围有分歧 → 以 `hldev/SKILL.md` 第 0 步为准(开发段有最终裁定权,因为它负责落地)。
   -->
   ```

   #### diff 三区块(区块 1 / 区块 2)规则不变

   - 区块 1 (原页面 diff 基线) + 区块 2 (改动清单) 仍按 v14 强制规范,只是**位置从页面流移到悬浮框 tab 1/2**
   - 已有的"全新页面场景 = 区块 1/2 内容为空标注"规则保留(放悬浮框 tab 1/2 里,空状态更不明显)

   **完整示例**:见 `hlpm/examples/order-list-with-export-csv.html`(悬浮框版本,对应 v18 档二 `.demo.html` 形态)
