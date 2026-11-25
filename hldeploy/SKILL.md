---
name: hldeploy
description: 部署规范，覆盖CI/CD流水线（lint→typecheck→test→build→deploy）、部署策略（滚动/蓝绿/金丝雀）、Docker多阶段构建、健康检查（/health+/health/detail）、部署后金丝雀监控（控制台错误/性能回归/页面故障检测）、回滚策略（少于5分钟）。Use when 用户需要 CI/CD 部署或发布后金丝雀监控时调用。
---

# 部署规范

> ## ⚠️ 能力边界声明
>
> 本技能"硬性关卡/强同步/会签"是**文档纪律**,靠 Agent 自觉 + 用户手动打断,**非** Claude Code runtime 强制(漏一步不自动阻断;Agent 模型弱或 prompt 冲突时关卡可能失效,需手动打断重读)。详见 `README.md` 「⚠️ 能力边界声明」。

## 接收发布版本

从 [hlrelease](../hlrelease/SKILL.md) 或项目现行发布系统取得远端、标签、完整提交、必需 CI、发布任务结果与构建产物标识。在部署前以对应远端核对标签解引用到的 SHA，确认镜像摘要／软件包就是该次成功发布的产物；仅有本地标签或候选分支时返回发布段。重部署历史版本沿用该版本的发布记录。只对已获授权的环境和产物执行操作。

## 通用纪律

🚨 **部署前用户确认（硬性关卡）**
- CI/CD 流水线（lint→typecheck→test→build）可自动执行
- **deploy 步骤前必须等待用户确认**，向用户展示：
  - 部署策略（滚动/蓝绿/金丝雀）
  - 目标环境（staging/production）
  - 当前与上一版本的不可变标识，及发布记录中对应的 SHA
  - 回滚方案
- 用户确认后方可执行部署，**严禁自动部署**

---

## CI/CD 流水线

```
lint → typecheck → test → build → deploy
```
- 任一阶段失败即停止，不继续后续阶段
- 部署前核对既有必需流水线，与发布记录中的 SHA 和产物绑定；按项目约定对目标环境运行部署前检查。

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

## 部署后金丝雀监控

部署前记录当前版本与正常健康响应。纯 API 或 CLI 使用真实接口请求或命令验收及对应运行指标；UI 服务另记录关键页面标志和同环境下的性能基线。部署后在授权的环境执行只读冒烟。将下面的 URL 指向实际服务，把选择器换成能证明核心功能就绪的元素。浏览器使用本库 [hlbrowse](../hlbrowse/SKILL.md) 的依赖与运行环境。

```sh
# HLBROWSE_DIR 为本库 hlbrowse 目录。先设置 HEALTH_URL 和 CANARY_URL。
curl --fail --silent --show-error --max-time 10 "$HEALTH_URL"
python3 "$HLBROWSE_DIR/browse.py" "$CANARY_URL" \
  'visible main' 'console --errors' 'perf' 'responsive knowledge/qa/canary-layout' 'expect-clean'
```

1. 在部署约定的启动窗口内核对 HTTP 状态和响应体的服务状态。遇到重定向、依赖降级或超时，按实际结果记录。
2. 在相同的关键页面核对控制台、三种视口截图和导航耗时。性能告警用项目阈值与部署前基线判断；缺少基线时只报告测量值。
3. 在约定的观察窗口内复查错误率、延迟与核心路径。记录采样时间、版本和异常，达到发布计划的回滚条件时按该计划处理。一次截图或一次成功响应只证明该次采样。

---

## 回滚策略

- 每次部署前记录当前版本号和回滚步骤
- 确保 < 5 分钟可完成回滚
- 数据库迁移必须可回滚（DOWN 脚本已测试）
- 回滚后运行冒烟测试确认服务正常

### 回滚操作

Kubernetes 回滚到上一修订：

```bash
kubectl rollout undo deployment/<service>
```

Compose 沿用部署时的 Docker context、项目名、Compose 文件组合及环境。下例适用于目标服务的 `image` 由项目变量 `API_IMAGE` 提供的项目。按已有部署机制恢复该变量或配置文件中的镜像引用，并同步到持久的部署配置。将 `SERVICE` 设为服务名，将 `PREVIOUS_IMAGE` 设为上一成功发布记录中的完整镜像摘要引用。演练时先运行配置核对部分。

```bash
(
  set -eu -o pipefail
  : "${SERVICE:?请设置目标服务名}" "${PREVIOUS_IMAGE:?请设置镜像名@sha256:摘要}"
  [[ "$PREVIOUS_IMAGE" =~ ^.+@sha256:[0-9a-f]{64}$ ]] || { echo "需要不可变镜像引用" >&2; exit 1; }
  export API_IMAGE="$PREVIOUS_IMAGE"
  resolved=$(docker compose config --format json "$SERVICE" |
    python3 -c 'import json,sys; print(json.load(sys.stdin)["services"][sys.argv[1]]["image"])' "$SERVICE")
  [[ "$resolved" == "$PREVIOUS_IMAGE" ]] || { echo "服务配置仍指向 $resolved" >&2; exit 1; }

  # 在已授权环境执行回滚
  docker compose up -d --no-deps --no-build --wait "$SERVICE"
  expected_id=$(docker image inspect --format '{{.Id}}' "$PREVIOUS_IMAGE")
  containers=$(docker compose ps --all --quiet "$SERVICE")
  [[ -n "$containers" ]] || { echo "没有找到服务容器" >&2; exit 1; }
  while IFS= read -r container; do
    actual=$(docker inspect --format '{{.State.Status}} {{.Image}}' "$container")
    printf '%s %s\n' "$container" "$actual"
    [[ "$actual" == "running $expected_id" ]] || { echo "容器状态或镜像 ID 不符" >&2; exit 1; }
  done <<< "$containers"
)
```

核对副本数与部署计划、服务健康状态和关键路径，记录环境、上一发布摘要、实际容器与冒烟结果。任一步失败时保留失败记录，回滚继续待验。

---

## 关联命令
- `/hlrelease` — 发布流程
- `/hldb` — 数据库迁移规范

---

## 交接段

> 本技能被 `hlchain` 编排为"可选的部署阶段"。完成本技能后, Agent 应:
>
> 1. 核对实际环境上运行的版本或不可变产物标识，与获准发布记录一致。
> 2. 完成发布计划要求的健康检查和观察，保留时间、关键路径结果及回滚点。必需检查未完成时，报告执行中或异常。
> 3. 如线上出现异常, 可调 `Skill hlbug "线上问题排查"` 修复(非必需续接)
>
> 部署是**链路终点**。完成后不再自动调任何技能。
>
> 如果用户是**单独调用本技能**, 此交接段不触发。

---

> **路径规范**：本文件涉及的 `knowledge/` 路径命名遵循 `hlpm/path-conventions.md` 中央规范。
