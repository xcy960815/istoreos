# AGENTS.md — AI 助手请先读

本仓库是 iStoreOS 官方源的 fork（origin = `xcy960815/istoreos`，upstream = `istoreos/istoreos`），
为 J4125 四口 2.5G 软路由维护裁剪版固件。

**任何改动前必读：[`docs/CUSTOM-TRIMMING.md`](docs/CUSTOM-TRIMMING.md)**，其中记录了：

- 用户 2026-10-05 要求删除的功能清单（Docker/Samba/UPnP/linkease 等）及原因——未经用户要求不得加回。**2026-10-09 改口：网关必须走公网，DDNS-Go 开箱即有**（OpenWrt 自带 `luci-app-ddns` 与 ddnsto 仍禁止加回），见 `docs/CUSTOM-TRIMMING.md` §十五
- 保留但有"看似无用"嫌疑的服务清单（openclash/tailscale/openlist/**ddns-go** 等，全部在用；Aria2/Transmission 已于 2026-10-10 删除，见 §二十）——注意其中**商店类应用根本不在构建期**，写进 seed 是死行，判"在不在固件里"以 `docs/CUSTOM-TRIMMING.md` §六/§九/§十 为准。**例外：DDNS-Go 已用第七条 feed 烘焙进固件**，不要再写成「刷机后商店装」
- 改动纪律：**功能增删只改 `config-custom.seed`，不改源码**。DDNS-Go 是唯一允许的 feed 例外（六个默认 feed 里没有它，必须在 `feeds.conf.default` 留 `src-git ddnsgo`）；不要借此把整个 app-hub 拉进来。**不要删 `target/linux` 里其他架构**——镜像已是 x86_64，那些目录不进固件，删了会把上游同步搞炸；下一轮 seed 可瘦的 D 档见 `docs/CUSTOM-TRIMMING.md` §十六。`istoreos-24.10` 分支仅用于 ff-only 同步上游（只合并官方修复，不为上游开 PR）
- 上游同步工作流：`git fetch upstream` → `git checkout istoreos-24.10 && git merge --ff-only upstream/istoreos-24.10` → `git checkout custom-24.10 && git rebase istoreos-24.10` → `git push --force-with-lease origin custom-24.10`（命令详见 BUILD-CUSTOM.md）。因 seed 收敛在一个文件，99% 的提交无冲突；符号改名时 `make defconfig` 会静默删掉该行，靠 CI 的 seed 审计（`.github/scripts/seed-audit.sh`）报出已知清单外的未生效行并阻断，再按报告改 seed（改名不改功能，不用记账）。
- PR 纪律：**不为上游原仓库送 PR**。本仓库定位是裁剪版维护 fork，只做需求裁剪与问题修复（如 vlmcsd、缓存死锁），所有改动留在 `custom-24.10` 分支供本地使用。如需贡献给 upstream，请评估是否影响其他设备或需要讨论后再决定。
- 记录纪律：**每次功能增删（改 seed）必须同一提交里更新 `docs/CUSTOM-TRIMMING.md`**，且写两层——①功能视角：变更后设备"不能做什么"（或恢复了什么）＋影响＋替代方案，格式见该文档 §六；②包名明细：按批次列全。不留记录的 seed 变更视同未完成；临时用 iStore 商店装回验证不用记录

**了解整个家庭服务器改造计划（为什么这样裁剪、全家设备分工、迁移路线）：读 [`docs/HOME-SERVER-BACKGROUND.md`](docs/HOME-SERVER-BACKGROUND.md)**。

构建与刷机步骤见 [`BUILD-CUSTOM.md`](BUILD-CUSTOM.md)；云端构建走 Actions（手动触发）。CI 历次失败的原始复盘（run 编号、日志原文）在 [`docs/CI-HISTORY.md`](docs/CI-HISTORY.md)，节号与 CUSTOM-TRIMMING.md 对应；CUSTOM-TRIMMING.md 只留当前有效的结论。

**进度（2026-10-10 晚）**：r10 镜像已成功，**还没刷任何机器**。试刷用 N100 + img（不是 ISO、不是双公头 USB 线），**禁止动 J4125**。快照见 `docs/CUSTOM-TRIMMING.md` 文首「当前进度」。
