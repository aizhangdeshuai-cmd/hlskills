---
name: hldeploy
description: 部署规范，覆盖CI/CD流水线（lint→typecheck→test→build→deploy）、部署策略（滚动/蓝绿/金丝雀）、Docker多阶段构建、健康检查（/health+/health/detail）、部署后金丝雀监控（融合 gstack /canary：控制台错误/性能回归/页面故障检测）、回滚策略（<5分钟）。Use when 用户需要 CI/CD 部署或发布后金丝雀监控时调用。
---

# 部署规范

## 通用纪律

🚨 **部署前用户确认（硬性关卡）**
- CI/CD 流水线（lint→typecheck→test→build）可自动执行
- **deploy 步骤前必须等待用户确认**，向用户展示：
  - 部署策略（滚动/蓝绿/金丝雀）
  - 目标环境（staging/production）
  - 当前版本号与上一版本号
  - 回滚方案
- 用户确认后方可执行部署，**严禁自动部署**

---

## CI/CD 流水线

```
lint → typecheck → test → build → deploy
```
- 任一阶段失败即停止，不继续后续阶段
- 每次部署前自动运行完整流水线

---

## 部署策略

| 策略 | 适用场景 | 特点 |
|------|---------|------|
| **滚动更新** | 常规发布 | 逐步替换实例，无额外资源消耗 |
| **蓝绿部署** | 需要瞬时切换/回滚 | 两套环境，切换瞬间完成 |
| **金丝雀发布** | 高风险变更 | 逐步放量，先小比例验证 |

---

## Docker 规范

- 使用**多阶段构建**（multi-stage build）减小镜像体积
- 不在镜像中硬编码密钥，通过环境变量注入
- 使用非 root 用户运行应用
- 基础镜像使用 `alpine` 或 `slim` 版本

---

## 健康检查

每个服务必须提供两个端点：

| 端点 | 用途 | 响应 |
|------|------|------|
| `/health` | 简单探活 | 200 OK |
| `/health/detail` | 依赖可达性 | JSON：各依赖状态 |

**启动顺序**：应用启动 → 健康检查通过 → 开始接收流量

---

## 部署后金丝雀监控（融合 gstack /canary）

部署完成后立即启动监控，验证生产环境健康：

### 监控检查项

| 检查项 | 方法 | 不通过时 |
|------|------|---------|
| **控制台错误** | `$B goto <prod-url> && $B console --errors` | 回滚部署 |
| **页面加载** | `$B goto <prod-url> && $B text` | 检查日志 |
| **关键页面可达** | `$B is visible ".hero-section"` | 回滚部署 |
| **性能回归** | `$B perf` 对比部署前基线 | 性能下降 >20% 触发告警 |
| **响应式布局** | `$B responsive /tmp/canary-layout` | 记录 Bug |
| **API 端点** | `curl -s <prod-url>/health` | 回滚部署 |

### 监控流程

```
1. 部署完成
2. 等待健康检查通过（最长 30s）
3. $B goto <prod-url>          → 冒烟验证
4. $B console --errors         → 收集 JS 错误
5. $B responsive /tmp/canary-* → 三屏布局验证
6. 监控持续 5min，有异常 → 回滚
7. 5min 无异常 → 监控结束，部署成功
```

运行独立金丝雀检查：在终端执行 `Skill gstack canary` 加载 gstack /canary 技能。

---

## 回滚策略

- 每次部署前记录当前版本号和回滚步骤
- 确保 < 5 分钟可完成回滚
- 数据库迁移必须可回滚（DOWN 脚本已测试）
- 回滚后运行冒烟测试确认服务正常

### 回滚操作
```bash
# 回滚到上一版本
kubectl rollout undo deployment/<service>
# 或
docker compose up -d <previous-image>
```

---

## 关联命令
- `/hlrelease` — 发布流程
- `/hldb` — 数据库迁移规范

---

> **路径规范**：本文件涉及的 `docs/` 路径命名遵循 `hlpm-product/path-conventions.md` 中央规范。
