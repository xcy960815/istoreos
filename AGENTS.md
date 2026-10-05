# AGENTS.md — AI 助手请先读

本仓库是 iStoreOS 官方源的 fork（origin = `xcy960815/istoreos`，upstream = `istoreos/istoreos`），
为 J4125 四口 2.5G 软路由维护裁剪版固件。

**任何改动前必读：[`docs/CUSTOM-TRIMMING.md`](docs/CUSTOM-TRIMMING.md)**，其中记录了：

- 用户 2026-10-05 要求删除的功能清单（Docker/Samba/DDNS/UPnP/linkease 等）及原因——未经用户要求不得加回
- 保留但有"看似无用"嫌疑的服务清单（openclash/tailscale/aria2 等，全部在用）
- 改动纪律：**功能增删只改 `config-custom.seed`，不改源码**；`istoreos-24.10` 分支仅用于 ff-only 同步上游

**了解整个家庭服务器改造计划（为什么这样裁剪、全家设备分工、迁移路线）：读 [`docs/HOME-SERVER-BACKGROUND.md`](docs/HOME-SERVER-BACKGROUND.md)**。

构建与刷机步骤见 [`BUILD-CUSTOM.md`](BUILD-CUSTOM.md)；云端构建走 Actions（手动触发）。
