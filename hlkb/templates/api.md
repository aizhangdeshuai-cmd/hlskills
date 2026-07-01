# API 接口模板

> 复制本文件, 重命名为 `{module}.md` 放到 `.hl/knowledge/api/`

## 接口总览

| 接口 | Method | URL | 权限点 | 引入版本 | 状态 |
|---|---|---|---|---|---|
| 列出黑名单 | GET | `/blacklist/page` | `blacklist:view` | v2 | ✅ |
| 校验重复 | GET | `/blacklist/check-duplicate` | `blacklist:create` | v2 | ✅ |
| 新增黑名单 | POST | `/blacklist` | `blacklist:create` | v2 | ✅ |
| 导入 Excel | POST | `/blacklist/import` | `blacklist:import` | v2 | ✅ |
| 下载模板 | GET | `/blacklist/template.xlsx` | `blacklist:import` | v2 | ✅ |
| 移除 | POST | `/blacklist/{id}/remove` | `blacklist:remove` | v2 | ✅ |
| **恢复(v3 新增)** | **POST** | **`/blacklist/restore/{id}`** | **`blacklist:restore`** | **v3** | **✅** |

---

## 详细说明

### GET /blacklist/page

- **权限**: `blacklist:view`
- **入参**:
  - `companyId` (long, 必填, 多公司隔离)
  - `status` (string, 选填, ACTIVE/REMOVED/SUPERSEDED, 默认 ACTIVE)
  - `keyword` (string, 选填, 姓名/工号/证件号)
  - `resignedDateStart` (yyyy-MM-dd, 选填)
  - `resignedDateEnd` (yyyy-MM-dd, 选填)
  - `pageNum` (int, 选填, 默认 1)
  - `pageSize` (int, 选填, 默认 20)
  - `sort` (string, 选填, 默认 `created_at`)
  - `order` (enum, 选填, `ascending`/`descending`/null, 默认 `descending`)
- **出参**:
  ```json
  {
    "code": 0,
    "data": {
      "total": 123,
      "list": [
        {
          "id": 1,
          "empNo": "E001",
          "empName": "张三",
          "genderText": "男",
          "resignedCompany": "北京 ABC 科技有限公司",
          "idType": "身份证",
          "idNumber": "110101199001011234",
          "remark": "因严重违规被开除",
          "resignedDate": "2024-12-15",
          "createdByName": "admin",
          "createdAt": "2024-12-16 10:30:00",
          "status": "ACTIVE",
          "source": "MANUAL"
        }
      ]
    }
  }
  ```
- **错误码**:
  - 403 无权限
  - 500 系统错误
- **性能**: P95 < 500ms

---

### POST /blacklist/restore/{id} (v3 新增)

- **权限**: `blacklist:restore`
- **入参**:
  - `id` (long, 路径参数, 必填, REMOVED 记录的 ID)
  - body: `{ "restoredReason": "误操作, 该员工表现良好恢复" }` (长度 1-500)
- **出参**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 1,
      "status": "ACTIVE",
      "mergedSuperseded": null,
      "message": "恢复成功"
    }
  }
  ```
  `mergedSuperseded` 不为 null 时表示合并了同证件号 ACTIVE 记录:
  ```json
  {
    "code": 0,
    "data": {
      "id": 1,
      "status": "ACTIVE",
      "mergedSuperseded": 2,
      "message": "恢复成功, 已合并原活跃记录"
    }
  }
  ```
- **错误码**:
  - 400 恢复原因为空 / 长度超限
  - 403 无权限
  - 404 记录不存在(可能已被物理删除)
  - 409 状态冲突(已被恢复 / 状态非 REMOVED)
  - 500 系统错误(事务 ROLLBACK)
- **性能**: P95 < 300ms
- **事务**: 同事务包含 `supersede` 操作(NFR-D-1 事务原子性)
- **关联**:
  - 业务规则: `docs/v3/prd.md §12 BL-12`
  - ADR: `.hl/knowledge/adr/0001-bl12-restore-strategy.md`
  - 数据库: `.hl/knowledge/db/blacklist.md §恢复流程`

---

## 接口版本历史

| 版本 | 新增/修改/废弃 | 接口 |
|---|---|---|
| v2 | 新增 | GET /blacklist/page, GET /blacklist/check-duplicate, POST /blacklist, POST /blacklist/import, GET /blacklist/template.xlsx, POST /blacklist/{id}/remove |
| v3 | 新增 | POST /blacklist/restore/{id} |

---

## 调用方(外部系统)

| 调用方 | 用途 | 频率 |
|---|---|---|
| `report-admin-ui` (前端 SPA) | HR 管理员操作界面 | 高 |
| `BlacklistSyncService` (上游推送, 未来) | 上游 HR 系统推送 | 待定 |

---

## 安全与权限

- 所有接口需要登录态(Spring Security)
- 后端用 `@PreAuthorize('hasAuthority("blacklist:xxx")')` 兜底
- 前端 `v-if` 隐藏按钮 + 后端 @PreAuthorize 双重防护

---

## 错误码总览

| 错误码 | HTTP | 含义 | 触发场景 |
|---|---|---|---|
| 0 | 200 | 成功 | - |
| 40001 | 400 | 参数错误 | 入参缺失/格式错误/超长 |
| 40301 | 403 | 无权限 | `@PreAuthorize` 拦截 |
| 40401 | 404 | 资源不存在 | ID 不存在(可能已物理删除) |
| 40901 | 409 | 状态冲突 | 恢复时状态已非 REMOVED / 并发冲突 |
| 50001 | 500 | 系统错误 | 事务失败 / DB 异常 |

详见 `.hl/knowledge/error-codes/README.md`