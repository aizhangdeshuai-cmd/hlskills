---
name: hlpm
description: 多角色协作-产品段（23步）。从需求到交付物打包的全流程,覆盖加载上下文→竞品分析(含参考咨询)→PRD→设计规范检查→保真度咨询→设计→测试用例→三项一致性终检→打包交付。与 hldev 配套使用:产品交付物经重量评审会签后交接给开发。Use when 用户提出新需求且产品与开发是两个角色、需要显式交接,或调用 /hlpm。
---

# 多角色协作-产品段流程

> ## ⚠️ 流程纪律的执行机制
>
> 本流程的"硬性关卡""返回上一步""强同步规则"是 markdown 文本纪律,Claude Code 不会机械地强制执行。Agent 加载后会**自觉遵守**,但如 Agent 模型弱或 prompt 冲突,关卡可能失效。
>
> **真实约束**:文档本身 + Agent 自觉 + 用户手动打断。
> **不是**:Claude Code runtime hook 拦截 + 状态机门禁。
>
> 如发现 Agent 在第 X 步没停下来等你确认 / 直接跳过第 Y 步 / 没返回上一步重做,请**手动打断**让它重读 SKILL.md 对应章节。
>
> 详细能力边界见仓库 `README.md` 「⚠️ 能力边界声明」段。

---

## §诚实声明:会签机制的真实约束

本技能步骤 5/7/9/9a 出现的"5 方会签"/"2 方会签"是 markdown 描述——**实际执行时,同一个 LLM 在主 agent 上下文中按多个 role prompt 顺序扮演,产出意见**。**不是**真·多 agent 进程级对抗。

**意见多样性受限于**:
- 同一 LLM 的同质化倾向(5 个角色可能给类似意见)
- 单一温度参数(无法对不同角色设不同温度)
- 上下文共享(后发言角色可能参考前角色意见)

**真实价值**:角色提示词强制模型从特定维度审视(structured review),**不是**独立对抗(independent review)。

**如需真·多模型对抗**:需额外挂载多 LLM API key 配置,本流程不内置。

> 步骤 5/7/9/9a 直接引用本段(避免重复书写)。


> 属于 `hlskills` 技能系统。与 `hldev` 配套使用，构成"产品 + 开发"分工的标准开发流水线。
> 完整规范见 `hlskills/SKILL.md`。

---

## 🚨 核心纪律(先读再启动)

> 本节是本技能的最高约束,优先级高于下面所有"通用纪律"和 23 步流程

### 完整内容(详见 `disciplines/` 子目录)

| 段 | 文件 | 主题 |
| --- | --- | --- |
| 🚨 角色边界铁律 | `disciplines/role-boundary.md` | 三条边界 + 输出范围 + 角色 Agent 映射 + 启动清单 + 触发 hlkb |
| 通用纪律 | `disciplines/completion-validation.md` | 完成前验证 + 豁免清单 + 受阻停止 + 升级 |
| 三项强同步 | `disciplines/strong-sync.md` | PRD/设计/用例三项一致 + 小改快通道 |
| 版本基线 commit | `disciplines/baseline-commit.md` | 基线 v1 提交规范 |

### 一句话摘要

- **角色边界铁律**: 产品段绝不修改产品代码 + 代码修改唯一入口是 `hldev` + 设计稿是条件性输出不是必出
- **完成前验证**: 证据先于断言 + 豁免清单区分文档/代码类 + 3 次驳回升级用户决策
- **三项强同步**: PRD/设计/用例三项必须一致 + 驳回强制重走 + diff < 20 行小改豁免通道
- **版本基线 commit**: PRD/设计/用例基线 v1 必须 commit + 格式 `docs(vX): baseline {type} v1` + 项目不进 git 时允许跳过

## 产品段开发流程（23 步）

> **步骤编号说明**:23 步用分层标签(0/0.5/0.6/1/2a-c/3/4/5/6a.0-2/6b/6b.5/7/8/9/9a/9.5/10/11/12)而非线性 1→23,子步骤(如 6a.1)表示同一阶段内的细分。带标签的步骤合计 23 个;实际执行时按 0.5 步评估的规模/设计条件会跳过部分步骤。

### 第零阶段：加载项目上下文
0. **加载已有文档** — 在分析新需求之前，**先读取项目已有知识**，避免重复分析：
   - 如存在 `.hl/memory/` → Read 全部 memory 文件（project.md / techstack.md / architecture.md / conventions.md / working.md）
   - 如存在已有分析文档（竞品分析 / PRD / 技术设计 / ADR）→ Read 加载
   - 如有 `docs/design/spec.md` 或同级设计规范文件 → **记录路径**，供 6a.1 使用
   - 迭代需求场景：必须先理解项目现状，再分析新需求

### 第零阶段.5：规模判断(阻塞点)

0.5. **★ 需求规模与设计需求评估** — `analyst` 启动后,**一次性用 `AskUserQuestion` 问 3 个问题**（合并批量问,避免后续重复打断）:

**问题 1: 本次需求规模**
- 选项 A: **轻量需求** (业务规则 < 3 条,只改 1 个模块/页面,预计代码 < 100 行)
- 选项 B: **标准需求** (业务规则 3-10 条,涉及 2-3 个模块)
- 选项 C: **复杂需求** (业务规则 > 10 条,涉及多模块/多角色/有非功能要求)

**问题 2: 本次是否涉及设计调整**
- 选项 A: **涉及**(UI / 交互 / 页面布局 / 视觉变化)
- 选项 B: **不涉及**(纯后端 / 数据 / 接口 / 状态机 / 业务规则 / 算法)

**问题 3: 评审模式选择**

> 用白话描述触发时机：两种模式都"在 PRD + 设计 + 用例都写完后开会",区别在**开几次会 / 几个角色**

- 选项 A: **分阶段评审**(重量, 3 场独立会签:PRD/设计/用例 各开 1 次会, 串行执行)
  - 适用:复杂需求 / 跨模块改动 / 多人协作 / 高风险改动
  - 流程:步骤 5 PRD 评审 → 步骤 7 设计评审 → 步骤 9 用例评审, 每场会签通过后才进入下一步
  - 强同步规则:任一驳回强制重走后续所有评审
- 选项 B: **集中评审**(轻量, 1 场集中评审——PRD + 设计 + 用例**全部写完后**开 1 次会, 5 角色集中讨论)
  - 适用:轻量需求 / 迭代优化 / bug 修复 / 单模块微调
  - 流程:跳过中间 3 场会签, 在 9.5 一致性终检**之前**插入 1 场集中评审
  - 5 角色都参与(`analyst` 主持 + `architect` + `designer` + `executor` + `test-engineer`)——集中评审不等于"少角色",而是"5 人 1 场会"代替"5 人 3 场会", 仍产出交叉审视
  - 强同步规则:驳回时只需在该场评审中说明修改意见, 改完后重走 1 场即可

**根据回答决定后续路径**:

