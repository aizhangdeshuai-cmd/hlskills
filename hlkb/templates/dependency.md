# 第三方依赖模板

> 复制本文件, 重命名为 `README.md` 放到 `.hl/knowledge/dependencies/`

## 依赖总览(按项目分类)

### 前端 (report-admin-ui/package.json)

| 依赖名 | 版本 | 用途 | 许可证 | 引入版本 | 升级计划 |
|---|---|---|---|---|---|
| `vue` | 2.7.x | 前端框架 | MIT | v1 | v3 评估 Vue 3 升级 |
| `vue-router` | 3.x | 路由 | MIT | v1 | - |
| `vuex` | 3.x | 状态管理 | MIT | v1 | v3 评估 Pinia |
| `element-ui` | 2.15.x | UI 组件库 | MIT | v1 | (与 Vue 2 绑定) |
| `axios` | 0.27.x | HTTP 客户端 | MIT | v1 | - |

### 后端 (ehr-report/pom.xml)

| 依赖名 | 版本 | 用途 | 许可证 | 引入版本 | 升级计划 |
|---|---|---|---|---|---|
| `spring-boot-starter-web` | 2.7.x | Web 框架 | Apache 2.0 | v1 | - |
| `spring-boot-starter-security` | 2.7.x | 安全框架 | Apache 2.0 | v1 | - |
| `mybatis-plus` | 3.5.x | ORM | Apache 2.0 | v1 | - |
| `mysql-connector-j` | 8.0.x | MySQL 驱动 | GPL | v1 | (需注意许可证) |
| `pagehelper` | 1.4.x | 分页插件 | MIT | v1 | - |

### 测试

| 依赖名 | 版本 | 用途 | 许可证 | 引入版本 |
|---|---|---|---|---|
| `junit-jupiter` | 5.x | 单元测试 | EPL 2.0 | v1 |
| `mockito` | 4.x | Mock 框架 | MIT | v1 |
| `@vue/test-utils` | 2.x | Vue 单元测试 | MIT | v1 |

## 依赖升级策略

### 升级前必看

1. 查阅依赖的 [changelog / release notes]({链接})
2. 检查升级是否涉及 breaking change
3. 在测试环境跑全量回归

### 升级流程

1. 升级 `package.json` / `pom.xml` 版本号
2. 跑测试(`npm run test` / `mvn test`)
3. 跑 lint(`npm run lint` / `mvn checkstyle:check`)
4. 跑 e2e(E2E 测试覆盖)
5. **更新本知识库表格**(新增列 `升级到 {新版本}, {日期}, {变更摘要}`)
6. **同 commit 提交代码 + 知识库条目**(仓库即文档)

### 重大升级(vue 2 → vue 3 等)

- 必须有 ADR(`.hl/knowledge/adr/{NNNN}-{slug}.md`)
- 必须有迁移脚本(代码自动迁移 + 手动兜底)
- 必须有完整回归测试
- 一次 commit 升级一个依赖,**避免**批量升级多依赖导致问题难定位

## 依赖安全审计

### 周期

- 每季度一次(`npm audit` + `mvn dependency-check:check`)
- 高危漏洞(CVSS >= 7.0) **立即升级**, 不等季度

### 流程

1. `npm audit` 或 `mvn dependency-check:check`
2. 筛选中/高危漏洞
3. 评估影响(是否有 breaking change / 是否直接升级可解决)
4. **升级 + 测试 + 回归** (见"升级流程")
5. **更新本知识库 + ADR**(如重大变动)

## 许可证清单

| 许可证 | 含义 | 本项目使用情况 |
|---|---|---|
| MIT | 允许商用 / 修改 / 分发 | 主流 |
| Apache 2.0 | 比 MIT 多专利授权 | 主流 |
| GPL | 强 copyleft, 商用受限 | MySQL 驱动(注意) |

## 关联

- API 接口: `.hl/knowledge/api/`
- 环境变量: `.hl/knowledge/env-vars/`
- 技术栈: 项目根 `CLAUDE.md` §技术栈