# iStoreOS 裁剪版（J4125 网关）

这是 [istoreos/istoreos](https://github.com/istoreos/istoreos) 的维护 fork，不是官方发行。分支 `custom-24.10` 给家里的 **J4125 四口 2.5G（i226-V）** 编纯网关固件：Docker / NAS 已迁走，路由器只做路由、Tailscale 入口和公网 DDNS。

当前最新镜像：**r43**（2026-10-30）。**记录在案的现场验证仍是 r33**（N100 闪迪 USB 已验证，傲腾已写入）；r38～r43 的首页 SSE、Tailscale 授权登录、OTA 中文进度尚未写验证结论。J4125 刷机前备份见维护机 `~/Documents/j4125-backup-20261018/`（还原用 1019 那份，不要整包灌）。未确认现场已刷前，不要远程动正在用的 J4125。

镜像：[Releases](https://github.com/xcy960815/istoreos/releases)（tag `r<构建号>`）。刷 **EFI img**：解压 `*-squashfs-combined-efi.img.gz` 后整盘 `dd`。默认账号 `root`、空密码。

## 开箱有什么

QuickStart 首页（存储服务只留 WebDAV、家长控制常显、磁盘信息正常、SSE ~1Hz 流量图）、Argon 主题、Tailscale **1.104.1** + LuCI（服务菜单）、DDNS-Go、OpenList、**系统 → OTA（仅本仓库 Releases）**、**服务 → 健康巡检（Telegram）**、iStore 商店、网络唤醒、ttyd、vlmcsd、kmod-igc、irqbalance。侧栏保留「网络向导」和「系统 → 备份与升级 / OTA」。

刷完再从 iStore 商店按需装（**不在构建期**，写进 seed 也进不了镜像）：OpenClash、eqos、oaf、cpufreq、风扇、diskman、gowebdav、fastnet、floatip。

## 删了什么（未经要求不得加回）

包名批次见 [`docs/CUSTOM-TRIMMING.md`](docs/CUSTOM-TRIMMING.md)。这里只记刷完机**不能再做什么**。

### 用户点名去掉的服务

| 不能再做 | 替代 / 备注 |
|---|---|
| 在路由器上跑 Docker / 容器管理 | 已迁 9400F |
| Samba / 易有云 / unishare 文件共享 | 文件服务归 9400F/N100；OpenList WebDAV 保留 |
| UPnP 自动端口映射 | 公网入口用防火墙手动转发 |
| ddnsto / Linkease 穿透 | 远程走 Tailscale；公网走 DDNS-Go |
| OpenWrt 自带 `luci-app-ddns` | 用 DDNS-Go，不要把这套加回来 |
| Aria2 / Transmission 下载器 | 首页下载卡片一并去掉 |
| 用 OTA 刷回 koolcenter 官方整包 | 「系统 → OTA」只拉本仓库 Releases，下载后仍需手动确认刷写；要官方包自己下载整盘写 |
| WireGuard / unetd | 远程只走 Tailscale |
| Bootstrap 第二主题 | 只留 Argon |
| 侧栏「文件传输」 | 已删包 |
| 首页 Samba / 易有云 / 下载 / Docker / ddnsto 卡片 | 存储服务只留 WebDAV |

### 界面没有、查询工具还在

| 看不见 | 实际还留着 | 原因 |
|---|---|---|
| 侧栏「网络存储 / 磁盘阵列 / S.M.A.R.T.」 | `smartd` + `smartctl` + `mdadm` | 给首页磁盘信息；无数据盘不要这些页 |
| 「系统 → 挂载点」 | `luci-mod-system`、`block-mount` | 备份与升级同包，只能藏菜单 |

### 按纯网关定位裁掉的能力

无对应硬件或场景，不是「以后可能用」：

- 无线 AP / USB 无线网卡
- 3G/4G/5G 模组（手机 USB 共享网络仍可用）
- USB 串口、并口、USB 摄像头、USB 声卡
- 接显示器跑图形 / i915 加速
- NFS 服务端、CIFS/davfs2 挂别人的盘、iSCSI、硬盘休眠、USB over IP
- L2TP / PPTP / SSTP / GRE / IPIP / IPsec、链路聚合、中继
- DS-Lite / MAP / SIT 等 IPv6 过渡隧道（原生 IPv6 还在）
- KVM 虚拟化
- 老式/万兆/Broadcom 等非保险网卡（保险只留 igc + e1000/e1000e/igb/r8169/r8125 + 主流 USB 网卡）
- 老式交换机芯片、ISDN/ATM、SCTP、TPM 密钥环、htop/strace（后两者可事后 opkg 装回）

下一轮还能瘦、但还没动的候选在 `docs/CUSTOM-TRIMMING.md` §十六。

## 试刷（N100）

N100 双口 Intel I225-V：第一口 WAN，第二口 LAN `192.168.100.1`。和家里 J4125 同网段，**不要插进家里交换机**。

1. 从 Releases 下 r43 的 `combined-efi.img.gz`，解压后整盘写入 U 盘（macOS 用终端.app 的 `sudo dd`，Finder「无法读取」正常，不要初始化）。
2. N100：U 盘优先启动，Secure Boot 关。
3. 测试机网线接 **第二口**，静态 `192.168.100.2/24`，网关留空；关掉会抢这个网段的 Wi‑Fi。打开 http://192.168.100.1 。

不要用双公头 USB 线连电脑和 N100。

## 构建

功能增删只改 `config-custom.seed`，不改源码。允许的例外只有：`feeds.conf.default` 的 `src-git ddnsgo`，以及 defconfig 前的 `pin-tailscale-prebuilt.sh`、`pin-quickstart.sh`、`drop-luci-theme-bootstrap.sh`。

云端：GitHub Actions 工作流 `Build iStoreOS trimmed`，手动触发。本地步骤、上游同步、刷机注意见 [`BUILD-CUSTOM.md`](BUILD-CUSTOM.md)。

分支：`istoreos-24.10` 只 ff-only 跟踪官方，**只留本地、不推 fork**；定制都在 `custom-24.10`，推送需明确指令。不为上游开 PR，也不向官方仓库推任何分支或标签。

## 文档

| 文件 | 内容 |
|---|---|
| [`AGENTS.md`](AGENTS.md) | 助手入口：纪律、例外、当前进度 |
| [`docs/CUSTOM-TRIMMING.md`](docs/CUSTOM-TRIMMING.md) | 裁剪记录（改 seed 必同步更新） |
| [`docs/HOME-SERVER-BACKGROUND.md`](docs/HOME-SERVER-BACKGROUND.md) | 全家设备分工和为什么这样裁 |
| [`docs/CI-HISTORY.md`](docs/CI-HISTORY.md) | CI 失败复盘 |
| [`BUILD-CUSTOM.md`](BUILD-CUSTOM.md) | 构建、刷机、同步上游 |

上游项目：[iStoreOS](https://github.com/istoreos/istoreos)（基于 OpenWrt，GPL-2.0）。本仓库只做需求裁剪和本地修复。