| 规模 | 涉及设计 | 评审模式(默认) | 路径 | 跳过步骤 |
|------|---------|---------------|------|---------|
| 轻量 | 涉及 | **集中评审** | 轻量+设计+集中评审 路径 | 2b/2c(竞品) / 6a.2 简化 / 中间 3 场评审合并 / 9.5 只跑 2 矩阵 |
| 轻量 | 不涉及 | **集中评审** | 轻量无设计+集中评审 路径 | 2b/2c(竞品) / 整个第二阶段 / 中间 3 场评审合并 / 9.5 只跑 2 矩阵 |
| 标准 | 涉及 | 分阶段评审(默认) | 完整 23 步 | (无跳过) |
| 标准 | 不涉及 | 分阶段评审(默认) | 标准无设计 路径 | 整个第二阶段 |
| 复杂 | 涉及 | 分阶段评审(强制) | 完整 23 步 + 加严 | (无跳过;3 场评审不合并,5 角色视角全覆盖) |
| 复杂 | 不涉及 | 分阶段评审(强制) | 复杂无设计 路径 | 整个第二阶段;非功能需求加深 |

> **评审模式可被 0.5 步骤问题 3 覆盖**:
> - 复杂需求"评审模式"字段被锁定为"分阶段评审",**用户不可改**(风险太大)
> - 轻量/标准需求"评审模式"字段可由用户问题 3 自由选择
> - 用户选择优先于默认:轻量需求用户也可选"分阶段评审"(想要更严格把关)

**注意**:
- 用户可随时在后续步骤中**升级路径**(如发现原本"轻量"实际复杂)
- 升级路径时,已完成的步骤不重做,**补齐跳过的步骤**即可
- 用户可随时在后续步骤中**降级路径**(如发现"涉及设计"实际不涉及) → 跳过整个第二阶段

0.6. **版本目录选择**(`analyst`,**自动派生为主**,不再单独阻塞)
- 扫描历史版本目录:`ls -d docs/v*/ 2>/dev/null | sort -V`
- **3 种情况处理**(详见 `path-conventions.md` §0.2):
  - **情况 A**(无历史版本):**自动**创建 `docs/v1/`,后续所有交付物写 `docs/v1/`(不询问)
  - **情况 B**(全部已开发):**自动**创建下一版本号(如 `docs/v3/`),不询问
  - **情况 C**(有未开发版本):**追加 1 次 `AskUserQuestion` 询问**(0.5 步骤的 3 个问题已合并问完,这里只问 1 个):
    - 列出所有未开发版本 + 交付时间 + 业务规则数 + 一致性矩阵状态
    - 选项:在指定旧版本上修改 / 新建版本
- 决定后,记录当前 `{ver}` 变量(如 `v1` / `v2`),后续所有步骤按 `docs/{ver}/<doc-name>` 路径输出
- 路径替换规则:任何文档步骤中提到的 `docs/prd.md` 实际输出为 `docs/{ver}/prd.md`,以此类推
- 详细规范见 `path-conventions.md` §零(版本目录管理)

### 第一阶段：需求阶段

1. **需求分析** — `analyst` 基于已有文档上下文，理解并梳理新需求。
   - 如用户提供需求文档（含图片）：用 Read 工具读取文本；优先用模型原生多模态识别图片中的草图/流程图/参考截图
   - 图片内容与文字需求合并分析，形成完整需求理解

2a. **★ 竞品分析 - 询问参考竞品**（阻塞点）
   - 用 `AskUserQuestion` 问用户：是否有参考竞品？
   - 选项：**有** / **无** / **不确定**
   - 【阻塞点】：未询问用户不得进入 2b/2c
   - 不允许"用户没回应就跳过"或"默认无参考"

2b. **竞品分析 - 读取参考竞品**（仅当 2a 选"有"时执行）
   - 用户指定具体竞品：读取其官网/产品文档/用户评价，输出参考竞品画像
   - 用户提供文件（截图/录屏/PRD）：用多模态识别内容
   - 产出：参考竞品核心功能 / 差异化优势 / 定价策略
   - 完成后进入 2c

2c. **竞品分析 - 品类调研**（新项目必做;已有项目的迭代需求推荐做）
   - 识别 3-5 个直接竞品与间接竞品
   - 输出竞品分析报告：功能矩阵 / 定价 / 优劣势
   - 明确自身产品定位与差异化方向

3. **目标用户画像 / 差异化定位**（仅新项目，hlpm 路径）
   - 输出用户群体 / 使用场景 / 核心诉求排序
   - 差异化定位必须能"一句话说清"，否则标 🔴 风险

