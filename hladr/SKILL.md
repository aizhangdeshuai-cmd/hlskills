---
name: hladr
description: 架构决策记录（ADR）规范，定义何时记录、必填字段、取代与归档规则。Use when 关键技术选型、架构设计决策。通过 /hladr 调用。
---

# 架构决策记录（ADR）

> **🚨 与 hlkb 合并**: hladr 产出的 ADR 文件直接写入项目的 `knowledge/adr/` 目录(不独立存放在 `docs/adr/`)。
> 模板、编号与维护规则详见 [ADR 模板](../hlkb/templates/adr.md) 和项目级 `knowledge/adr/README.md`。

---

## 何时记录 ADR

对以下类型的技术选型必须记录 ADR：
- **框架选择** — 前端框架、后端框架、ORM等
- **库选择** — 第三方库、工具链
- **架构模式** — 微服务/单体、六边形架构、事件驱动等
- **基础设施** — 数据库选型、消息队列、缓存方案
- **关键约定** — API版本策略、鉴权方式、部署策略

项目已有 ADR 目录或格式时沿用项目约定；与本技能默认值冲突时，在首个 ADR 中注明采用的格式及原因。

---

## ADR 格式

文件存放在 `knowledge/adr/`，命名为 `NNNN-<slug>.md`，NNNN 为四位连续编号，永不重置。**格式以 [ADR 模板](../hlkb/templates/adr.md) 为唯一来源**，复制模板后至少保留以下内容：

- 标题：`# {NNNN}. {决策标题}`；
- 状态块：状态（Proposed / Accepted / Deprecated / Superseded by [NNNN]）、日期、决策者；
- 上下文、决策与后果；
- 备选方案：每项写优点、缺点和不选原因；
- 实施细节与关联条目。

---

## 取代规则

当架构决策被新的决策取代时：
- 原 ADR 文件**不删除**，保留历史上下文
- 在原 ADR 状态中写入 `Superseded by [NNNN](NNNN-slug.md)`，链接实际的后继文件
- 新 ADR 引用被取代的 ADR

---

## 关联

- 交付文档清单中包含 ADR 文档
- 写入、归档与检索见 [hlkb](../hlkb/SKILL.md)

---

> **路径规范**：本文件涉及的 `knowledge/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
