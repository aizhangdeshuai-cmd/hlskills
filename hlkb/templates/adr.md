# ADR 模板 (Michael Nygard 格式)

> 复制本文件, 重命名为 `{NNNN}-{slug}.md` 放到 `.hl/knowledge/adr/`
> NNNN = 4 位顺序号(如 0001, 0002), 永不重置
> slug = 简短描述, 全小写, 单词用连字符

---

# {NNNN}. {决策标题}

> **状态**: Proposed | Accepted | Deprecated | Superseded by [NNNN]
> **日期**: YYYY-MM-DD
> **决策者**: analyst / architect / designer / executor / test-engineer(集中评审 5 角色)

## 上下文(Context)

我们面临的问题/需求是什么?包括:
- 业务背景
- 技术约束
- 已知的"做这个决策之前"的现状

## 决策(Decision)

我们决定做什么?

**一句话总结**: {这个决策的简短描述}

## 后果(Consequences)

这个决策带来的正面/负面影响:
- ✅ 正面: {好处}
- ❌ 负面: {代价}
- ⚠️ 风险: {潜在风险, 缓解措施}

## 备选方案(Alternatives Considered)

### 方案 A: {名称}

- 描述: {一句话}
- 优点: ...
- 缺点: ...
- **不选原因**: ...

### 方案 B: {名称}

- 描述: ...
- 优点: ...
- 缺点: ...
- **不选原因**: ...

### 方案 C: {名称}(本决策采纳)

- 描述: ...
- 优点: ...
- 缺点: ...
- **选中原因**: ...

## 实施细节(Implementation Details)

具体怎么落地,包括代码示例/SQL/配置变更等。

## 关联(References)

- 业务规则: `docs/v{N}/prd.md §{N}`
- 数据库: `.hl/knowledge/db/{table}.md`
- 状态机: `.hl/knowledge/state-machines/{entity}.md`
- 相关 ADR: `{NNNN}-{slug}.md` (如有)
- 外部链接: (如有)