4. **PRD 编写**（`analyst` 生成内容 → 写入文件，**按功能点剖切(默认) + 6 附录**）
   - **🚨 章节结构(默认:按功能点剖切)**: PRD 章节按 **"每个功能点 1 张卡片"** 组织(参见下方"14 字段功能点卡片模板"),不是按"业务逻辑/操作流程/数据流转/状态机/权限"等维度。理由:
     - 按维度剖切 → 读一个功能点要跳 5 个章节(散)
     - 按功能点剖切 → 读一个 BL-N 一节搞定(集中)
     - 横切内容(状态机全图/权限矩阵/埋点全表/原型截图/决策历史/差异清单)走附录
   - **结构模板**:
     ```
     # PRD · {项目名} v{N}

     §0 上下文与依据 (元信息 + 业务背景 + 跳过项 + 唯一迭代点 + 章节地图)
     §1 ~ §N  BL-1 ~ BL-N  每张卡片(14 字段模板)
     附录 A    状态机总图(跨功能)
     附录 B    角色 × 权限点矩阵(跨功能)
     附录 C    数据埋点需求(全表)
     附录 D    原型截图引用
     附录 E    关键决策点对比(如 BL-N 的 3 方案对比)
     附录 F    v{N} 与 v{N-1} 差异清单
     ```

   - **14 字段功能点卡片模板**(每个 BL-N 一张,字段顺序固定):
     ```
     ## §{N} BL-{N} {功能点名称}(继承 v{N-1} / v{N} 新增)

     > **一句话**: {该功能一句话描述}
     > **重要性**: {P0/P1/P2 + 缺失影响}
     > **状态机变化**: {本功能影响的状态机边,或不涉及}
     > **架构决策**: {关键架构选型,如"方案 C 软唯一 + 合并"}
     > **原型**: docs/v{N}/design/{page}.html #{锚点}

     ### {N}.1 用例编号
     `BL-{N}`

     ### {N}.2 用例名称
     {功能点名称 + 一句话说明}

     ### {N}.3 优先级
     **{P0/P1/P2}**({缺失影响})

     ### {N}.4 角色
     1. **{角色 1}**: {可/不可触发 + 所需权限}
     2. **{角色 2}**: ...

     ### {N}.5 前置条件
     1. {条件 1}
     2. {条件 2}

     ### {N}.6 触发事件
     {用户怎么进入这个功能}

     ### {N}.7 主功能场景
     1. {步骤 1}
     2. {步骤 2}
     ...

     ### {N}.8 拓展
     #### {N}.8.1 替代路径({名称})
     {描述}
     #### {N}.8.2 异常路径 A — {名称}
     {描述}
     #### {N}.8.3 异常路径 B — {名称}
     {描述}

     ### {N}.9 业务逻辑
     1. {规则 1}
     2. {规则 2}

     ### {N}.10 关键决策点({可选,本功能有架构决策时才有})
     {3 方案对比表 + 选中方案 + 选中理由}

     ### {N}.11 数据埋点
     | ID | 事件名称 | 触发时机 | 上报参数 | 采样率 |
     |---|---|---|---|---|
     | ... | ... | ... | ... | ... |

     ### {N}.12 验证标准
     | AC | 验收点 | 可追溯测试 | 优先级 |
     |---|---|---|---|
     | ... | ... | ... | ... |

     ### {N}.13 发生频率
     **{高/中/低/N/A}**({描述})

     ### {N}.14 非功能性需求
     1. **{性能/安全/兼容/一致性 NFR-XX-N}**: {描述}
     2. ...

     ### {N}.15 未解决的问题
     (本期 v{N} 无, 如下为 v{N+1}+ 预留)
     1. **{预留 1}**: {描述}
     2. ...
     ```
     - **14 字段全填**, 不留 N/A。频率/未决问题/无 NFR 也要写(如"无 N/A", "低(每月 X 次)", "无 v3 范围外预留")
     - **数据埋点 / 验证标准**用 4 列对照表(本质是"事件/AC 索引"),散文化反而难读
     - **业务逻辑 / 主功能场景 / 拓展**用编号列表(便于后续引用"BL-12 业务规则第 3 条")
     - **关键决策点**(3 方案对比)单列, 不混在"业务逻辑"里
     - **每张卡片顶部 > 引言 5 行**: 一句话 / 重要性 / 状态机变化 / 架构决策 / 原型 — 让读者 5 秒掌握本功能全貌

   - **何时用维度剖切(旧式)**: 仅当项目 < 3 个功能点(< 3 BL)时考虑用维度结构(避免 1-2 张卡片就 N 个附录)。本节默认按功能点,旧式维度剖切**已废弃**,不再推荐

   - **附录内容(6 个,跨功能视角)**:
     - **附录 A 状态机总图**: Mermaid 状态图 + 状态转移条件总表(整合所有 BL 的状态变化)
     - **附录 B 角色 × 权限点矩阵**: 表格(角色 × 权限点,行=角色,列=权限点,值=✅/❌)
     - **附录 C 数据埋点全表**: 整合所有 BL 卡片 §N.11 涉及的埋点,加全局索引
     - **附录 D 原型截图引用**: 设计稿截图清单,每张标注源 HTML
     - **附录 E 关键决策点对比**(可选): 本版本 1-N 个关键决策点的"3 方案对比 + 选中方案 + 选中理由"
     - **附录 F 与上一版本差异清单**: 本版 vs 上一版的所有变化(行为/字段/索引/接口/枚举)

   - **本卡片 7 大核心内容**:
     - **业务逻辑**:每个功能的完整业务规则,包含所有分支条件、边界情况、异常路径
     - **操作流程**:每个用户操作的主流程 + 替代流程 + 异常流程
       - **流程图 (Mermaid 优先 + 文字双轨)**: 如流程复杂, 用 ```mermaid 块绘制. 格式示例:
         ```mermaid
         flowchart TD
           A[用户操作] --> B{条件判断}
           B -->|满足| C[正常流程]
           B -->|不满足| D[替代流程]
           C --> E[异常处理]
         ```
       - **🚨 Mermaid 双轨兜底(强同步)**: Mermaid 块在 Word/Notion/飞书云文档等场景可能不渲染(后续 `hlprd` 转 docx 时尤为关键)。**Mermaid 块 + 文字版流程描述必须同时存在**,**缺一不可**:
         1. **Mermaid 块**: 图形化流程(主路径)
         2. **文字版主/替代/异常三路径**(`### 主流程` / `### 替代流程` / `### 异常流程` 3 段,每段列步骤要点)
         3. 评审基线: Mermaid 块与文字版必须描述同一流程,**互相校验**——任一缺失 → 评审不通过
       - 缺流程图(双轨) → 标 🔴 + 评审驳回
     - **数据流转**:字段级定义(字段名/类型/必填/校验规则/默认值/示例值)
     - **状态机**:核心实体(订单/用户/任务等)的完整状态流转图
     - **权限规则**:每个功能/页面的访问权限(游客/登录用户/管理员等)
     - **非功能需求**:性能指标(响应时间/QPS)、安全要求、兼容性要求
     - **数据埋点需求**: 业务方/运营需要观测的"用户行为/系统事件"埋点设计
       - 必含字段: 埋点事件 ID / 事件名称 / 触发时机(按钮点击/页面曝光/接口调用/异常) / 上报参数(用户 ID/业务 ID/设备信息) / 上报位置(前端/后端) / 采样率(100% 关键 / 1% 普通)
       - 格式: 表格列出, 每条埋点 1 行 (ID / 名称 / 触发 / 属性)
     - **缺失警告**: PRD 没埋点段, 运营/产品上线后看不到用户行为数据, **技术评审会不通过**
   - **🚨 原型截图引用(可选但推荐)**: 跨功能场景的截图全表在 **附录 D**,每个 BL 卡片里**不重复**截图,只写"本功能涉及的截图引用(链接到附录 D 条目)"。格式:
     ```markdown
     ### N.16 原型截图(本功能)
     - 弹窗: 详见 附录 D · {条目}
     - 操作列对比: 详见 附录 D · {条目}
     ```
     **规则**:
     1. **路径相对于 PRD 所在目录** (`docs/v{N}/`), 用相对路径 (例: `design/list-page.png`)
     2. **每张截图必须标注源 HTML** (`*.html`),评审人可点击看交互/动效
     3. **截图来源**: 步骤 6b.5 设计稿截图产物 (`screenshot[-N].png`) — 不重复截图,直接引用
     4. **不可用时**: 标 "🚧 暂无原型截图" + 链接到 `docs/v{N}/design/*.html` 源文件占位
     5. **跳过条件**: 本次需求 0.5 步选"不涉及设计" → 附录 D 整段不写(纯后端 PRD 不需要 UI 截图)
   - **不确定就问**:任何业务逻辑、数据规则、流程细节有不确定的地方,立即向用户提问
   - **禁止模糊字眼**:PRD 中不得出现"暂定""待确认""或""等"
   - **🚨 模糊字眼 grep 自检(硬性)**: 步骤 4 写完后, 主 agent 执行:
     ```bash
     grep -nE "暂定|待确认|或者|大致|大概|类似|TBD|TODO|FIXME|XXX|…$|等$" docs/{ver}/prd.md
     ```
     命中任意行 → 警告 + 标记 🔴 + 阻塞进入步骤 5 PRD 评审,必须替换为具体值或问用户。
     豁免清单(允许出现): "等"作为"等等"语气的引号内文字 / "TBD"在显式标注的"待办"段中(且附 owner + 截止日期) / "类似"作为对比描述(如"类似 bulk insert")

