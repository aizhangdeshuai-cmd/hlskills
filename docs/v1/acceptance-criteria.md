<!-- ⚠️ 演示包 / NOT CURRENT VERSION: 此文件是 hlpm-product 流程的演示样例(演示需求:"为 SKILL.md 加 v13 状态徽章"),业务规则/测试用例/矩阵均为演示虚构,不得引用为真实规则。本仓库当前版本 v15。详情见 ../README.md -->

# 验收标准 - v1(v13 状态徽章)

> 路径: `docs/v1/acceptance-criteria.md`

| # | 标准 | 验证方法 | 关联 PRD |
|---|------|---------|---------|
| AC-1 | SKILL.md 顶部 5 行内出现 1 行徽章 | `head -5 SKILL.md \| grep -E "^\!\["` | BR-3 |
| AC-2 | 徽章含"v13"字样 | `head -5 SKILL.md \| grep "v13"` | BR-1 |
| AC-3 | 徽章含"联合评审"或"3 合 1"字样 | `head -5 SKILL.md \| grep -E "联合评审\|3 合 1"` | BR-2 |
| AC-4 | 离线环境下文字版徽章可读 | 断网后查看文档 | BR-2 异常流程 |
| AC-5 | GitHub 渲染正常 | 推送后查看仓库首页 | 非功能 |
