# AGENTS.md — AI 助手请先读

本仓库是 iStoreOS 官方源的 fork（origin = `xcy960815/istoreos`，upstream = `istoreos/istoreos`），
为 J4125 四口 2.5G 软路由维护裁剪版固件。

**任何改动前必读：[`docs/CUSTOM-TRIMMING.md`](docs/CUSTOM-TRIMMING.md)**，其中记录了：

- 用户 2026-10-05 要求删除的功能清单（Docker/Samba/UPnP/linkease 等）及原因——未经用户要求不得加回。**2026-10-09 改口：网关必须走公网，DDNS-Go 开箱即有**（OpenWrt 自带 `luci-app-ddns` 与 ddnsto 仍禁止加回），见 `docs/CUSTOM-TRIMMING.md` §十五
- 保留但有"看似无用"嫌疑的服务清单（openclash/tailscale/openlist/**ddns-go** 等，全部在用；Aria2/Transmission 已于 2026-10-10 删除，见 §二十）——注意其中**商店类应用根本不在构建期**，写进 seed 是死行，判"在不在固件里"以 `docs/CUSTOM-TRIMMING.md` §六/§九/§十 为准。**例外：DDNS-Go 已用第七条 feed 烘焙进固件**；**Tailscale 守护进程+LuCI 已烘焙（官方 1.104.1 amd64 预编译，r17 已有，见 §二十二）**。**QuickStart 首页已烘焙（r22 起有初版；r33 为 N100 已验证版：存储服务只留 WebDAV、家长控制常显、侧栏无 RAID/SMART、首页磁盘信息正常；r38 起流量图改 SSE ~1Hz，§二十三/§三十五/§四十），r17 还是 Argon 概览，不要写成「r17 开箱即有」**
- 改动纪律：**功能增删只改 `config-custom.seed`，不改源码**。允许的 feed/构建例外只有五条：① `feeds.conf.default` 的 `src-git ddnsgo`；② `.github/scripts/pin-tailscale-prebuilt.sh` + `.github/scripts/tailscale-durable/`（defconfig 前把官方 amd64 预编译和 asvow LuCI 铺进构建树，并覆盖 helper：不建 netifd `network.tailscale`、`firewall.tszone` 绑 `device=tailscale0`、开机 ensure；见 `docs/CUSTOM-TRIMMING.md` §二十二；LuCI 菜单在「服务」）；③ `.github/scripts/pin-quickstart.sh`（只 clone `quickstart` + `luci-app-quickstart`，首页去掉 Samba/易有云/下载器/ddnsto，存储服务只留 WebDAV，家长控制常显，侧栏不要 RAID/SMART，Makefile 保留 smartd+smartctl+mdadm 给磁盘信息，menu.d 关掉「系统 → 挂载点」，磁盘信息等到 Disk.Status 才结束 loading，首页流量图走 SSE ~1Hz，见 §二十三/§三十一～§三十五/§四十）；④ `.github/scripts/drop-luci-theme-bootstrap.sh`（`luci-light` 硬依赖 Bootstrap，不改的话 seed 删了也会被加回，见 §二十四）；⑤ `.github/scripts/patch-argon-menu-search.sh`（feeds install 后对 third feed 的 Argon 主题打补丁：侧栏「搜索菜单」空输入不弹层、结果面板自适应高度带圆角阴影、「未找到」居中，见 §四十三）。不要借此把整个 app-hub 拉进来，也不要为了编最新 Tailscale 去升 packages 的 golang（1.104.1 要 Go 1.27，本树 1.23.12，r8 已炸过）。**不要删 `target/linux` 里其他架构**——镜像已是 x86_64，那些目录不进固件，删了会把上游同步搞炸；下一轮 seed 可瘦的 D 档见 `docs/CUSTOM-TRIMMING.md` §十六。`istoreos-24.10` 分支仅用于 ff-only 同步上游（只合并官方修复，不为上游开 PR）
- 上游同步工作流：`git fetch upstream` → `git checkout istoreos-24.10 && git merge --ff-only upstream/istoreos-24.10` → `git checkout custom-24.10 && git rebase istoreos-24.10` → **用户明确要求后**才 `git push --force-with-lease origin custom-24.10`（不推 `istoreos-24.10`；命令详见 BUILD-CUSTOM.md）。因 seed 收敛在一个文件，99% 的提交无冲突；符号改名时 `make defconfig` 会静默删掉该行，靠 CI 的 seed 审计（`.github/scripts/seed-audit.sh`）报出已知清单外的未生效行并阻断，再按报告改 seed（改名不改功能，不用记账）。
- **开工先查上游（常驻规则，2026-10-31 用户要求）**：每次会话开始时（每个会话查一次即可，别每条命令都查）先 `git fetch upstream --no-tags`，然后看两个数：① `git rev-list --count istoreos-24.10..upstream/istoreos-24.10`＝上游新提交数；② `git rev-list --count custom-24.10..istoreos-24.10`＝本地还没 rebase 的积压。非零就 `git log istoreos-24.10..upstream/istoreos-24.10 --stat` 判断影响面：**只改其他架构目录（rockchip 等不进 x86_64 固件的）＝无影响**，一句话带过；改了 x86 target、kernel/base、`feeds.conf.default`，或触及现存模块相关路径（openclash/tailscale/ddns-go/quickstart/luci-app-ota/istoreos-ops 等对应的包与 feed）＝有影响。**只要有新提交（无论有无影响）就主动提示用户：新提交清单＋影响面＋建议，让用户决定要不要走上面的同步工作流；未经用户明确要求不得 merge/rebase/push**。上游无更新时一句话确认即可，不展开。
- 推送纪律：**禁止向 upstream（`istoreos/istoreos`）推送任何分支或标签，也不开 PR**。`istoreos-24.10` 只留本地跟踪 upstream，**不要推到 origin**。唯一允许的推送是 `custom-24.10` → `origin`，且**必须用户明确要求后再推**，不要自作主张（2026-10-31 用户明确要求）。
- PR 纪律：**不为上游原仓库送 PR**。本仓库定位是裁剪版维护 fork，只做需求裁剪与问题修复（如 vlmcsd、缓存死锁），所有改动留在 `custom-24.10` 分支供本地使用。如需贡献给 upstream，请评估是否影响其他设备或需要讨论后再决定。
- 记录纪律：**每次功能增删（改 seed）必须同一提交里更新 `docs/CUSTOM-TRIMMING.md`**，且写两层——①功能视角：变更后设备"不能做什么"（或恢复了什么）＋影响＋替代方案，格式见该文档 §六；②包名明细：按批次列全。不留记录的 seed 变更视同未完成；临时用 iStore 商店装回验证不用记录

**了解整个家庭服务器改造计划（为什么这样裁剪、全家设备分工、迁移路线）：读 [`docs/HOME-SERVER-BACKGROUND.md`](docs/HOME-SERVER-BACKGROUND.md)**。

构建与刷机步骤见 [`BUILD-CUSTOM.md`](BUILD-CUSTOM.md)；云端构建走 Actions（手动触发）。CI 历次失败的原始复盘（run 编号、日志原文）在 [`docs/CI-HISTORY.md`](docs/CI-HISTORY.md)，节号与 CUSTOM-TRIMMING.md 对应；CUSTOM-TRIMMING.md 只留当前有效的结论。

**OTA（2026-10-23）**：`luci-app-ota` 已改打本仓库 GitHub Releases（§三十七），禁止再指 koolcenter。**运维（同日）**：`istoreos-ops` 提供 OTA 前 curated 备份（盘满不拦刷）与 `istoreos-health` 巡检（§三十八）；Telegram 通知 + LuCI「服务 → 健康巡检」见 §三十九（无邮件）。

**进度（2026-10-30）**：最新镜像 **r43**（`8940a8b6fd`，seed 521，Releases 已发布；r34/r35 未出包）。含 QuickStart SSE 流量图、Tailscale「授权登录」、OTA 中文 + 下载进度。**记录在案的现场验证仍是 r33**（N100，已写入机内 16G 傲腾）；r38～r43 的界面改动未记录刷机验证。J4125 配置备份在维护机 `~/Documents/j4125-backup-20261018/`（还原用 **1019** 那份，不要整包灌）；**未确认主路由已刷裁剪版**（10-19 18:19 仍是官方 24.10.8）。不要为 NPM 把 Docker 加回网关（反代放 9400F）；不要用 Open-Box 换生产 OpenClash。快照见 [`docs/CUSTOM-TRIMMING.md`](docs/CUSTOM-TRIMMING.md) 文首、§三十六、§四十/§四十一。