5. **★ PRD 评审会签**（重量评审 1/3，阻塞点,仅"分阶段评审"模式执行）
   - **触发条件**:仅当 0.5 步骤评审模式选 A "分阶段评审" 时执行本步骤
   - **跳过条件**:选 B "集中评审" 时,本步骤+步骤 7+步骤 9 全部跳过,跳到步骤 9a"集中评审"
   - 参与方：`analyst` 主持 + `architect` + `executor` + `designer` + `test-engineer`
   - 评审基线：PRD v(latest)
   - 各角色各自输出评审意见（**通过 / 有保留 / 反对**）
   - **⚠️ 会签机制(诚实声明)**: 5 方会签由**同一 LLM 按角色顺序扮演**(非真·多 agent 进程对抗)。详见上方 §诚实声明段。
   - **不通过 → 返回步骤 4 → 输出 PRD v(N+1) → 触发【强同步规则】**
   - **3 轮上限**：同一项评审最多驳回 3 轮，超出升级用户决策

   **【v5 强同步规则 - PRD 评审驳回时】**
   PRD 重写后不仅需重走步骤 5 自身（直到通过），还必须：
   - 在设计稿（步骤 6b）相应位置同步修改
   - 在测试用例（步骤 8）相应位置同步修改
   - 重走步骤 7 设计评审 + 步骤 9 用例评审
   - **即便设计/用例原本已通过，也必须重走（不能豁免）**

### 第二阶段：设计阶段（v11 条件性执行:仅当 0.5 步骤选"涉及设计"时执行）

> **条件触发**:0.5 步骤问题 2 选 A "涉及 UI/交互/页面/视觉变化" 才执行本阶段
> **跳过条件**:0.5 步骤问题 2 选 B "不涉及(纯后端/数据/接口/状态机/规则/算法)" → 整个第二阶段直接跳过,跳到步骤 8 用例编写
> **本阶段产出**:仅是"设计稿 + 设计评审";不写产品代码,不调接口,不建数据库

6a.0 **设计需求确认**(执行本阶段前先问)
- 如未在 0.5 步骤明确,此处再问一次:本次是否涉及 UI 变化?
- 选 "不涉及" → 跳到步骤 8(本阶段 6a.1/6a.2/6b/7 全部跳过)
- 选 "涉及" → 继续

6a.1 **★ 设计规范检查**（阻塞点"硬性约束"）
   - 读取项目目录，自动检查是否存在设计规范：
     - 检查路径（按优先级）：
       1. `docs/design/spec.md`
       2. `docs/design/SKILL.md`
       3. `docs/design/` 目录下任意 `.md` 文件
       4. 项目根目录 `DESIGN.md`
   - 找到 → **🚨 硬性约束**：字体/色彩/间距/圆角/阴影/组件样式/动效基调 **一律按规范**，**严禁偏离**：
     - 任何字段值（颜色 hex/字号 px/间距值）必须与规范**字面一致**
     - 如发现"规范中无此场景"→ 标记 `🔴 规范缺口` + 暂停设计 + 询问用户
     - 严禁"参考规范"自行发挥（哪怕只是改了一个圆角值）
   - 未找到 → 输出"未发现设计规范"报告，继续 6a.2
   - 【阻塞点】：必须执行目录扫描 + 输出检查报告，无论是否找到
   - 找到规范后，designer 需在设计前输出**规范遵循清单**：
     - [ ] 字体（标题/正文/代码字号字重行高）
     - [ ] 色彩（主色/辅色/强调色/中性色 + 亮/暗双套）
     - [ ] 间距系统（基础单位 + xs/sm/md/lg/xl 各级）
     - [ ] 圆角与阴影（按钮/卡片/弹窗分级）
     - [ ] 核心组件（按钮 4 态、输入框 4 态、标签/徽章/头像）
     - [ ] 动效基调（hover/过渡/缓动曲线）
   - **：设计稿内必须显式引用规范条款**
     - 形式:在 HTML/CSS 注释中标注 `/* 规范: docs/design/spec.md §3.2 圆角值 */`
     - 便于设计评审时核对每条设计决策的规范依据

6a.2 **★ 设计保真度咨询**（阻塞点）
   - 用 `AskUserQuestion` 问用户选哪一档：
     - **低保真原型**（线框图 / 灰度布局 / 基础组件，适合内部评审、流程对齐）
     - **中保真 HTML 原型**（默认推荐：色彩 + 真实组件 + 完整交互 + 真实示例数据）
     - **高保真 HTML 原型**（像素级还原 + 全部状态 + 动画 + 真实数据，适合用户验收/对外演示）
     - **🆕 已有页面高保真 + 逻辑说明 demo**（**6a.0 已选"已有页面微调"时推荐**:基于原页面源码做高保真修改 + 每个交互元素挂 `data-prd` 等属性 + 点击 🔗 弹侧边栏显示 PRD/用例/状态机/矩阵片段。纯静态 HTML,双击即开,适合"在已有页面加东西"的场景把设计稿作为可点开的活文档交付）
   - 【阻塞点】：未询问用户不得进入 6b 设计
   - **保真度一经选定，整个项目统一遵循该档**，不可临时升级要求

