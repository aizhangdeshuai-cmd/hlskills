---
name: hlmemory
description: 项目记忆与工作记忆管理，跨会话持久化项目知识（技术栈/架构/约定/决策），防止上下文压缩丢失工作状态。Use when 新会话开始需加载项目上下文、或需要保存当前工作状态防止丢失。通过 /hlmemory 调用。
---

# 项目记忆与工作记忆

> 属于 `hlskills` 技能系统。每次会话自动加载项目上下文，会话结束时保存关键发现。

---

## 目录结构

```
项目根目录/.hl/memory/
├── project.md          # 项目基本信息（名称/目标/干系人/约束）
├── techstack.md        # 技术栈（语言/框架/库/数据库/工具链及版本）
├── architecture.md     # 架构决策（模块划分/数据流/关键ADR）
├── conventions.md      # 约定与规范（Git/API/DB/编码/部署 约定）
├── working.md          # 工作记忆（当前任务/待办/发现/阻塞）
└── agents.md           # Agent 配置（哪个 Agent 负责什么）
```

---

## 会话流程

### 会话开始时

1. Read `.hl/memory/project.md` → 了解项目背景
2. Read `.hl/memory/techstack.md` → 了解技术栈
3. Read `.hl/memory/architecture.md` → 了解架构决策
4. Read `.hl/memory/conventions.md` → 了解约定规范
5. Read `.hl/memory/working.md` → 恢复上次会话的工作状态
6. Read `.hl/memory/agents.md` → 了解当前 Agent 配置

### 会话结束时

1. 如有新发现/决策 → 追加到对应的 memory 文件
2. 更新 `.hl/memory/working.md` → 保存当前进度和待办
3. 如用户明确要求 → `remember` 保存特定内容

---

## 各文件格式

### project.md

```markdown
# 项目记忆

## 基本信息
- 项目名称: xxx
- 项目目标: xxx
- 关键干系人: xxx
- 约束条件: xxx

## 当前阶段
- 阶段: 开发/测试/发布
- 活跃分支: feature/xxx
- 最近里程碑: xxx
```

### techstack.md

```markdown
# 技术栈

## 前端
- 框架: React 18 / Vue 3 / Next.js 14
- UI 库: Ant Design / Element Plus / Tailwind
- 状态管理: Zustand / Pinia

## 后端
- 语言/框架: Go 1.22 / Python 3.12 / Node.js 20
- 数据库: PostgreSQL 16 / MySQL 8 / Redis 7
- ORM: Prisma / GORM / SQLAlchemy

## 基础设施
- 部署: Docker / Kubernetes / Vercel
- CI/CD: GitHub Actions / GitLab CI
- 监控: Sentry / Grafana / Datadog
```

### architecture.md

```markdown
# 架构决策

## 模块划分
- 模块A (目录: src/a/): 职责xxx
- 模块B (目录: src/b/): 职责xxx
- 模块间调用关系: A→B→DB

## 关键ADR
- ADR-0001: 选择 PostgreSQL 而非 MySQL | 理由: JSONB 支持
- ADR-0002: 使用 Redis 缓存 | 理由: 低延迟
- 详见 `docs/adr/NNNN-<slug>.md`（NNNN = 4 位顺序编号）

## 数据流
Client → Nginx → API Gateway → Service → DB/Cache
```

### conventions.md

```markdown
# 约定与规范

## Git
- Conventional Commits: feat/fix/docs/refactor/test/chore
- 分支: feature/* / fix/* / hotfix/* / release/*
- 禁止直接提交 main

## API
- RESTful，URL使用复数名词+kebab-case
- 错误格式: { "error": { "code": "...", "message": "..." } }
- 鉴权: Bearer Token

## 数据库
- 每迁移必须有 UP/DOWN
- 大表变更使用扩展-收缩模式

## 编码
- camelCase 变量/函数, PascalCase 组件
- TypeScript 禁止 any
- 单文件 ≤ 300 行

## 部署
- CI/CD: lint → typecheck → test → build → deploy
- 每服务提供 /health + /health/detail
```

### working.md

```markdown
# 工作记忆

## 当前任务
- 正在做: [任务名称] (FEAT-001)
- 下一步: [任务名称]

## 待办
- [ ] [待完成项]
- [ ] [待完成项]

## 发现
- [关键发现1]
- [关键发现2]

## 阻塞
- [阻塞项] → 等待 xxx
```

---

## 与 hlskills 集成

| 技能 | 如何使用 hlmemory |
|------|-----------------|
| `hlpm` | 会话启动加载项目记忆，决策写入 architecture.md |
| `hlbug` | 修复中发现的技术债写入 working.md |
| `hlrefactor` | 重构决策写入 architecture.md |
| `hlpm` | 分析结论写入 project.md + techstack.md |
| `hllegacy` | 分析结果写入 memory 全部文件 |

---

## 初始设置

首次使用时，创建记忆目录：

```bash
mkdir -p .hl/memory
```

然后按 `hlpm` 流程逐步填充各文件内容。

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