6b. **UI/UX 设计**（`designer`"已有页面微调"产出规则）
   - 按 6a.1 规范 + 6a.2 保真度产出设计
   - 遵循 hlpm 三步决策（如果 6a.1 未找到规范）：
     1. 检查现有设计规范（已在 6a.1 完成）
     2. 是否先整理设计规范（询问用户：是否调用 `hllegacy` 第 11 步整理）
     3. 是否有参考页面（询问用户）
   - 控件复用：优先使用项目已有的前端组件库
   - 风格统一：新设计必须与当前系统风格保持一致
   - 架构统一：遵循项目已有的前端架构模式
   - 与当前系统页面逐项对比（截图对照）：字体/按钮/表格/表单/弹框/间距/分割线/图标
   - **输出基线版本 v1**，登记到 `consistency-rules.md` 的版本基线表

   ---

   ### 🚨 已有页面微调的产出规则(硬性约束）

   > **如果本次需求是"在已有页面上做调整"（如新增按钮 / 改文案 / 调布局），设计稿必须基于原页面 diff，不允许另起炉灶**

   **两种场景区分**（用 `AskUserQuestion` 在 6a.0 步骤确认）：

   | 场景 | 判定 | 设计稿产出 |
   |------|------|----------|
   | **全新页面 / 全新模块** | 无任何已有页面可参考 | 独立设计稿 `docs/{ver}/design/<page-name>.html` |
   | **已有页面微调** | 有 1 个或多个已有页面要改 | **基于原页面 diff 的设计稿**（见下） |

   **"已有页面微调"设计稿产出规则**（v14 强制）：

   1. **必须找到原页面的实现代码**
      - 位置：项目源码目录（如 `src/pages/<page>.vue` / `app/views/<page>.tsx` 等）
      - 找不到 → 标记 `🔴 原页面缺失` + 暂停 + 询问用户

   2. **设计稿必须是原页面的"修改版"**，不是"全新页"
      - **不允许**：复制原页面代码 → 重新设计 → 输出一个长得像但实质是新的 HTML
      - **要求**：以原页面 HTML 为基础，**只标注修改部分**（新增/修改/删除）

   3. **设计稿结构**（必须包含 3 个区块）：

      ```html
      <!-- 区块 1:原页面代码（保留,标注为 diff 基线） -->
      <!-- 规范: docs/design/spec.md §3.2 圆角值 -->
      <div class="page" data-diff-mode="baseline">
        <header>...原页面...</header>
        <main>...原页面...</main>
        <!-- 改动点 A:新增"导出 CSV"按钮 ↓ -->
        <!-- 改动点 B:标题文案调整 ↓ -->
        <!-- 改动点 C:删除"高级筛选"折叠面板 ↓ -->
      </div>

      <!-- 区块 2:diff 标注（必须显式列出每处改动） -->
      <section data-diff-summary>
        <h3>本次改动清单</h3>
        <ul>
          <li>🟢 新增: <code>.page main .toolbar button.export-csv</code> (第 24 行后插入)
             <ul><li>原因:业务方要求导出筛选结果</li>
                 <li>规范引用: <code>docs/design/spec.md §4.1 按钮 4 态</code></li></ul>
          </li>
          <li>🟡 修改: <code>.page main h1</code> 文案 "订单列表" → "订单管理"
             <ul><li>原因:产品改名</li>
                 <li>规范引用: <code>docs/design/spec.md §3.1 标题字号</code></li></ul>
          </li>
          <li>🔴 删除: <code>.page main .advanced-filter</code> 整个折叠面板
             <ul><li>原因:用户调研显示 90% 不用,移到二级页</li>
                 <li>影响范围: PRD 业务规则 R-15 / 测试用例 TC-023</li></ul>
          </li>
        </ul>
      </section>

      <!-- 区块 3:修改后的完整页面（带 diff 标记） -->
      <div class="page" data-diff-mode="modified">
        <!-- ...完整代码,改动处用 class="diff-add" / "diff-mod" / "diff-del" 标记... -->
      </div>
      ```

   4. **diff 标注要求**:
      - 改动点 A (新增): 用 `<ins>` 标签或 `class="diff-add"` 高亮
      - 改动点 B (修改): 用 `<mark>` 标签或 `class="diff-mod"` 高亮
      - 改动点 C (删除): 用 `<del>` 标签或 `class="diff-del"` 加删除线
      - 每个改动点必须写: **原因** + **规范引用** + **影响范围**

   5. **命名约定**:
      - 旧文件原页面:`docs/v{old}/design/<page-name>.html`（如 v0 是首次基线,可能不存在）
      - 新文件本次微调:`docs/{ver}/design/<page-name>.diff.html`（用 `.diff.html` 后缀区分）

   6. **设计评审特别检查**:
      - diff 区块 2 的每条改动**必须有规范引用**（如 `§3.2 圆角值`）
      - 缺规范引用 → 评审不通过,返回 6a.1 补规范检查
      - 改动超出规范范围 → 标记 `🔴 规范缺口` 升级用户

   7. **🚨 设计稿输出后立即执行: 6b.5 截图(hlprd 前置准备)**

      > **触发条件**: 设计稿 HTML 写完后**立即**截图(逻辑上是 6b 的子步骤,不是独立阶段)。
      >
      > **目的**: `hlprd` 生成的"标准交付包 .docx"需嵌入设计稿截图供业务方查看。无截图 = 业务方看不到 UI, 文档价值大降。
      >
      > **执行位置**: 6b 完成后、7 设计评审**之前**。

      - **实现**: `designer` agent 调 `Skill hlbrowse` 打开 `docs/{ver}/design/*.html` (含子目录 components/ 和 flows/), 用 `screenshot` 命令保存为:
        - 单个设计稿: `docs/{ver}/design/screenshot.png`
        - 多个设计稿: `docs/{ver}/design/screenshot-1.png`、`screenshot-2.png`、... `screenshot-N.png`
      - **命名约定**: `screenshot[-N].png` (无 `-N` 后缀 = 第一个)
      - **失败处理**:
        - `hlbrowse` 不可用 → 跳过截图, hlprd 退化为"无图模式"(仍可生成 .docx, 但 UI 部分显示"暂无截图"占位)
        - HTML 渲染失败 → 跳过该文件, 记录到 `docs/{ver}/design/screenshot-errors.log`
      - **不二次截图**: 步骤 7 (设计评审) 通过后不再重新截图。后续 `hlprd` 复用本步产物。
      - **错误用法**: 不要把 6b.5 放到 6b 之前(没设计稿就截图)或 7 之后(评审通过才截图=错过修正时机)。

   ---

   ### 🆕 5 区块扩展（仅当 6a.2 选"高保真 + 逻辑说明 demo"档时强制）

   > **触发条件**：6a.2 选了"已有页面高保真 + 逻辑说明 demo"档位 → 3 区块扩为 5 区块；其他档位维持 3 区块原结构。
   >
   > **目的**：让设计稿成为"活文档"——交付时附带该页面每个交互元素对应的 PRD/测试用例/状态机/一致性矩阵逻辑，**评审人员点右下角悬浮框即可看到该页面所有逻辑上下文**。
   >
   > **🚨 DEV-NOT-FOR-PROD**:区块 1 / 2 / 3.2-3.5 / 4 / 5 全部是**设计稿元信息**,**禁止搬到生产代码**。dev 拿到设计稿**只搬区块 3（含 3.1）整个 DOM** + 关联 CSS（排除 `.logic-*` / `.floating-meta-*` / `[data-prd]` / `[data-tc]` / `[data-state]` / `[data-matrix]` / `.logic-badge` / `#logicPanel` / `#floatingMetaToggle` / `#floatingMetaPanel` / `#logic-data`）。详见顶部 `<-- DEV-NOT-FOR-PROD -->` 注释的搬运白名单。

   #### 输出结构：页面流 + 悬浮框

   - **页面流主体**：**只放区块 3（真实页面）+ 区块 3.1（默认 ACTIVE 状态）**。dev 拿到这个 HTML 时，`<body>` 内除悬浮框外的所有内容都是可搬生产代码。
   - **右下角悬浮框**：所有元信息（区块 1 / 2 / 3.2-3.5 / 4 / 5）收纳到右下角悬浮按钮 + 展开面板。
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

   - `data-prd` / `data-state` / `data-tc` / `data-matrix` 属性仍挂在区块 3 真实元素上(这些属性是元信息载体,生产代码搬时要删,但设计稿生成时不省)
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

   **`verifier` 二次验证**: 步骤 7 设计评审时,`verifier` 用 `hlbrowse` 打开设计稿,**实际点击 1 个角标**(选最大块的 PR-XXX),**必须看到悬浮框展开 + 切到 tab 7 + 对应 logic-item 高亮**。否则评审不通过。

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

   **`verifier` 框架场景二次验证**: 步骤 7 设计评审时,`verifier` 不仅点击角标验证交互,**还必须在控制台跑 `document.querySelectorAll('.logic-badge')[0].onclick !== null || getEventListeners`** 的等价检查(用 `dispatchEvent` 看是否触发)。Vue 场景下还需确认 listener 绑在 `mounted` 后,而不是 Vue 挂载前的同一 DOM 节点。

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

   **`verifier` 必查项**: 步骤 7 设计评审时,`verifier` 点击角标后**必须截图**,**截图里能看到标题栏 + × 按钮**才算通过。看不到 → 评审不通过。

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
     设计与实现分离: 本 HTML = 区块 3 真实页面 + 悬浮框元信息面板
   
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

   **完整示例**:见 `hlpm/examples/order-list-with-export-csv.html`(已重写为悬浮框版本)

   ### 设计稿文件命名规范

   | 场景 | 文件名 | 路径 |
   |------|--------|------|
   | 全新页面 | `<page-name>.html` | `docs/{ver}/design/` |
   | 已有页面微调 | `<page-name>.diff.html` | `docs/{ver}/design/` |
   | 组件级改动 | `<component-name>.html` | `docs/{ver}/design/components/` |
   | 流程图 | `<flow-name>.html` | `docs/{ver}/design/flows/` |

> **设计稿截图(6b.5 子步骤)** 见 6b 段内第 7 小项,不在此处重复。

7. **★ 设计评审会签**（重量评审 2/3，阻塞点,仅"分阶段评审"模式执行）
   - **触发条件**:仅当 0.5 步骤评审模式选 A "分阶段评审" 时执行本步骤
   - **跳过条件**:选 B "集中评审" 时,本步骤跳过,合并到步骤 9a"集中评审"
   - 参与方：`designer` 主持 + `analyst` + `executor` + `architect` + `test-engineer`
   - **⚠️ 会签机制(诚实声明)**: 5 方会签由**同一 LLM 按角色顺序扮演**(非真·多 agent 进程对抗)。详见上方 §诚实声明段。
   - **评审基线**（硬性检查项）：
     - **🚨 规范遵循**：必须与 6a.1 找到的规范**字面一致**（v14 硬性检查项,不可"参考发挥"）
       - 检查方式:每条设计决策的 CSS 值与规范文档 grep 对比
       - 任何字段值偏差（哪怕 1px / 1 颜色）→ 评审不通过
       - 规范缺口（规范中无此场景）→ 必须先补规范,再设计
     - **🚨 diff 完整性**(仅"已有页面微调"场景）：设计稿必须包含 3 个区块 + 每条改动有规范引用 + 改动点用 diff 标记
     - 保真度：以 6a.2 选定的档为基线，不可临时升级要求
     - 内容对齐：与 PRD v(latest) 业务规则一致
   - 不通过 → 返回步骤 6b → 输出设计 v(N+1) → 触发【强同步规则】
   - 3 轮上限：同一项评审最多驳回 3 轮，超出升级用户决策

   **【v5 强同步规则 - 设计评审驳回时】**
   设计重写后不仅需重走步骤 7 自身（直到通过），还必须：
   - 检查 PRD（步骤 4）相应位置是否需要同步（设计变更是否影响业务逻辑）
   - 在测试用例（步骤 8）相应位置同步修改
   - 如 PRD 受影响 → 重走步骤 5 PRD 评审
   - 重走步骤 9 用例评审
   - **即便 PRD/用例原本已通过，也必须重走**

### 第三阶段：测试准备

> **v11 补充**:即使跳过了第二阶段(设计),本阶段仍必须执行
> 测试用例的双源对齐:有设计稿时对齐 PRD+设计;无设计稿时对齐 PRD+技术约束(架构/接口/数据)
> 一致性矩阵在"无设计"场景下自动少 1 列(无"设计页面"列)

#### 无设计场景下,一致性矩阵列定义

| 矩阵 | 完整版列(有设计) | 无设计版列 | 说明 |
| --- | --- | --- | --- |
| 业务规则覆盖矩阵 | PRD 业务规则 / 设计页面 / 测试用例 TC / ✅❌ | **PRD 业务规则 / 测试用例 TC / ✅❌**(省略"设计页面") | 设计列省略,保留业务规则 + 用例双向对照 |
| 状态机覆盖矩阵 | 状态 / 设计状态 / 测试用例 / ✅❌ | **状态 / 测试用例 / ✅❌**(省略"设计状态") | 状态机的视觉呈现通常在设计中,无设计场景不验证视觉状态 |
| 权限覆盖矩阵 | 角色 / 设计权限点 / 用例权限 TC / ✅❌ | **角色 / 用例权限 TC / ✅❌**(省略"设计权限点") | 权限点的 UI 呈现(隐藏/禁用)在无设计场景不可验证 |
| 非功能需求覆盖矩阵(性能/安全/兼容) | PRD 指标 / 设计实现策略 / 测试验证方法 / ✅❌ | **PRD 指标 / 测试验证方法 / ✅❌**(省略"设计实现策略") | UI 实现策略属于视觉决策,无设计场景不适用 |

> 一致性矩阵模板(`consistency-rules.md`)需支持 `{hasDesign}` 标志,**渲染时自动隐藏"设计"列**;无设计场景下,**"设计页面"列的 ✅ 视为永真**(不构成阻塞)。

8. **测试用例编写**（`test-engineer`，含 E2E）
   - 按 **PRD v(latest) + 设计 v(latest) 双源对齐编写**
   - 覆盖：主流程 + 替代流程 + 异常流程
   - 包含：边界值用例、权限分支用例、E2E 场景
   - 用例必须能反推 PRD 验收标准
   - **输出基线版本 v1**，登记到 `consistency-rules.md` 的版本基线表

9. **★ 用例评审会签**（重量评审 3/3，阻塞点,仅"分阶段评审"模式执行）
   - **触发条件**:仅当 0.5 步骤评审模式选 A "分阶段评审" 时执行本步骤
   - **跳过条件**:选 B "集中评审" 时,本步骤跳过,合并到步骤 9a"集中评审"
   - 参与方：`test-engineer` + `analyst` 联合
   - **⚠️ 会签机制(诚实声明)**: 2 方会签由**同一 LLM 按角色顺序扮演**(非真·多 agent 进程对抗)。详见上方 §诚实声明段。
   - **评审基线**：
     - 用例 v(latest) + PRD v(latest) + 设计 v(latest) 三方对齐
     - 业务规则 / 状态机 / 权限 三个维度均覆盖
   - 不通过 → 返回步骤 8 → 输出用例 v(N+1) → 触发【强同步规则】
   - 3 轮上限

   **【v5 强同步规则 - 用例评审驳回时】**
   用例重写后不仅需重走步骤 9 自身（直到通过），还必须：
   - 反查 PRD（步骤 4）验收标准是否与新用例匹配
   - 反查设计（步骤 6b）交互流程是否覆盖新用例
   - 如 PRD/设计受影响 → 重走步骤 5 PRD 评审 + 步骤 7 设计评审
   - **即便 PRD/设计原本已通过，也必须重走**

### 第三阶段.5:集中评审(仅"集中评审"模式)

9a. **★ 集中评审**(阻塞点,**仅当 0.5 评审模式选 B"集中评审"时执行**)
   - **触发条件**:0.5 步骤评审模式选 B "集中评审"
   - **跳过条件**:选 A "分阶段评审"时,本步骤跳过,中间 3 场独立评审已执行
   - **位置**:在步骤 8 用例编写完成后,步骤 9.5 一致性终检之前
   - **参与方**(5 角色全部参与, 与分阶段评审相同):
     - `analyst` 主持(产品维度)
     - `architect`(技术可行性 / 根因风险)
     - `designer`(规范遵循 / 视觉一致性)
     - `executor`(实现工作量 / 复用评估)
     - `test-engineer`(测试覆盖 / 边界条件)
   - **⚠️ 会签机制(诚实声明)**: 5 方会签由**同一 LLM 按角色顺序扮演**(非真·多 agent 进程对抗),意见多样性受同质化/单一温度/上下文共享限制。详见上方 §诚实声明段。
   - **白话描述**: PRD + 设计 + 用例**全部写完后**开 1 场集中评审会, 5 角色同时在场. 速度快于"分阶段评审"(不开 3 次), 但**保持 5 角色交叉审视**(不是"3 角色自查"——后者会让 architect/executor 视角缺失, 退化为低质量评审)
   - **评审内容**(一次性覆盖 PRD/设计/用例 三方):
     1. **PRD 评审**:`analyst` 主审 6 大模块(业务/操作/数据/状态机/权限/非功能); `architect` / `executor` 补充"技术不可行"或"工作量翻倍"意见
     2. **设计评审**:`designer` 主审 6a.1 规范遵循 + 6a.2 保真度对齐; `executor` 补充"组件复用 / 现有架构集成"; `test-engineer` 补充"交互状态覆盖"
     3. **用例评审**:`test-engineer` 主审 三方对齐 + 三维覆盖(业务规则/状态机/权限); `analyst` 补充"用户场景完整性"; `architect` 补充"边界条件"
   - **评审基线**:PRD v(latest) + 设计 v(latest)(条件) + 用例 v(latest)
   - **不通过处理**(强同步规则):
     - 驳回 → 修改对应文档 → 在本场集中评审中**整体重审** 1 次
     - 1 轮不通过 → 升级为"分阶段评审"模式(再走完整 3 场)
     - 避免:1 场内多次反复修改再重审(降低效率)
   - **通过后**:进入 9.5 一致性终检(规则不变)
   - **3 轮上限**:同一份交付物,集中评审最多驳回 3 轮,超出升级用户决策

### 第四阶段：交付前终检

9.5. **★ 三项一致性终检**(阻塞点）
   - 在所有评审通过后、进入交付前执行
   - **Agent 分工**：
     - `analyst`（只读）**提取要素**：从 PRD/设计/用例三方抽取业务规则、状态机、权限点、非功能指标
     - `analyst` **生成初稿**：输出"一致性矩阵"内容（按 `consistency-rules.md` 模板）
     - 写入文件由主 agent/调用方负责
     - `verifier`（只读）**验证一致性**：交叉比对三方覆盖情况，出具 ✅/❌ 判定
   - **提取范围**（与第 4 矩阵字段逐字对齐）：
     - PRD：业务规则 + 状态机分支 + 验收条件 + 非功能指标（**性能 / 安全 / 兼容**三类分别列）
     - 设计：页面 + 状态 + 交互流程 + 非功能 UI 实现策略（**性能 / 安全 / 兼容**三类分别列）
     - 用例：前置条件 + 步骤 + 预期结果 + 非功能验证方法（**性能 / 安全 / 兼容**三类分别列）
   - **三类非功能需求定义**：
     - **性能**：QPS / 响应时间 / FPS / 并发数
     - **安全**：加密 / 鉴权 / 脱敏 / 注入防护
     - **兼容**：浏览器 / 设备 / 系统版本
   - **非功能需求 owner 角色分配**（避免"谁都该写但谁都不写"）：
     | 非功能类型 | 推荐 owner | 必备字段 | 阶段 |
     | --- | --- | --- | --- |
     | 性能 | `architect`(后端)/ `executor`(前端) | P50/P95/P99 响应时间, QPS, FPS, 并发数, 资源占用 | PRD §非功能 |
     | 安全 | `security-reviewer` 或 `architect` | 鉴权方式, 数据脱敏, 注入防护(XSS/SQL/命令), 审计日志 | PRD §非功能 + 用例 §安全 TC |
     | 兼容 | `executor`(前) | 浏览器矩阵(Chrome/Safari/Firefox/Edge 版本), 设备(iOS/Android), 系统版本下限 | PRD §非功能 + 设计 §兼容状态 |
     - 缺 owner = 一致性矩阵该项标 🔴 + 阻塞 9.5 通过
   - 三方交叉比对：每个 PRD 业务规则 → 必须有对应设计页面 + 对应用例
   - **输出【一致性矩阵】**（按 `consistency-rules.md` 模板）：
     - 业务规则覆盖矩阵
     - 状态机覆盖矩阵
     - 权限覆盖矩阵
     - 非功能需求覆盖矩阵（性能 / 安全 / 兼容性）
     - 不一致清单
   - 不一致 → 返回对应步骤（4 / 6b / 8）修改 → 触发强同步 → **重走后续所有评审**（强同步规则：不可豁免已通过的评审）
   - 9.5 返回后路径示例：
     - 不一致项在 PRD → 返回 4 → PRD 评审（5）必须重走 + 设计评审（7）必须重走 + 用例评审（9）必须重走
     - 不一致项在设计 → 返回 6b → 设计评审（7）必须重走 + 用例评审（9）必须重走
     - 不一致项在用例 → 返回 8 → 用例评审（9）必须重走
   - 【阻塞点】：一致性矩阵未生成 + 全部 ✅ 通过 → 禁入步骤 10

10. **验收标准与非功能需求打包**（`analyst` + `test-engineer` 生成 → 写入文件）
    - 验收标准：从 PRD 业务规则 + 用例反推的可验证条款
    - 非功能需求：性能 QPS/响应时间、安全、兼容性
    - 与一致性矩阵对齐

11. **交付物自检**（`analyst` 用 `handoff-package.md` 逐项核对 → 输出自检报告）
    - 8 项产品交付物逐项勾选自检清单(6 必出项必须齐全;竞品/设计稿按本次是否适用勾选或标"不适用")
    - 一致性矩阵存在且勾选完整
    - 三项版本号匹配（PRD vX = 设计 vX = 用例 vX）
    - **自检报告落盘**：写入 `docs/{ver}/handoff-self-check.md`（与 `handoff-package.md` 配套，供开发段参考）
    - `analyst` 生成自检报告内容 → 主 agent/调用方写入文件

12. **打包交付**
    - 输出 8 项交付物到版本目录 `docs/vN/`（其中竞品分析、设计稿为条件出,其余 6 项必出;含一致性矩阵与自检报告）：
      1. 竞品分析报告（条件出:新项目/品类调研时，路径 `docs/{ver}/analysis/`）
      2. PRD（含版本号）
      3. 设计稿（条件出:涉及 UI 时，含版本号）
      4. 测试用例（含版本号）
      5. 验收标准
      6. 非功能需求
      7. 一致性矩阵
      8. **自检报告**(`docs/{ver}/handoff-self-check.md`，步骤 11 输出，供开发段步骤 0 验证）
    - 通知开发接手（`hldev` 步骤 0）

---

## 硬性关卡汇总

| 步骤 | 关卡 | 触发后果 |
|------|------|---------|
| 2a | 未询问参考竞品 | 禁入 2b/2c |
| 5 | PRD 评审未会签通过 | 禁入下一步(涉及设计→禁入 6a.1;不涉及设计→禁入步骤 8) |
| 6a.1 | 未执行目录扫描 + 输出检查报告 | 禁入 6a.2 |
| 6a.2 | 未询问保真度 | 禁入 6b |
| 6b | 找到规范后未严格遵循 | 设计稿需重做(v14 硬性:字面一致) |
| 6b | 已有页面微调未基于原页面 diff | 设计稿需重做(v14 硬性:必须含 3 区块) |
| 6b | diff 缺规范引用 | 评审不通过,返回 6a.1 补规范检查 |
| 7 | 设计评审未会签通过 | 禁入 8 |
| 9 | 用例评审未会签通过(分阶段评审模式) | 禁入 9.5 |
| 9a | 集中评审未通过(集中评审模式) | 禁入 9.5,1 轮不通过升级为分阶段评审 |
| 9.5 | 一致性矩阵未生成 + 全部 ✅ | 禁入 10 |
| 任一驳回 | 回退修改未重走后续评审 | 强同步失败，禁入下一阶段 |

---

## 交付文档清单（产品段 8 项）

| # | 文档 | 路径 | 负责 Agent | 步骤 |
|---|------|------|-----------|------|
| 1 | 竞品分析报告 | `docs/{ver}/analysis/competitive-analysis.md` | `analyst` 生成 → 写入文件 | 2b/2c |
| 2 | PRD 文档 | `docs/{ver}/prd.md` | `analyst` 生成 → 写入文件 | 4 |
| 3 | 设计稿 | `docs/{ver}/design/*.html` | `designer` | 6b |
| 4 | 测试用例 | `docs/{ver}/test-cases.md` | `test-engineer` | 8 |
| 5 | 验收标准 | `docs/{ver}/acceptance-criteria.md` | `analyst` 生成 → 写入文件 | 10 |
| 6 | 非功能需求 | `docs/{ver}/non-functional-requirements.md` | `analyst` 生成 → 写入文件 | 10 |
| 7 | 一致性矩阵 | `docs/{ver}/consistency-matrix.md` | `analyst` 生成 + `verifier` 验证 | 9.5 |
| 8 | **自检报告** | `docs/{ver}/handoff-self-check.md` | **`analyst` 生成 → 写入文件** | **11** |

> **`{ver}` = 0.6 步骤决定的当前版本号**(如 `v1` / `v2` / `v3`)

---

## 变更传播规则

当用户在"确认设计"或后续阶段提出修改时，**所有关联文档必须同步更新**：
- PRD 变更 → 设计稿 + 测试用例 + 一致性矩阵同步更新
- 设计稿变更 → PRD（如果影响业务逻辑）+ 测试用例 + 一致性矩阵同步更新
- 测试用例变更 → PRD（反查验收标准）+ 设计稿（反查交互流程）+ 一致性矩阵同步更新
- 任一变更 → 触发【强同步规则】，重走后续所有评审

产品经理（`analyst`）负责追踪，确保所有文档一致性。

---

## 与 hl-flow 的关系

| 维度 | hl-flow | hlpm + hldev |
|------|---------------|------------------------|
| 适用场景 | 单人 / 小团队（一人跑完全流程） | 多人协作（产品 + 开发两角色分工） |
| 评审机制 | 内部评审，analyst 汇总 | 重量评审 3 场独立会签 |
| 一致性 | 无显式机制 | 强同步 + 一致性矩阵（v5） |
| 交接 | 无显式交接 | 8 项产品交付物 + 一致性矩阵打包 |
| 拒收 | 无 | 开发可拒收 + 拒收原因 |

**hl-flow 与 hlpm + hldev 二选一**: 团队只有 1 人 → 走 hl-flow(28 步单人);有产品+开发分工 → 走 hlpm + hldev(23+15 步多角色)。两者**不叠加**, 选其一即可。

---

## 不在本技能范围

> **本技能明确不做以下事情**,如需请调用对应技能:

- ❌ **任何源代码的修改**（.ts/.js/.py/.java/.go/.vue/.tsx/.jsx/...）—— 改代码请用 `hldev`
- ❌ **数据库迁移、部署、CI/CD 配置** —— 用 `hldev` / `hldb` / `hldeploy`
- ❌ **依赖安装、构建、跑测试** —— 用 `hldev`
- ❌ **真实代码评审、安全扫描** —— 用 `hldev` 步骤 5/9
- ❌ **git 提交、PR 推送、tag 发布** —— 用 `hldev` 步骤 8/14
- ❌ **跨会话的"产品 AI + 开发 AI"自动协作**（本期不实现编排器）
- ❌ **历史版本回溯**（v5 不维护版本历史，只看当前最新）
- ❌ **自动会签工具实现**
- ❌ **自动 diff 检测**（一致性靠人工+矩阵保证）

### 本技能产出的 8 类文档清单（配套给 `hldev` 步骤 0 验证）

| # | 文档 | 路径 | 必出/条件 | 步骤 |
|---|------|------|-----------|------|
| 1 | 竞品分析报告 | `docs/{ver}/analysis/competitive-analysis.md` | 条件 | 2b/2c |
| 2 | PRD 文档 | `docs/{ver}/prd.md` | **必出** | 4 |
| 3 | 设计稿 | `docs/{ver}/design/*.html` | 条件(0.5 选涉及) | 6b |
| 4 | 测试用例 | `docs/{ver}/test-cases.md` | **必出** | 8 |
| 5 | 验收标准 | `docs/{ver}/acceptance-criteria.md` | **必出** | 10 |
| 6 | 非功能需求 | `docs/{ver}/non-functional-requirements.md` | **必出** | 10 |
| 7 | 一致性矩阵 | `docs/{ver}/consistency-matrix.md` | **必出** | 9.5 |
| 8 | 自检报告 | `docs/{ver}/handoff-self-check.md` | **必出** | 11 |

> **`{ver}` = 0.6 步骤决定的当前版本号**(如 `v1` / `v2` / `v3`)

**交接给 `hldev` 的 8 项交付物(6 必出 + 2 条件出)**:
- 6 项必出: PRD / 测试用例 / 验收标准 / 非功能需求 / 一致性矩阵 / 自检报告
- 2 项条件出: 竞品分析报告(新项目/品类调研时)/ 设计稿(0.5 选涉及 UI 时)

---

## 交接段

> 本技能被 `hlchain` 编排为"全流程第 1 阶段"。完成本技能后, Agent 应:
>
> 1. 验证 `docs/vN/` 目录存在 + 8 项交付物中的必出项文件非空(6 必出;竞品/设计稿按条件)
> 2. 询问用户: "产品段完成, 是否进入开发段 (hldev)?"
> 3. 用户确认后, 调 `Skill hldev "开始开发 docs/vN/ 里的 8 项交付物"` 进入下一阶段
>
> 4. (可选) 如用户需要在交付开发前**先给业务方签字**, 调 `Skill hlprd "为 <项目名> 合成 v{N} 签字包"` 生成 `docs/vN/sign-off-package.docx`. 用户带着 .docx 找业务方签字. 业务方签后再回 hlchain 继续 (本步骤插入 hlpm 与 hldev 之间, 不影响 hldev 本身).
>
> 如果用户是**单独调用本技能** (不通过 hlchain), 此交接段不触发, 由用户决定下一步。
