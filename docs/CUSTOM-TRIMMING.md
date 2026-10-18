# iStoreOS 定制裁剪记录（面向后续 AI 助手 / 维护者）

> **必读**。本仓库是 `xcy960815` 对 iStoreOS 官方源（`istoreos/istoreos`）的 fork，
> 用于为家里的 J4125 四口 2.5G 软路由（LAN IP `192.168.100.1`）构建裁剪版固件。
> 用户在 2026-10-05 明确要求删除下列功能，**除非用户再次明确要求，不得在 seed 中加回**。

## 当前进度（2026-10-18 夜，后续 AI 先读这里）

**N100 已验证 r33**（`680cb032d5`，闪迪 USB 整盘）：首页磁盘信息有系统根目录用量；侧栏**没有**「网络存储 / 磁盘阵列 / S.M.A.R.T.」；存储服务只留 WebDAV、家长控制常显。seed `=y` **516**。下一步验机仍以 r33 为准；**禁止动 J4125**。

首页磁盘卡片要 `smartd` 包（含 `/etc/smartd.conf`）+ `smartctl` + `mdadm`；侧栏 RAID/SMART 仍从 controller 删除。r28 有菜单+磁盘信息；r29 拆工具后 loading；r31 空白（Raid.List 空数组提前结束转圈）；r32 等到 Disk.Status 仍转圈（无 smartd 包）。**尚未证明必须跑 smartd 后台进程**，不要为了「无盘」再拆这个包。明细 §二十三、§三十一～§三十五。

**两套状态不要混：** Releases 有 r22 / r28～r33。N100 双口 Intel I225-V（`kmod-igc`），第一口 WAN、第二口 LAN `192.168.100.1`。r17 是 Argon 概览（没有 QuickStart 首页）。r23～r27 从未出包。

**后续 seed 变更（2026-10-10，§二十）**：用户已要求移除 Aria2/Transmission 及其页面入口，当前 seed 已关闭 9 个包（596 → 587 个 `=y`）。r12 起的镜像已不含下载器（r10、r11 仍含）。

**后续 seed 变更（2026-10-12，§二十一）**：用户要求删除「在线升级」页面，seed 再关 2 个包（587 → 585 个 `=y`）。r13 起的镜像已不含 OTA。

**后续 seed 变更（2026-10-14，§二十二）**：用户要求内置最新 Tailscale。守护进程本来就在（r13 是 1.80.3）；本轮换成官方 **1.104.1** amd64 预编译，并烘焙 LuCI（asvow `luci-app-tailscale` v1.2.6）。不能从源码编最新版（要 Go 1.27，本树 golang 1.23.12）。seed 585 → 587。

**后续 seed 变更（2026-10-16，§二十三，`5612b37936` 已推送）**：用户要官方那种 QuickStart 首页，但不要 Samba/易有云/下载器/OTA。第三条构建例外 `.github/scripts/pin-quickstart.sh`：只 clone 两个包，从首页渲染里**删掉**存储/下载/远程域名/Docker 整块（不是开关隐藏）。侧栏「网络向导」保留。seed 587 → 590。**r17 没有这些**，还是 Argon 概览。

**后续 seed 变更（2026-10-16，§二十四，`5612b37936` 已推送）**：用户要求去掉第二主题 Bootstrap。seed 再关 1 个包（590 → 589）。`luci-light` 硬依赖它，所以还有 `.github/scripts/drop-luci-theme-bootstrap.sh`。界面只留 Argon。**r17 仍带 Bootstrap。**

**产物去处（2026-10-16 起，§二十五）**：构建成功后，镜像除 Actions artifact（14 天过期、下载要登录）外，自动发 GitHub Releases（tag `r<run_number>`，长期公开下载）。r17 及更早只在 artifact 里。

**后续 seed 变更（2026-10-16，§二十六）**：用户要求先清「杂项零头」。seed 删除 7 行（589 → 582）：`kmod-igbvf`、`kmod-ipt-physdev`（连带 br-netfilter）、`kmod-keys-encrypted`、`kmod-keys-trusted`、`kmod-ppdev`、`kmod-sctp`、`kmod-tpm`。**尚未构建**，编入 r19 之后的下一轮（r20）。

**后续 seed 变更（2026-10-16，§二十七）**：用户要求「继续删，最后一起编」。第二批清收一次做完：删 26 行、钉 8 行（seed 582 → **556**）——显示栈（钉 `kmod-drm-i915`）/USB 摄像头/USB 音频/隧道群（sit·ip6-tunnel·iptunnel6·nat46·siit·ds-lite·map）/老式交换机（swconfig＋6 驱动＋spi-ks8995）/nbd/htop·strace/华为 LTE 驱动/非保险网卡（钉 tg3·ixgbe·bnx2·amd-xgbe·amazon-ena·forcedeth·dwmac-intel）。**尚未构建**，与 §二十六 一起编入 **r20**。

**后续 seed 变更（2026-10-17，§二十八）**：用户指挥执行器重做一遍审计、Claude 验收。第三批清收删 **26 行**（seed 556 → **530**）——crypto 残留 7 条（arc4/cts/des/echainiv/fcrypt/michael-mic/pcbc，消费者 mppe·ipsec·rxrpc·NFS·CIFS·无线全不在固件且无 imply 回加）/Broadcom PHY 三连（bcm84881·broadcom·phylib-broadcom，tg3·bnx2 钉关后的尾巴）/USB 外设 8 个（cm109·printer·hid-cp2112·dwc2·dwc3·roles·wdm·chaoskey）/AMD CCP·binfmt-misc·mdio-gpio·mmc＋mmc-spi。**r21 构建审计暴露 3 行孤儿连带**（crypto-rsa 随 CCP、asn1-encoder 随 §二十六 的 tpm、裸 mdio 随 broadcom 链一起没了消费者），同轮一并删（见本节末「r21 连带」）。HID 输入簇与 unetd 全家经评估**保留**；`kmod-usb-uhci/ohci`（QEMU 老机型 USB）留后续。**r21 审计阶段红、未出镜像**，修后重触发。

**后续变更（2026-10-17，§二十三改口）**：用户只要首页「磁盘信息 + 存储服务里的 WebDAV」。`pin-quickstart.sh` 把「存储服务」模块加回首页，模块内**只留 WebDAV 卡片**（易有云 / Samba 仍从渲染删除，不留空位）。下载 / Docker / ddnsto 仍不显示。`auto_setup` 允许从商店装 `gowebdav`，仍拒绝 samba/linkease。同日再改口：快捷入口「家长控制」未装 `luci-app-oaf` 也要显示（点进去再商店装应用过滤）。r22 及更早、以及只含 WebDAV 那次构建都没有家长控制这块，**由 r28 重编**（见文首「当前进度」）。

**后续变更（2026-10-17 晚，§二十三/§三十 补漏）**：r28 侧栏仍有「网络存储」父菜单和「磁盘阵列 / S.M.A.R.T.」——不是 Samba 没删干净，是 `luci-app-quickstart` 自己注册的；`quickstart` Makefile 还硬依赖 `smartd`/`smartmontools`/`mdadm`，所以 §三十 从 seed 删掉的 SMART 三件套被 defconfig 加回了（r28 manifest 为证）。`pin-quickstart.sh` 拆掉这两条菜单和那四项 DEPENDS；`seed-audit.sh` 若再看到 smartd/mdadm=`y` 就红。要重编。

**后续变更（2026-10-17 夜，§三十一）**：用户要求删侧栏「挂载点」和「文件传输」。seed 删 `luci-app-filetransfer` 两行（514 → **512**）；挂载点在 `luci-mod-system` 里（备份与更新同包，不能删包），由 `pin-quickstart.sh` 写 menu.d 关掉。`block-mount` / sftp 仍留。工作区已改，**未提交、未推送、未构建**。

**后续变更（2026-10-17 夜，§三十二）**：r29 首页「磁盘信息」一直 loading。QuickStart 调 `GET /nas/disk/status/`，预编译守护进程要 `smartctl`；§三十/补漏把 `smartmontools` 也拆掉了。加回 `smartmontools`+`smartmontools-drivedb`（当时 512 → 514），`smartd` 仍不要。r30 已编已刷，**仍 loading**——还缺 `mdadm`，见 §三十三。

**后续变更（2026-10-18，§三十三）**：首页磁盘信息 `Promise.all([Disk.Status, Raid.List])`，RAID 列表要 `mdadm`。r30 只加了 smartctl，U 盘当系统盘不是主因。seed 加回 `mdadm`（514 → **515**），侧栏「磁盘阵列」仍藏、`smartd` 仍不要。工作区已改，**未提交、未推送、未构建**。defconfig 可能顺带加回 `kmod-md-*`，那是 mdadm 依赖，不是侧栏。

| 事实 | 细节 |
|---|---|
| 可用固件 | GitHub Actions **r17** 成功（run [`38561237293`](https://github.com/xcy960815/istoreos/actions/runs/38561237293)，提交 `597a40aba3`），产物 `istoreos-x86_64-trimmed-r17`。刷 **EFI img**：gz 解压后的 `*-squashfs-combined-efi.img` 整盘 dd。r10 已过时，别再刷 |
| r17 里面有什么 | DDNS-Go **6.12.2**、Tailscale **1.104.1** + LuCI（VPN → Tailscale）；WireGuard、网络唤醒、OpenList、Argon + Bootstrap。**没有** Docker/Samba/UPnP/ddnsto/下载器/OTA。登录是 Argon 状态概览，**没有** QuickStart 首页，侧栏**没有**「网络向导」。默认 `root` / 空密码 |
| 已写到哪 | 64G SanDisk 当 N100 系统盘（整盘 dd）。Finder「无法读取磁盘」正常，**不要初始化**。macOS 要用终端.app 完全磁盘访问后 `sudo dd`，Cursor `osascript` 会被 TCC 拦 |
| **禁止** | **不要刷正在用的 J4125**（和 N100 都是 `192.168.100.1`）。N100 的 LAN **不要**插家里交换机。**不要**用双公头 USB 线连 Mac↔N100 |
| N100 | **已经用这根 U 盘开过机**，能进 LuCI。双网口、无显示器、机内 16G 傲腾（RST 缓存条当不了系统盘就别写）。BIOS：U 盘优先、Secure Boot 关。Mac 无内置网口：网线接 N100 **第二口**，`192.168.100.2/24`、**网关留空**。家里关 Wi‑Fi；公司 USB 网卡（用过 AX88179A）必须排在 Wi‑Fi 下面，否则 `192.168.100.1` 会被公司网抢走 |
| 官方截图 | 家里 **J4125** 上的官方整包 QuickStart（Samba/易有云/固件更新卡片），不是 r17，也不是选错分支。`custom-24.10` 跟踪的就是 `istoreos-24.10` |
| 构建状态（2026-10-17 重写） | 全部改动已推送在 `origin/custom-24.10`（seed `=y` **514**）：QuickStart 首页＋去 Bootstrap（§二十三/§二十四）＋五批清收（§二十六 7 行、§二十七 26 删 8 钉、§二十八 26 行、§二十九 13 行、§三十 3 行）。最后成功镜像 **r22**（`703d8b99d7`，只含到 §二十八；审计干净、丢失仅 thermal/xdp 两已知项）；r23～r27 临时构建已取消并从 Actions 删除；**r28 正从最终版 `afcc97d026` 全新构建**，成功自动进 Releases（tag `r28`） |
| 本机编 | Mac 是 M1 Max，编不了这份 x86 树。9400F 还没装 Ubuntu |
| 还没做 | r28 出镜像后写 U 盘验证：QuickStart 首页（存储服务只留 WebDAV、家长控制常显）、WireGuard 已无、无盘无 SMART 报错；审计里显示栈/摄像头/隧道/交换机/br-netfilter/SMART 等应消失、「seed 没写却开启」不应新增；D 档剩余项（ruby/git/taskd/sqlite3-cli/lm-sensors-detect、冷门 fs，§十六）等 N100 证据；**J4125 仍禁止刷** |

后续 AI：**不要**把 QuickStart 写成「r17 已有首页」（r17 没有；r22 起有初版、r28 为最终版）；**不要**只删 seed 里的 bootstrap 就以为主题没了；**不要**再拿 r10 试刷；**不要**把双公头线当刷机方案。

## 一、改动纪律（最重要）

1. **所有功能增删只允许改根目录的 `config-custom.seed`，禁止直接修改源码文件** —— 这是上游修复能无痛合并的前提
2. 分支规则：
   - `istoreos-24.10`：只用于跟踪官方（`git merge --ff-only upstream/istoreos-24.10`），不放任何定制
   - `custom-24.10`：定制分支（seed、CI、文档都在这里），基于 istoreos-24.10 rebase 前进
3. 云端构建：GitHub Actions（`.github/workflows/build-istoreos.yml`，手动触发，公开仓库免费）
4. 完整构建/刷机流程见根目录 `BUILD-CUSTOM.md`
5. **记录纪律：凡改 `config-custom.seed`（功能增删），必须在同一提交里更新本文档**，写两层：
   - **功能视角**：变更后设备"不能做什么"（或恢复了什么能力）＋影响＋替代方案——表格格式参考 §六 的「功能视角」表
   - **包名明细**：按批次列出全部增删的包名
   - 临时用 iStore 商店装回验证不用记录；只有落在 seed 里的长期变更需要登记

## 二、删除清单（2026-10-05，用户要求）

| 类别 | 被删的包 | 原因 |
|---|---|---|
| Docker 全家桶 | containerd、docker、dockerd、docker-compose、runc、tini、libdevmapper、libseccomp、docker-deps、luci-app-dockerman、luci-app-dpanel、app-meta-dpanel、luci-lib-docker 及 i18n | Docker 服务已全部迁往 9400F Ubuntu 服务器（192.168.100.10），路由器不再跑容器 |
| Samba/文件共享 | samba4-server、samba4-libs、luci-app-samba4、kmod-fs-ksmbd、unishare、luci-app-unishare 及 i18n | 路由器不再做 NAS/文件共享；文件服务归 9400F/N100 |
| DDNS（OpenWrt 自带 + ddnsto，**仍禁止加回**） | ddns-scripts 全系列（含 cloudflare/dnspod/services/aliyun）、luci-app-ddns、ddnsto、luci-app-ddnsto 及 i18n | 用户不用自带那套，也不用 Linkease 穿透。**DDNS-Go 已于 2026-10-09 加回固件，见 §十五**；当初把三套一起删是误把「不用自带 DDNS」写成了「不用公网」 |
| UPnP | miniupnpd-nftables、luci-app-upnp、libminiupnpc 及 i18n | 无使用需求，减少暴露面 |
| Linkease 系 | linkease、luci-app-linkease、ddnsto 同属 Linkease 生态 | 未使用 |

## 三、保留清单（有实际使用证据，后续 AI 不要当成"没用"误删）

> ⚠️ 本清单是**功能**层面"别丢"，不等于"固件里已烘焙"：其中 openclash、`app-meta-*`、`luci-app-{cpufreq,fan,eqos,oaf,diskman,gowebdav,…}` 等不在构建期，按需从 iStore 商店装回。**QuickStart 首页已定要烘焙**（卡片已裁，见 §二十三），但 **r17 还没有**；改动已推送（`5612b37936`）、r19 构建中。哪些真在固件里、哪些要装回——唯一清单见 §六「仍然完好、一个没动的功能」和 §十，证据见 §九。

- **openclash**：全家主力代理，GeoIP 数据齐全、多份配置备份（用户本机代理 7897 与之同源）
- **ddns-go + luci-app-ddns-go**：公网 IP + 免费域名，**开箱即有**（第七条 feed `ddnsgo`）。勿删、勿改回「刷机后商店装」、勿用 `luci-app-ddns` 顶替
- **tailscale + luci-app-tailscale**：家人设备远程入口，路由器是 exit node（与公网 DDNS 并行，不是二选一）。**2026-10-14 起开箱即有**：官方 1.104.1 amd64 + asvow LuCI，见 §二十二。不要再写成「刷机后商店装 `luci-app-tailscale-community`」
- **openlist / vlmcsd / eqos / oaf / ttyd / wol(etherwake) / cpufreq / luci-fan / fastnet / floatip**：保留；2026-10-10 用户再次明确 OpenList 和它自带的 WebDAV 要留，不能随下载器删除
- **Aria2 / Transmission 已退出保留清单**：2026-10-10 用户明确不需要，连同管理页面和首页入口一起去掉，见 §二十。旧配置行数不再作为保留依据
- **istore / luci-app-store / argon 主题 / QuickStart 首页**：系统管理骨架，勿动。首页方案见 §二十三（磁盘信息 + 存储服务仅 WebDAV；Samba/易有云/下载器/ddnsto 卡片去掉）；不要加回 Bootstrap（§二十四）
- **kmod-igc**：四个 2.5G i226-V 网卡的驱动，删了机器变砖
- **irqbalance**：定制新增，为四张 2.5G 网卡分摊中断

## 四、硬件与拓扑上下文

设备分工、网段和四口规划只在 [`HOME-SERVER-BACKGROUND.md`](HOME-SERVER-BACKGROUND.md) §二/§三 维护。本固件目标机 J4125 的定位：纯网关 + Tailscale 入口 + 公网 DDNS-Go + VLAN 分段 + OpenList（含 WebDAV）。

## 五、改回/新增某功能的正确姿势

1. 临时：刷好系统后在 iStore 商店装回
2. 长期：往 `config-custom.seed` 加一行 `CONFIG_PACKAGE_xxx=y`，提交到 custom-24.10，Actions 重编

## 六、二次裁剪（2026-10-05，按"纯网关"定位再减法）

首轮 seed = 官方镜像清单做减法，官方清单里大量包是为**通用硬件**准备的。按目标机最终定位
（无无线的纯网关 + Tailscale 入口 + 公网 DDNS-Go + VLAN，文件服务归 9400F/N100）做第二轮减法。
仍在 seed 内完成，未动源码；§三保留清单**原封未动**。seed 包配置行数 1078 → 697。

### 功能视角：二次裁剪后这台路由器"不能再做什么"

| 不能再做的功能 | 涉及（已删） | 影响 / 替代方案 |
|---|---|---|
| 无线 AP / 无线中继 / USB 无线网卡 | mac80211、hostapd、wpa-supplicant、全系无线驱动+固件 | 机器本来就没无线网卡；日后插 USB 无线网卡需往 seed 加回 mac80211+wpa-supplicant |
| 3G/4G/5G 上网模组、随身 WiFi 拨号 | modemmanager、libmbim/libqmi、comgt、usb-modeswitch、mhi/qrtr | 无此硬件；**断网应急改用手机 USB 共享网络**（rndis/ipheth/cdc-ncm 已保留，插 iPhone/Android 可当 WAN） |
| USB 转串口设备（调试线/串口模块） | kmod-usb-serial 全系 | 需要时 iStore 临时装回或往 seed 加一行 |
| 接显示器看图形界面、GPU 工具 | i915/amdgpu/radeon 固件、DRM/fb 全系、nvtop | 无头设备无影响；GRUB 菜单和 VGA 文本控制台仍可用，QEMU 验证不受影响 |
| 当 NFS/Samba 服务器；用 cifsmount/davfs2 挂载别人的网络盘 | NFS 服务端全家、cifsmount、davfs2（Samba 首轮已删） | OpenList 及其自带 WebDAV 保留；独立的 gowebdav/webdav2 仍不在构建期 |
| RAID / 多盘合并 / 硬盘休眠 / iSCSI / USB over IP | mdadm+kmod-md、kmod-dm、mergerfs、hd-idle、iscsi/aoe、usbip | 单盘直用完全不受影响 |
| L2TP/PPTP/SSTP VPN 拨号、GRE/IPIP 隧道、IPsec、链路聚合、中继 | 各协议 kmod+用户态、bonding、relayd | 不用这些拨号协议；远程走 Tailscale 或公网端口转发。~~WireGuard 完整保留~~ **（2026-10-17 已删 WireGuard+unetd 全家，远程只走 Tailscale，见 §二十九）** |
| 跑 KVM 虚拟机 | kvm/vfio/vhost（容器首轮已删） | 虚拟化归 9400F/N100 |
| 识别老式/服务器级网卡（万兆、FC、古董 PCI） | 对应驱动+固件 | 常用保险已留：**igc + e1000/e1000e/igb/r8169/r8125** + 主流 USB 网卡（asix/ax88179/aqc111/rtl8152） |
| ISDN/ATM 电话线拨号 | misdn/hfc/atm/solos | 古董功能，无影响 |
| UPnP NAT 映射（首轮已删）的残留客户端库 | libnatpmp1 | 无影响 |

### 仍然完好、一个没动的功能

本节写于 r4 审计之前，当时把"路由器在用的功能"和"固件里已烘焙的包"混为一谈，按 §九/§十 的口径重列。以下清单已按 §二十 更新为当前 seed 的预期，r10 等旧镜像仍含 Aria2/Transmission：

- **固件里确实有（r17）**：**tailscale 1.104.1 + luci-app-tailscale（见 §二十二）**、**ddns-go + luci-app-ddns-go（见 §十五）**、openlist（含 WebDAV）、
  vlmcsd、ttyd、wol、iStore 商店本体（`luci-app-store`+`dkml`）、argon 主题、zram、lm-sensors（CPU/风扇温控）、smartd（**r17 有；2026-10-17 无盘删除，见 §三十；注意 smartd 是硬盘 SMART、不是温控，温控是 lm-sensors**）、
  wireguard（**r17 有；2026-10-17 起从 seed 删除，见 §二十九**）、dnsmasq-full、flow offload（kmod-nf-flow）
- **不在固件里、刷机后要从商店装回**：openclash、eqos、oaf、cpufreq、luci-app-fan、fastnet、floatip、
  gowebdav——它们从来不是构建期候选，包名与证据见 §十。**Tailscale LuCI 已不在此列**。**QuickStart 也不该再写成商店装，但 r17 还没有，等 §二十三 那轮构建**

### 包名明细（按批次）

| 批次 | 删除内容 | 依据 |
|---|---|---|
| A 无线全家 | mac80211/cfg80211、ath/mt76/rtl/rtw/iwlwifi 全系 kmod+固件（含 iwlwifi-firmware×8、rtl-固件×15）、hostapd、wpa-supplicant/wpa-cli、wifi-scripts、wireless-regdb、iw/iwinfo/libiwinfo | J4125 盒子无无线网卡，四口全有线 |
| A 蜂窝 modem 全家 | modemmanager、libmbim/libqmi/libqrtr-glib/uqmi/umbim/qmi-utils、comgt×3、usb-modeswitch、adb/adb-enablemodem、chat、kmod-mhi/qrtr/wwan/mtk-t7xx、全部 kmod-usb-serial、usb-acm/usb-atm、kmod-atm/solos-pci、usb-net 中的 mbim/qmi/hso/sierra/kalmia/kaweth | 无蜂窝硬件；**USB 网卡与手机共享网络保留**（rndis/ipheth/cdc-ncm/asix/ax88179/aqc111/rtl8152 等） |
| A GPU/显示 | amdgpu/radeon/i915 固件、kmod-drm 全系、kmod-fb 全系、kmod-acpi-video/backlight、nvtop、libdrm | 无头路由；GRUB/QEMU 文本控制台不受影响（kmod-ata-piix 专门留作 QEMU 默认 IDE 启动） |
| B 文件/存储服务 | nfs-kernel-server 全家+rpcbind+kmod-fs-nfs×5、cifsmount/luci-app-cifs-mount/kmod-fs-cifs+kmod-fs-smbfs-common/wsdd2、davfs2+libneon、mergerfs+luci-app-mergerfs、hd-idle+luci-app-hd-idle、mdadm+kmod-md×7+kmod-dm(-raid)+kmod-dax、iscsi/aoe/mpt3sas/mvsas/libsas/scsi-tape/scsi-raid/libfc/libfcoe、usbip×3 | 文件服务已归 9400F/N100，单盘无 RAID（对应 §四 拓扑） |
| C 隧道/协议/虚拟化 | l2tp×3/ppptp(mppe)/sstp/gre/ipip/ipsec/macsec/tls 的 kmod+用户态、gre/ipip 协议处理器、bonding+proto-bonding、relayd+luci-proto-relay、trelay、kmod-kvm×3/vfio×2/vhost×2/irqbypass、kmod-9p×3、kmod-misdn/hfc×2 | 不用 L2TP/PPTP 拨号（远程走 Tailscale 或公网端口转发），不做虚拟化宿主，无 ISDN |
| C Docker/UPnP 孤儿 | kmod-veth/macvlan/ipvlan/vxlan/br-netfilter/nf-ipvs、libnatpmp1 | 原为已删 Docker/UPnP 的依赖（首轮漏网） |
| C 老式网卡 | 3c59x/8139/tulip/via/sis/skge/sky2/tg3/bnx2*/mlx4/5/ixgbe/i40e/iavf/qed×4/sfc/ena/amd-xgbe/atl×5/alx/b44/e100/forcedeth/natsemi/ne2k/pcnet32/niu/pcs-xpcs/stmmac/dwmac/ethoc/et131x/dm9000/r6040/vmxnet3、kmod-r8168/r8126/r8127、ssb 及 bnx2/bnx2x/e100/qed/rtl/mwifiex 各固件 | **保险只留 igc（命根）+ e1000/e1000e/igb/r8169/r8125** |

### D 档（查清依赖后另批处理，本次未动）

候选仍在 seed 里。2026-10-09 把「能不能因只做 x86 再砍」也写进台账，见 **§十六**（未改 seed，等当前 CI 出镜像）。

- `ruby` 全家、`git/git-http`、`taskd/luci-lib-taskd`、`sqlite3-cli`：官方镜像里某处在用，无法本地查依赖（`linkmount` 原也在此列，§九 证实它是商店包，已随 §十 清掉）
- `lm-sensors-detect` + `perl` + perlbase-*×31：perl 疑似仅被 lm-sensors-detect（Perl 脚本）拉入；**lm-sensors 本体必须留**（luci-app-fan 温控）
- 文件系统类待确认数据盘实际格式：btrfs/ntfs3/f2fs/xfs/reiserfs/jfs/hfs/hfsplus/isofs/udf/cramfs/minix/msdos + exfat/vfat（U 盘建议留）
- 其他低价值但便宜：swconfig/switch-*、map/ds-lite/sit/siit/nat46、kmod-sctp/tpm/udptunnel/ppdev 等

**验证方法（路由器上执行）**：`opkg whatdepends ruby git taskd perl lm-sensors-detect`；`df -T /mnt/sata1-4`

### 安全网（为什么敢删）

1. `make defconfig` 会把"仍被保留包硬依赖"的项自动加回 `=y`——审计脚本 `.github/scripts/seed-audit.sh` 现在直接打印这份"seed 没写却开启"的清单（`seed-audit.txt` 第二段），刷前照它核对，不再靠猜候选。**但不止硬依赖**：它还会加回 **profile 默认包**（`DEFAULT_PACKAGES`），这类可能与有意替换的实现冲突，见 §七
2. **`make defconfig` 必须在 `./scripts/feeds install -a` 之后跑**，否则所有 feed 包的 `CONFIG_PACKAGE_*=y` 行被静默丢弃（符号还不存在），后果见 §七 原因 1
3. **软依赖**（脚本 shell 调用而非包依赖）不会被自动拉回——QEMU 启动验证 + 刷机后核对 LuCI 各页（重点：iStore 商店、**已烘焙的 Tailscale/DDNS-Go**；下一轮才有 QuickStart 首页；磁盘管理、openclash 这些**先按 §九 从商店装回**再核对）照 BUILD-CUSTOM.md 流程走
4. `dkml`（iStoreOS 动态内核模块加载器，package/diy/dkml）**保留**：iStore 商店装内核模块类应用的基础设施

## 七、构建顺序与 dnsmasq 冲突（r1，2026-10-05）

| 规则 | 原因 |
|---|---|
| **先 `./scripts/feeds update -a && ./scripts/feeds install -a`，再 `cp config-custom.seed .config && make defconfig`** | 顺序反了，feed 包符号还不存在，kconfig 把这些 `=y` 行无警告删除；r1 的产物连 LuCI 都没有 |
| seed 钉 `# CONFIG_PACKAGE_dnsmasq is not set` | `dnsmasq` 是 x86 profile 默认包，和 `dnsmasq-full` 装同一批文件，`package/install` 报文件冲突。`is not set` 扛得住 `default y`，扛不住其他包的 `select` |
| CI 在 defconfig 后跑 `seed-audit.sh` | 符号不存在时 `=y` 行被静默删除，只能靠审计发现；阻断规则见 §十四 |

**功能视角**：零增删。`dnsmasq-full` 以 `PROVIDES:=dnsmasq` 满足依赖。

查构建状态：`gh run list` 要带 `--repo xcy960815/istoreos --workflow "Build iStoreOS trimmed"`；本目录若配了 upstream remote，不带 `--repo` 会解析到上游并返回空数组。

日志原文、kconfig 语义实测、r1/r2 计数见 [`CI-HISTORY.md`](CI-HISTORY.md) §七。

## 八、vlmcsd 下载 404（r4）→ 结论并入 §十三

另一条仍有效的规则：`make download` 对失败包只打 `ERROR: package/…`、退出码仍是 0，所以 CI 的 Download sources 自己扫日志并失败退出。复盘见 [`CI-HISTORY.md`](CI-HISTORY.md) §八。

## 九、r4 审计定档：106 行未生效的真实构成

`seed 想要 697 → defconfig 后开启 705 → 丢失 106`（展开 `.config` 在 artifact 里叫 `config-expanded.txt`；此前写 `.config` 上传不到，dot 文件被 glob 跳过了）。

**符号不存在 104 行**，两类：

1. **带 ABI 后缀的 opkg 二进制包名** 61 行（`libcurl4` `libgcc1` `libubus20250102` `libruby3.3` …）。kconfig 符号是无后缀的 `libcurl`/`libubus`，后缀只出现在打包出的包名上。死行，库随依赖自动进镜像——已在 §十 清掉。
2. **iStoreOS 商店应用**（其余 43 行）：`luci-app-openclash`、`luci-app-tailscale-community`、`quickstart`/`luci-app-quickstart`/`luci-i18n-quickstart-zh-cn`、全部 `app-meta-*`、`luci-app-{cpufreq,fan,eqos,oaf,diskman,fastnet,floatip,gowebdav,openclawmgr}`、`luci-lib-mac-vendor`、`linkmount`、`fastnet`、`floatip`、`gowebdav`、`webdav2`、`appfilter`、`kmod-oaf`、`aria2-entry-deps`、`luci-js-deps`、`transmission-daemon-openssl`、`jansson4`。
   - **证据**：当时 `feeds.conf.default` 与上游 `istoreos/istoreos@istoreos-24.10` 逐字相同（只有 packages/luci/routing/telephony/store/third 六个 feed；**2026-10-09 起多了第七条 `ddnsgo`，见 §十五**），而 defconfig 后 `tmp/.config-package.in` 的 **11910** 个包符号里 `quickstart|openclash|app-meta|diskman|eqos|oaf|fastnet|floatip|linkmount|appfilter` 命中 **0**。
   - 这些应用住在**没写进 feeds.conf 的仓库**：`jjm2473/openwrt-app-meta`（`applications/app-meta-*`）、`jjm2473/openwrt-apps`（`luci-app-cpufreq`/`luci-app-fan`/`luci-lib-mac-vendor`）、`istoreos/quickstart`、`istoreos/istoreos-app-hub`（`apps/quickstart,fastnet,floatip,linkmount,webdav2,…`）。
   - 也就是说 §六 的基准（路由器 `opkg list-installed` 1122 包）**混入了刷机后从 iStore 商店运行时安装的包**，它们从来不是本仓库的构建期候选；裁剪台账里它们的"已删/保留"都是虚账。
   - 反面确认：商店自身在——`luci-app-store`、`dkml`、`istoreos-files`、`tailscale`（守护进程）都有符号且已开启，刷完机仍可从商店逐个装回。

**符号存在却没开成 2 行**：`kmod-thermal`、`kmod-xdp-sockets-diag`——内核内建符号没开（需 `make kernel menuconfig`，或该 target 未 support），与 feed 无关。

**已定（2026-10-06，用户选）**：**不**把整个 iStore 商店 / app-hub 追加进 `feeds.conf`，维持"固件只留路由栈 + 商店本体，刷机后按需从 iStore 商店装回 openclash / eqos …"。随之把 104 行死 seed 清掉，见 §十。

**修订（2026-10-09）**：公网域名是硬需求，六个默认 feed 里又没有 DDNS-Go。允许也只允许 **一条** 例外 feed：`src-git ddnsgo https://github.com/sirpdboy/luci-app-ddns-go.git;v6.12.2`。这不是「商店 feed 开闸」——openclash 等仍不进构建期。见 §十五。

**修订（2026-10-14）**：用户要求内置最新 Tailscale。第二条构建例外是脚本、不是新 feed：`.github/scripts/pin-tailscale-prebuilt.sh`。openclash 等仍不进构建期。见 §二十二。

**修订（2026-10-16）**：用户要 QuickStart 首页、不要那些已删服务。第三条构建例外 `.github/scripts/pin-quickstart.sh`：只 clone 两个包，不拉 app-hub。见 §二十三。

## 十、清掉 104 行"从未生效"的 seed 行（2026-10-06，697 → 593）

### 功能视角

**设备能做的事零变化**——这 104 行自写进 seed 起就是空转（符号不存在，defconfig 无警告删除），删掉它们不移除任何一块已烘焙的功能；固件产物与清理前逐包相同。

要交代的不是"删了什么"，而是**刷机后必须自己装回的东西**（原先误以为已在固件里）：OpenClash、eqos IP 限速、oaf/appfilter 应用过滤、cpufreq 与风扇调节、diskman 磁盘管理、gowebdav/fastnet/floatip/webdav2。装回途径：LuCI → iStore 商店（本体 `luci-app-store` + `dkml` 已在固件）。**2026-10-10 更正：Aria2/Transmission 及其入口与商店元数据不再装回**（§二十）；**Tailscale LuCI 2026-10-14 起已烘焙**（§二十二，r17 已有）；**QuickStart 首页方案见 §二十三，r17 还没有**；下方批次清单只记录历史清理，不是恢复清单。

### 包名明细（全部为「符号不存在」的死行，按档位列全）

**A 库类——带 ABI 后缀的 opkg 包名（61）**：jansson4、libatomic1、libblkid1、libblobmsg-json20240329、libbpf1、libbz2-1.0、libcomerr0、libcurl4、libe2p2、libelf1、libevent2-7、libevent2-core7、libevent2-pthreads7、libext2fs2、libf2fs6、libfdisk1、libfuse1、libgcc1、libgmp10、libipset13、libiptext-nft0、libiptext0、libiptext6-0、libjson-c5、libjson-script20240329、libkeyutils1、liblua5.1.5、liblucihttp0、liblzo2、libmbedtls21、libmnl0、libmount1、libncurses6、libnetfilter-conntrack3、libnettle8、libnfnetlink0、libnftnl11、libnghttp2-14、libnl-tiny1、libopenssl3、libpcap1、libpopt0、libpsl5、libreadline8、libruby3.3、libsensors5、libsmartcols1、libsqlite3-0、libss2、libstdcpp6、libsysfs2、libubox20240329、libubus20250102、libuci20250120、libuclient20201210、libucode20230711、libusb-1.0-0、libustream-mbedtls20201210、libuuid1、libuv1、libxtables12

**B 商店元数据 app-meta-*（9）**：app-meta-{aria2,eqos,fastnet,floatip,gowebdav,openclawmgr,openlist,transmission,vlmcsd}

**C 商店 LuCI 前端（24）**：luci-app-{cpufreq,diskman,eqos,fan,fastnet,floatip,gowebdav,oaf,openclash,openclawmgr,quickstart,tailscale-community}、luci-i18n-{cpufreq,diskman,eqos,fan,fastnet,floatip,gowebdav,oaf,openclawmgr,quickstart}-zh-cn、luci-js-deps、luci-lib-mac-vendor

**D 其他商店主包/入口（10）**：appfilter、aria2-entry-deps、fastnet、floatip、gowebdav、kmod-oaf、linkmount、quickstart、transmission-daemon-openssl、webdav2

**保留未动**：`kmod-thermal`、`kmod-xdp-sockets-diag`——这两行符号真实存在，只是内核内建项没开，属"真缺"而非"死行"，要恢复得动 `make kernel menuconfig`，不能从 seed 里一删了之。D 档（§六）里点名要查依赖的 `linkmount` 也在这批被清掉了：它根本不是构建期候选，路由器上那份是商店装的。

## 十一、CI 缓存与构建时长（r5–r7，2026-10-06）

- **只缓存 `dl`**：save 挂 `always()`，被 timeout 杀掉也照存，省掉冷下载约 28 分钟
- **不缓存 `staging_dir`**：`.built` stamp 在 `build_dir/`，只存 staging_dir 续不了编，白占 10GB 配额
- `build_dir` 能不能缓存看 Report disk usage 量出的体积；更彻底的路是 9400F 自建 runner，**未定**
- 全量冷编约 4h15m–4h45m（r7 实测）；加 DDNS-Go 后 r8 编译段 4h21m。350 分钟 timeout 够用

死循环诊断、stamp 落点表、取消语义实测见 [`CI-HISTORY.md`](CI-HISTORY.md) §十一/§十三。

## 十二、CI 整理（2026-10-07）

结论已落进 workflow 和脚本：审计逻辑在 `.github/scripts/seed-audit.sh`（装好 feeds、跑过 defconfig 后可本地执行）；apt 依赖只维护 `.github/apt-packages.txt` 一份，CI 与 BUILD-CUSTOM 共用；artifact 只收结论（展开的 config、审计报告、compile.log），不收原料。逐条理由见 [`CI-HISTORY.md`](CI-HISTORY.md) §十二。

**仍待做**：seed 里约一半是依赖闭包抄写（`lib*`、`kmod-crypto-*`、`kmod-usb-*`、`shadow*`、`kmod-nf-*`、`perlbase-*`、`kmod-fs-*`），理论上能收到约 150 行意图清单。软依赖不会被 defconfig 拉回，所以不能靠推理删：逐组剥离 → `make defconfig` → 与基线包集合比差集，差集为 0 的组才删。需要 Linux 构建环境。

## 十三、vlmcsd 的两处 feed 笔误（r4–r7）

`jjm2473/openwrt-third` 的 vlmcsd Makefile 把 tag 写成 `1113`，上游实际叫 `svn1113`，归档内目录是 `vlmcsd-svn1113`。两行都要补：

| 行 | 原值 | 改成 |
|---|---|---|
| `PKG_SOURCE_URL_FILE` | `$(PKG_VERSION).tar.gz` | `svn$(PKG_VERSION).tar.gz` |
| `PKG_BUILD_DIR` | `$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)` | `$(BUILD_DIR)/$(PKG_NAME)-svn$(PKG_VERSION)` |

不补第一行，下载 404；不补第二行，构建目录是空的（`No targets specified and no makefile found`）。改的是 `scripts/feeds install` 生成的 feed 副本，不在仓库版本里，不算改源码。CI 和 BUILD-CUSTOM 步骤 3b 都只匹配原笔误整行；feed 作者自己修好后会跳过，不会拼出 `svnsvn1113`。sha256 与 feed 的 `PKG_HASH` 一致，内容没变。

CI 失败处理的两条规则：步骤里显式 `set -eo pipefail`（runner 默认 `bash -e` 不带 pipefail，`make | tee` 失败会静默变绿）；失败后只对 `ERROR: package/…` 点名的包 `-j1 V=s` 重跑，不全局重跑。

**功能视角**：零增删，vlmcsd 仍在固件里。r7 阶段耗时、日志原文、实测过程见 [`CI-HISTORY.md`](CI-HISTORY.md) §十三。

## 十四、审计阻断规则（2026-10-08）

- **seed 审计会阻断构建**：已知清单之外的未生效行、或 `CONFIG_PACKAGE_dnsmasq=y` 复现，都 `::error::` 失败，几分钟内暴露，不等编译
- 已知清单只有 `kmod-thermal`、`kmod-xdp-sockets-diag`（内核内建符号没开，见 §十）。往清单加项须同时在本文记账；已知项若开成了，审计会提示可从清单删
- 上游符号改名时 `make defconfig` 本地零提示，就靠这一步拦截；按 `seed-audit.txt` 改 seed 即可（改名不改功能，不用记账）

8 条 code-review 明细与验证过程见 [`CI-HISTORY.md`](CI-HISTORY.md) §十四。

## 十五、加回 DDNS-Go（2026-10-09，用户明确要求开箱即有）

首轮把三套 DDNS 一起删掉，依据写成「远程只走 Tailscale、不用公网」。2026-10-09 用户纠正：宽带有公网 IP、有免费域名，**网关必须走公网**；家人远程仍用 Tailscale，两条路并行。嫌 OpenWrt 自带 `luci-app-ddns` 难用，指定 **DDNS-Go**。

六个默认 feed 里没有 `ddns-go` / `luci-app-ddns-go`（它们是 iStore 商店应用，和 openclash 同类）。只往 seed 写 `CONFIG_PACKAGE_ddns-go=y` 会变成 §九 那种死行，CI 审计还会硬失败。所以这次破例改 `feeds.conf.default`，**只加一条** feed，不把 app-hub 拉进来。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：刷完机 LuCI 里就有 DDNS-Go，把免费域名的 A/AAAA 刷到当前公网 IP | `ddns-go`、`luci-app-ddns-go`、`luci-i18n-ddns-go-zh-cn` | 域名、Token 仍要用户自己填；不会预置任何密钥 |
| **能**：公网访问内网服务（配合防火墙手动端口转发） | 已有 firewall4，未改 | 不上 UPnP（仍禁止加回） |
| **仍不能**：用 OpenWrt 自带 DDNS、用 ddnsto 穿透 | `luci-app-ddns` / `ddns-scripts*` / `ddnsto` **不加回** | 用户明确不用这两套 |
| **仍不能**：开箱即有 OpenClash 等商店应用 | 未改 feeds 的另外六条、未改 §十 清单 | 刷机后商店装回，与本次无关 |

### 包名明细

| 动作 | 内容 |
|---|---|
| `feeds.conf.default` 新增 | `src-git ddnsgo https://github.com/sirpdboy/luci-app-ddns-go.git;v6.12.2`（起初跟 `main`，r8 改为钉 tag） |
| seed 新增 `=y` | `ddns-go`、`luci-app-ddns-go`、`luci-i18n-ddns-go-zh-cn`（seed `CONFIG_PACKAGE_*` 593 → 596） |
| 不加 | `app-meta-ddnsgo`（商店元数据，无 kconfig）、`luci-app-ddns`、`ddns-scripts*`、`ddnsto*` |

`ddns-go` 是 Go 包（`PKG_BUILD_DEPENDS:=golang/host`），冷编多一套 golang host。r10 已确认三行全部生效。

### 为什么钉 v6.12.2

`main` 已到 6.17.1，`go.mod` 要 Go ≥ 1.25；`istoreos-24.10` 的 golang 是 1.23.12，且 `GOTOOLCHAIN=local` 不许自动下载新 toolchain（r8 唯一失败的包）。`v6.12.2`（`c0730e9`）的 `go.mod` 正好是 1.23.12，与商店当时的版本相同。不为此升级 packages feed 的 golang。报错原文见 [`CI-HISTORY.md`](CI-HISTORY.md) §十五。

后续 AI：**不要**再根据 §二 旧表述把 DDNS-Go 删掉；**不要**把这条 feed 扩成整个商店源；golang 升到 ≥ 1.25 之前**不要**把 `ddnsgo` 改回跟踪 `main`。

## 十六、下一轮可瘦（2026-10-09 记，**未改 seed**）

用户问：固件只面向 x86，能不能再去掉一部分代码。结论先记在这里，**等当前 CI（含 §十五 DDNS-Go）出镜像后再动 seed**，免得正在跑的构建作废。

### 不要做的：从 git 里删其他架构源码

seed 已是 `CONFIG_TARGET_x86=y` / `CONFIG_TARGET_x86_64=y` / `DEVICE_generic`。`make` 只编 x86_64 内核和选中的包；`target/linux` 下 ARM、MTK、瑞芯微等目录**不会进 squashfs**。那些是上游源码树，删了会让 `istoreos-24.10` ff-only 和 `custom-24.10` rebase 必冲突，也违反 §一「不改源码」。CI 时间花在 tools/toolchain 和 x86 包上，不在别的 target。

「只做 x86」已经体现在 target 选择上，不是再删源码树。

### 可以做的：再收 seed（这台 J4125，不是「所有 x86」）

二次裁剪已经按盒子拿掉无线/蜂窝/老网卡/KVM。剩下是 §六 D 档——和架构无关，是「这台机器用不用」。每组必须先在路由器上 `opkg whatdepends`（或刷裁剪版后查），硬依赖为 0 才从 seed 钉 `# CONFIG_PACKAGE_xxx is not set`。软依赖（脚本里调命令）不会被 defconfig 拉回，见 §六安全网 3。

**2026-10-16 执行记录**：首批「杂项零头」（§二十六）＋第二批清收（§二十七）已落地——上表「老式交换机 / 过渡隧道」行整行执行（并多删 `kmod-siit`、`kmod-ip6-tunnel`、`kmod-iptunnel6`、`kmod-spi-ks8995`），「非保险网卡」行按行执行且保险定型（保留不再收）。两批都未用路由器 `opkg whatdepends`，依据是本地构建树反向依赖核查（依赖者全未进固件）+ CI 审计兜底。**剩余候选**：ruby/git/taskd/sqlite3-cli/lm-sensors-detect、冷门 fs——等 N100 刷机后按表中前提核查再动。

#### 功能视角（候选，未执行）

| 若从 seed 删掉，设备不能再做什么 | 候选（仍在 seed） | 前提 / 必须留的 |
|---|---|---|
| 跑 ruby 脚本 | `ruby`、`ruby-bigdecimal/date/digest/enc/pstore/psych/stringio/yaml` | `opkg whatdepends ruby` 为空才砍 |
| 在路由器上 git clone | `git`、`git-http` | 纯网关不需要；whatdepends 为空才砍 |
| taskd 任务框架 | `taskd`、`luci-lib-taskd` | 同上 |
| sqlite 命令行 | `sqlite3-cli` | **库可能被别的包依赖，只砍 CLI** |
| `sensors-detect` 探测芯片 | `lm-sensors-detect`、`perl`、全部 `perlbase-*` | **`lm-sensors` 本体留**（风扇温控） |
| 挂冷门磁盘格式 | `kmod-fs-{hfs,hfsplus,jfs,reiserfs,minix,cramfs,isofs,udf,msdos}` 及对应用户态 | **必留**：squashfs、ext4、vfat/exfat（U 盘）、efivarfs。btrfs/xfs/ntfs3/f2fs 等 `df -T /mnt/sata1-4` 再说 |
| 老式交换机 / DS-Lite 等过渡隧道 ✅ 已删（§二十七） | `map`、`ds-lite`、`kmod-sit`、`kmod-ip6-tunnel`、`kmod-iptunnel6`、`kmod-nat46`、`kmod-siit`；交换机簇 `kmod-swconfig`＋6×`kmod-switch-*`＋`kmod-spi-ks8995` | IPv6 本体（odhcp6c/odhcpd）留（未动） |
| 换一块非 Intel i226 的 PCI 网卡 ✅ 保险已定型（§二十七） | 非保险网卡已钉关：`kmod-tg3`、`kmod-ixgbe`、`kmod-bnx2`、`kmod-amd-xgbe`、`kmod-amazon-ena`、`kmod-forcedeth`、`kmod-dwmac-intel`（`kmod-igbvf` 已删，§二十六） | 保险保留不再收：`kmod-igc`（本机）、`kmod-e1000`、`kmod-e1000e`、`kmod-igb`、`kmod-r8169`、`kmod-r8125`；USB 网卡 + 手机 RNDIS/iPhone 共享仍留 |

#### 包名明细（仍在 seed，尚未删除）

执行时按上表分组从 `config-custom.seed` 去掉对应 `=y`（或钉 `is not set`），同一提交更新本节或新开一节：把「候选」改成「已删」，并写清刷完机少了什么。2026-10-16 首批记于 §二十六、第二批记于 §二十七。

后续 AI：**不要**把本节当成授权去删 `target/linux` 或其他架构源码。r9 已证明打盘会挂，允许的 seed 改动只有 §十七 的镜像布局；D 档包分批推进，首批与第二批已执行（§二十六、§二十七），其余等 N100 刷机后的依赖证据再继续。

## 十七、镜像布局：只出 squashfs，分区 32/512（r9，2026-10-09）

| seed 设置 | 原因 |
|---|---|
| `# CONFIG_TARGET_ROOTFS_EXT4FS is not set` | x86 默认还打一份 ext4 根镜像，`make_ext4fs` 按未压缩体积算，224MB 装不下，r9 挂在 `target/linux install`。刷机只用 `*-squashfs-combined-efi.img.gz`，ext4 根镜像用不上 |
| `CONFIG_TARGET_KERNEL_PARTSIZE=32`、`CONFIG_TARGET_ROOTFS_PARTSIZE=512` | 默认 16MB kernel 分区偏紧，root 224MB 不够 |

刷完机少的只是「另一份 ext4 根盘镜像」，LuCI、overlay、扩容不受影响。CI 遇到 `ERROR: target/linux` 会跑 `make target/linux/install -j1 V=s` 并上传 `logs/target`。i915 曾一直被 profile 的 `DEVICE_PACKAGES` 加回（§六 A 档漏网）；2026-10-16 已在 §二十七 钉 `# CONFIG_PACKAGE_kmod-drm-i915 is not set`，r20 构建验证是否真的不再进固件。

后续 AI：**不要**再把 `TARGET_ROOTFS_EXT4FS` 打开，也**不要**把 PARTSIZE 改回 224。日志与排查见 [`CI-HISTORY.md`](CI-HISTORY.md) §十七。

## 十八、CI 注解清理（2026-10-10）

已处理，固件零增删：actions 升到 Node 24 版本（`checkout@v5`、`cache@v5`、`upload-artifact@v6`）；`runs-on: ubuntu-24.04` 钉死，不跟 `ubuntu-latest` 切 26；已知未生效项只写 artifact，未知丢失仍 `::error::`。**不要**为消黄条从 seed 删 `kmod-thermal`/`kmod-xdp-sockets-diag`，也**不要**把 warning 加回。明细见 [`CI-HISTORY.md`](CI-HISTORY.md) §十八。

## 十九、Ventoy LiveCD ISO（2026-10-10，N100 16G 傲腾）

用户要把裁剪版装进 N100 机内 **16G 英特尔傲腾**。2026-10-10 晚用户纠正：**上次装官方 iStoreOS 用的就是 img**（`dd`/Etcher 整盘写入），N100 试刷优先走同一套，不必等 ISO。ISO 只是给「非要把文件丢进 Ventoy 菜单」的备选。r10 的 `combined-efi.img.gz` **不要**写进现有 Ventoy 盘（会覆盖 Ventoy），写到另一根普通 U 盘。

OpenWrt/iStoreOS 的 ISO 是 **LiveCD**：从光盘/Ventoy 启动进内存里的系统，**不会**像 Windows 安装盘那样自动写到傲腾。装盘仍然是把 `*-squashfs-combined-efi.img.gz` `dd` 到 NVMe。ISO 只解决「Ventoy 能点开、能进系统」。

x86_64 内核已 `CONFIG_BLK_DEV_NVME=y`，不必往 seed 加 `kmod-nvme`。镜像未压缩大约 kernel 32M + root 512M + 预置 2G 数据分区，16G 傲腾装得下；多出来的空间首次启动后若没自动扩，再手动扩 overlay。

### 功能视角

| 变更后能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：把 `*-image-efi.iso` 拷进 Ventoy 盘，菜单里启动进裁剪版（Live） | `CONFIG_ISO_IMAGES=y` | N100 关 Secure Boot；U 盘一直插着才是这套 Live |
| **能**：Live 里把 `*-squashfs-combined-efi.img.gz` dd 到傲腾，拔掉 U 盘从傲腾开机 | 仍用 combined-efi，不是 ISO 自己写入 | 傲腾上原有数据全没。认盘名：`lsblk` 看 `nvme0n1`，别 dd 到 Ventoy 那块盘 |
| **不能**：指望 ISO 图形安装向导 | OpenWrt 没有 | 命令见下 |
| **不能**：把 img.gz 拷进现有 Ventoy 盘当菜单项指望稳妥启动 | 整盘镜像 PARTUUID 常对不上 | 另找普通 U 盘 `dd` 整盘，与上次装官方相同 |

### 包名 / 文件明细

| 动作 | 内容 |
|---|---|
| seed 新增 | `CONFIG_ISO_IMAGES=y`（kconfig 文案就是 Build LiveCD） |
| apt 新增 | `genisoimage`（打 ISO 要 mkisofs；缺了 `target/linux` 才会报 Please install mkisofs） |
| CI 上传 | `bin/targets/x86/64/*.iso`；顺手把 `manifest` 改成 `*.manifest`（r10 那份清单没传上来） |
| 产物 | `*-x86-64-generic-image-efi.iso`（Ventoy）+ 原来的 `*-squashfs-combined-efi.img.gz`（dd 到傲腾）。两份都要拷到 Ventoy 盘 |

Live 里安装（U 盘是 Ventoy、傲腾是 nvme0n1 时）：

```bash
lsblk
# 确认傲腾是 nvme0n1、Ventoy 不是这块
gzip -dc /mnt/…/istoreos-*-squashfs-combined-efi.img.gz | dd of=/dev/nvme0n1 bs=4M
reboot
```

拔掉 U 盘，BIOS 从 NVMe 启动。16G「傲腾内存」条有的只能当 RST 缓存、不能当系统盘，BIOS 里关掉 Intel RST / 设成 AHCI 或 NVMe 直出；若 `lsblk` 根本没有 nvme，这颗条不能当硬盘用。

后续 AI：**不要**把 ISO 写成「安装盘」；**不要**为了 Ventoy 去改 `gen_image_generic.sh` 里写死的 2G 数据分区（那是源码）。J4125 仍刷 combined-efi 整盘，不走这条 Live 安装。

## 二十、移除 Aria2 / Transmission（2026-10-10，用户明确要求）

用户确认路由器不需要本地下载器：Aria2、Transmission、qBittorrent、Samba 和易有云均不作为网关服务；OpenList 的 WebDAV 保留，继续负责现有文件访问。这样下载和文件访问职责分开，网关不再常驻下载任务、BT 连接和下载管理页面。

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 在路由器上用 Aria2 下载 HTTP/HTTPS/FTP/SFTP 直链、磁力或 BT 任务 | aria2、aria2-openssl、ariang、Aria2 LuCI 页面 | 需要下载时改在 9400F 或其他服务器运行下载器；OpenList WebDAV 仍可访问已有文件 |
| 在路由器上运行 Transmission 常驻 BT、做种、队列和分享率管理 | transmission-daemon、transmission-web-control、Transmission LuCI 页面 | 不再由网关承担 BT 长连接、磁盘 I/O 和上传；需要 PT/做种时放到服务器 |
| 在路由器首页和 LuCI 菜单看到上述下载应用入口 | 对应 LuCI 页面、中文语言包及固件内入口 | iStore 商店本体保留；不删 iStore 本身 |
| 通过 Samba 或易有云提供文件共享/同步 | 首轮已删的 Samba/LinkEase 系 | OpenList WebDAV 是保留的文件访问方式 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除 | aria2、aria2-openssl、ariang、luci-app-aria2、luci-i18n-aria2-zh-cn |
| 从 config-custom.seed 删除 | transmission-daemon、transmission-web-control、luci-app-transmission、luci-i18n-transmission-zh-cn |
| 保留 | openlist、luci-app-openlist、luci-i18n-openlist-zh-cn；OpenList WebDAV 不随本批删除 |
| 已确认不在当前 seed | qbittorrent*、samba4-*、luci-app-samba4、linkease、luci-app-linkease、ddnsto* |

app-meta-aria2、app-meta-transmission、aria2-entry-deps、transmission-daemon-openssl 属于 iStore 商店应用的元数据/入口，早前清理死行时已经不在当前 seed；本次不改 iStore 商店源，也不删除 OpenList 或商店本体。

## 二十一、移除在线升级 OTA（2026-10-12，用户明确要求）

本仓库已脱离官方发布节奏，固件只从自己的 CI 出。`luci-app-ota` 检查和下载的是 `fw.koolcenter.com` 上的**官方完整版**，在裁剪版上点「升级」会把整台机器刷回官方镜像，裁剪全部作废——留着它不仅没用，还是一个误操作入口。

用户同时问过 WireGuard、网络唤醒、备份与升级：这三项与上游同步无关，当时**全部保留**。网络唤醒用来叫醒 9400F/N100；备份与升级是 `luci-mod-system` 自带页面，刷机前导出 `/etc/config`、本地上传自编镜像都靠它。**（WireGuard 已于 2026-10-17 删除——用户改口远程只走 Tailscale，见 §二十九；下表「保留」行的 kmod-wireguard/wireguard-tools/luci-proto-wireguard 同此。）**

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 在 LuCI「系统 → OTA」里在线检查、下载并刷入新固件 | luci-app-ota 及中文包 | 新固件从本仓库 Actions 下载 `*-combined-efi.img.gz`（或 sysupgrade 包），在「系统 → 备份与升级」本地上传刷入 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除 | luci-app-ota、luci-i18n-ota-zh-cn |
| 保留 | curl（不是 OTA 独占）；kmod-wireguard、wireguard-tools、luci-proto-wireguard；luci-app-wol、etherwake 及中文包；luci-mod-system（备份与升级） |

`package/istoreos-files` 的 postinst 仍会 sed 一次 `controller/admin/ota.lua`；文件不在时 sed 只打一行 stderr，该块不带 `set -e` 且以 `true` 收尾，不影响打包。不改它，守「不改源码」。

## 二十二、内置最新 Tailscale（2026-10-14，用户明确要求）

r13 固件里已经有 Tailscale **守护进程**，但是 packages feed（`jjm2473/packages@istoreos-24.10`）钉在 **1.80.3**。用户要求开箱即有、并且用最新稳定版。

不能从源码编最新版：本树 golang 是 **1.23.12** 且 `GOTOOLCHAIN=local`。Tailscale 1.80.3 要 Go 1.23.1（能编）；1.82.0 起要 1.24；**1.104.1（2026-10-07 最新稳定）要 Go 1.27.1**。升 golang 会牵动所有 Go 包（含已钉死的 DDNS-Go v6.12.2），r8 已经为此炸过一次，见 §十五。本 fork 只做 x86_64，所以改为装 **官方 amd64 预编译**，不改 packages 源码树。

LuCI 配置页 `luci-app-tailscale-community` 仍是商店应用、六个默认 feed 里没有符号（§九）。这次不拉 app-hub，只在 defconfig 前把 **asvow/luci-app-tailscale v1.2.6** 克隆进构建树（和 vlmcsd 补丁一样，副本不进 git）。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：刷完机就是 Tailscale 1.104.1，LuCI 里有配置页，可作 exit node | 官方 `tailscale`/`tailscaled` amd64 + `luci-app-tailscale` + 中文包 | 账号、auth key 仍要用户自己登；不预置密钥 |
| **仍不能**：用本树 Go 从源码编 1.82+ | 不升 `feeds/packages/lang/golang` | 要换更新的官方 tgz：改 `.github/scripts/pin-tailscale-prebuilt.sh` 里的版本和 HASH |
| **仍不能**：开箱即有 OpenClash 等其它商店应用 | 未改 app-hub、未改 §十 | 刷机后商店装回，与本次无关 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 构建脚本（feeds install 之后、defconfig 之前） | `.github/scripts/pin-tailscale-prebuilt.sh`：把 `package/feeds/packages/tailscale` 换成官方 `tailscale_1.104.1_amd64.tgz`（sha256 `108d1d96ecf410d305571e173516f27038f870919a9b89c914a167c6d33a4528`）；只装两个二进制。init/config 由 asvow LuCI 提供。`git clone --branch v1.2.6` asvow/luci-app-tailscale 到 `package/luci-app-tailscale` |
| seed 新增 `=y` | `luci-app-tailscale`、`luci-i18n-tailscale-zh-cn`（seed `CONFIG_PACKAGE_*` 585 → 587） |
| seed 原本就有、未删 | `tailscale`（守护进程；二进制由脚本换成 1.104.1） |
| 不加 | `luci-app-tailscale-community`（商店包，无 kconfig，写了也是死行）；不升 golang |

后续 AI：**不要**为了「最新 Tailscale」去升 packages 的 golang；**不要**把 asvow 这一包扩成整个 app-hub；换更新的官方版本只改脚本里的 `TS_VERSION` / `TS_HASH`。本地编也必须跑这支脚本，见 `BUILD-CUSTOM.md` 步骤 3c。

## 二十三、QuickStart 首页（不要 Samba/易有云/下载器，2026-10-16，用户明确要求）

r17 及更早镜像登录后是 LuCI Argon 概览，不是官方那种彩色首页。不是分支选错：`custom-24.10` 跟踪的就是 `istoreos-24.10`；用户截图来自家用 J4125 上的**官方整包**，那里从 iStore 商店装了 QuickStart。

六个默认 feed 里没有 `luci-app-quickstart`（§九）。2026-10-06 不装回，是因为首页会带下载器、Samba、易有云卡片；用户当时选镜像尺寸优先。2026-10-16 改口：**要这个首页，但那些已删服务不能跟着回来。**

不把 `linkease/nas-packages` 整仓写进 `feeds.conf`（会露出 samba/linkease 等符号）。第三条构建例外只 clone 两个包，和 Tailscale LuCI 同一套路。

首页卡片怎么处理：

| 区块 | 做法 | 原因 |
|---|---|---|
| 左侧菜单「网络向导」 | 保留（`luci-app-quickstart` 自带 `admin/network_guide`，补丁禁止动 controller） | 官方侧栏第二项；r17 没有 QuickStart 才看不见 |
| 首页卡片：网络向导 / 局域网设备 / 测速 / **家长控制** / 商店 / 内网·DNS·日志·终端 | 保留。家长控制官方要等 `luci-app-oaf` 装上才画，补丁改成始终显示 | 2026-10-17 用户明确这块有用。点击仍走商店装 `luci-app-oaf`（应用过滤），不烘焙 |
| 磁盘信息 | 保留 | 只读概览，不是 Samba |
| Docker | 前端已按 `/etc/init.d/dockerd` 是否存在决定；本镜像没有 dockerd，卡片不出现 | 不装 Docker |
| 固件更新 / 沙箱 | 前端已按 `ota` 二进制、`/ext_overlay` 决定；本镜像都没有 | OTA 已删（§二十一） |
| 侧栏「网络存储」→ 磁盘阵列 / S.M.A.R.T. | 从 `quickstart.lua` 删除这两条 `entry`，父菜单随子项消失；Makefile 保留官方四项（含 `smartd`） | 不要这些页。首页磁盘信息要 smartctl+smartd+mdadm，见 §三十二～§三十五 |
| 侧栏「系统 → 挂载点」 | `pin-quickstart.sh` 往 luci-app-quickstart 的 menu.d 写 `admin/system/mounts` `enabled: false` | 无数据盘。`luci-mod-system` 不能删（备份与更新在里面）。见 §三十一 |
| 存储服务 | 模块加回首页；**只留 WebDAV 卡片**，易有云 / Samba 从该模块渲染删除（不留空位） | 2026-10-17 改口：用户只要这块里的 WebDAV。卡片走商店 `gowebdav`（`auto_setup` 允许）；OpenList 自带 WebDAV 仍在，是另一条入口 |
| 下载服务（Aria2 / Transmission） | 从首页渲染删除 | §二十 |
| 远程域名（ddnsto） | 从首页渲染删除 | 公网走 DDNS-Go，禁止 ddnsto |
| 点「快速配置」从商店装回 Samba / 易有云 / 下载器 / Docker / ddnsto | `auto_setup.sh` 拒绝 | 即使用户以后从别处进向导，也不能把已删服务装回来。`gowebdav` 允许 |

`quickstart` 的 Makefile 声明依赖 `mdadm`/`smartd` 等磁盘工具。二次裁剪和 §三十 从 seed 拿掉它们之后，r28 仍被 defconfig 加回。之后拆掉 smartd 想只藏菜单，r32 首页磁盘信息一直转圈；§三十五 改口：`smartd` 加回查询链路，侧栏 RAID/SMART 仍删。不要为了「首页」去改 `package/istoreos-files` 源码。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：登录就是官方那种 QuickStart 首页；侧栏有「首页」和「网络向导」 | `quickstart` + `luci-app-quickstart` + 中文包 | 不再默认停在 Argon 状态概览；网络向导走 `admin/network_guide` |
| **能**：首页看到「存储服务」，里面只有 WebDAV | `pin-quickstart.sh` 加回 storage 模块并删掉易有云/Samba 卡片 | 点配置会走商店 `gowebdav`（未烘焙，刷机后按需装） |
| **能**：首页快捷入口看到「家长控制」 | 去掉「未装 oaf 不渲染」判断 | 点进去商店装 `luci-app-oaf`；不把 oaf 烘焙进固件 |
| **仍不能**：侧栏看到「网络存储 / 磁盘阵列 / S.M.A.R.T.」 | 删 controller 菜单 | 无数据盘不要这些页。`smartd` 后台要留给出首页磁盘信息（§三十五） |
| **仍不能**：侧栏看到「系统 → 挂载点」 | pin-quickstart 写 menu.d 关掉 | 无数据盘（§三十一）；`block-mount` 仍在 |
| **仍不能**：在首页看到或配置 Samba / 易有云 / Aria2 / Transmission / ddnsto | 这些卡片从渲染删除 + auto_setup 拒绝名单 | 文件服务用 9400F/N100；公网域名用 DDNS-Go；OpenList WebDAV 用 OpenList 自己的页面 |
| **仍不能**：开箱即有 OpenClash 等其它商店应用 | 未改 app-hub、未改 §十 | 刷机后商店装回，与本次无关 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 构建脚本（feeds install 之后、defconfig 之前） | `.github/scripts/pin-quickstart.sh`：sparse clone `linkease/nas-packages@c82c458b61e5` 的 `network/services/quickstart`（预编译 0.13.0）到 `package/quickstart`；sparse clone `linkease/nas-packages-luci@7e5083e2ca4c` 的 `luci/luci-app-quickstart`（0.12.10-r1）到 `package/luci-app-quickstart`。再改构建树副本：首页保留 diskInfo + storage，从渲染删除 docker/downloadService/remoteDomain；存储服务模块里删除易有云/Samba 卡片，默认打开 WebDAV，「配置存储服务」走 `gowebdav`；设置列表保留 storage、去掉下载/远程域名；快捷入口「家长控制」未装 oaf 也显示；controller 删除 RAID/SMART 菜单；Makefile **保留** `+smartmontools +smartd +smartmontools-drivedb +mdadm`（§三十五）；menu.d 关掉「系统 → 挂载点」（§三十一）；`auto_setup.sh` 拒绝 samba/linkease/aria2/transmission/docker/ddnsto/unishare，**允许 gowebdav**；`disable_update_check=1` |
| seed 新增 `=y` | `quickstart`、`luci-app-quickstart`、`luci-i18n-quickstart-zh-cn`（seed `CONFIG_PACKAGE_*` 587 → 590） |
| defconfig 可能自行加回 | `smartd`/`smartmontools`/`mdadm` 是有意留下的（审计缺了就红）。`mdadm` 可能顺带拉回 `kmod-md-*`，不是侧栏 |
| 不加 | 整个 nas-packages / app-hub；`app-meta-samba`、linkease、aria2、luci-app-ota、ddnsto |

后续 AI：**不要**把 nas-packages 写成第七/八条 feed；升 QuickStart 版本只改脚本里的 `NAS_COMMIT` / `LUCI_COMMIT` / `QS_VERSION` / `LUCI_VERSION`，前端字符串对不上就让 CI 红、不要猜着补。本地编也必须跑这支脚本，见 `BUILD-CUSTOM.md` 步骤 3d。

## 二十四、去掉 Bootstrap 第二主题（2026-10-16，用户明确要求）

LuCI 默认集合 `luci-light` 的 `DEPENDS` 带 `+luci-theme-bootstrap`。只从 seed 删 `CONFIG_PACKAGE_luci-theme-bootstrap=y`，`make defconfig` 会把它加回来，镜像里还是两个主题。

界面已经用 Argon（`istoreos-files` 依赖 `luci-theme-argon`，`99_theme` 默认切过去）。用户只要这一个，不要系统里再出现 Bootstrap。

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 在「系统 → 语言和界面」里切到 Bootstrap 主题 | `luci-theme-bootstrap` | 只留 Argon；配色仍走 `luci-app-argon-config` |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除 | `luci-theme-bootstrap`（seed `CONFIG_PACKAGE_*` 590 → 589） |
| 构建脚本（feeds install 之后、defconfig 之前） | `.github/scripts/drop-luci-theme-bootstrap.sh`：从 `luci-light` Makefile 去掉 `+luci-theme-bootstrap` |
| 审计 | `seed-audit.sh`：展开后的 `.config` 若再出现 `CONFIG_PACKAGE_luci-theme-bootstrap=y` 则失败 |
| 保留 | `luci-theme-argon`、`luci-app-argon-config` 及中文包 |

后续 AI：**不要**只删 seed 那一行就以为主题没了；本地编也必须跑这支脚本，见 `BUILD-CUSTOM.md` 步骤 3e。**不要**改 `package/istoreos-files` 里的 `99_theme`（源码）。

## 二十五、构建产物自动发 GitHub Releases（2026-10-16，用户明确要求）

r17 及更早的镜像只挂在 Actions 的 artifact 上：**14 天过期**，下载还要登录 GitHub。用户要求把构建产物放到 Releases 长期可下载。

### 功能视角

| 变更后能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：在仓库 Releases 页直接下载每轮镜像（tag `r<run_number>`），长期有效、无需登录 | workflow 新增 Publish 步骤（`gh release create`） | artifact 上传保留（14 天，供 run 页快速取）；不改变固件内容 |
| **仍不能**：在固件里在线升级 | OTA 已删（§二十一） | 下载 `*-squashfs-combined-efi.img.gz` 解压后整盘写入，或在「系统 → 备份与升级」本地上传 |

### 明细

| 动作 | 内容 |
|---|---|
| workflow 新增 | `build-istoreos.yml`：job 申请 `permissions: contents: write`（仓库全局默认仍是 read，没动它）；`Upload images` 之后新增 `Publish to GitHub Releases`（`if: success()`），`gh release create r<run_number>` 上传 `*.img.gz`、`*.iso`、`sha256sums`、`*.manifest`，tag 锚定被构建的提交；同一 run 重跑用 `gh release upload --clobber` 覆盖 |
| 仅手动触发 | 构建入口仍只有 workflow_dispatch；Release 是产物去处，不是触发器 |

后续 AI：**不要**为发 Release 去改仓库全局默认权限；**不要**把 Release 当作「已刷机验证」的证据——机器验证仍按 `BUILD-CUSTOM.md` 流程走。

## 二十六、杂项零头清收（2026-10-16，用户明确要求）

用户要求「先把杂项的依赖包删了」——即「还能删什么」审查里最小无争议的一组：并口、SCTP、TPM 密钥环、网卡 VF、iptables physdev 桥接匹配；连带拉入的 `kmod-br-netfilter` 随之消失。这是分批瘦身的第一批，其余组（显示栈、非保险网卡、隧道群、工具）待逐批确认后另行记录。

本批**未经路由器 `opkg whatdepends`**，依据是本地构建树的反向依赖静态核查：这 7 个包的依赖者在构建树里全部未启用或同批删除（`iptables-mod-physdev`、`kmod-usb-serial-mos7720`、`parport-pc`、`lp`、`sctp-diag`、`tpm-tis`/`tpm-i2c`/`tpm-spi`；`kmod-keys-encrypted` 依赖 `kmod-keys-trusted`，同批一起删），且它们都不在 x86/64 的 `DEVICE_PACKAGES` 里。CI seed 审计兜底：若 feeds 里还有构建树外、本地看不到的隐藏依赖，`defconfig` 会把被依赖项加回，并出现在审计报告「seed 没写却开启」列表里，按报告处理即可。体积收益不大（都是小模块），价值在于去掉无场景功能、保持 seed 精简。

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 接并口（老式打印机）设备 | `kmod-ppdev` | 无此场景；依赖它的 `kmod-usb-serial-mos7720`、`parport-pc`、`lp` 都没进固件 |
| 跑 SCTP 协议 | `kmod-sctp` | 家庭网络无此用途；`sctp-diag` 没进固件。要时从 opkg/iStore 装回 |
| 使用内核 TPM 密钥环（trusted / encrypted keys） | `kmod-tpm`、`kmod-keys-trusted`、`kmod-keys-encrypted` | J4125 无 TPM 芯片；接口驱动（`tpm-tis` 等）都没进固件。无影响 |
| 给 SR-IOV 虚拟机分配 Intel 网卡 VF | `kmod-igbvf` | KVM 早已删（§六）；换物理网卡走保险驱动（`kmod-igb` 还在），不受影响 |
| 用 iptables `-m physdev` 匹配桥接物理口 | `kmod-ipt-physdev`、连带 `kmod-br-netfilter` | fw4/nftables 不使用；唯一依赖者 `iptables-mod-physdev` 没进固件。要时装回它会把两者一起拉回 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除（7 行；seed `=y` 计数 589 → 582） | `kmod-igbvf`、`kmod-ipt-physdev`、`kmod-keys-encrypted`、`kmod-keys-trusted`、`kmod-ppdev`、`kmod-sctp`、`kmod-tpm` |
| 连带自动消失（本不在 seed，由依赖拉入） | `kmod-br-netfilter`（构建树里唯一来源是 `kmod-ipt-physdev` 的 DEPENDS，`package/kernel/linux/modules/netfilter.mk:847`） |
| 保留 / 勿动 | `kmod-udptunnel4/6`——WireGuard 硬依赖（`netsupport.mk:1555`），**不是**零头；`kmod-i2c-algo-bit`/`kmod-i2c-core`/`kmod-ptp`——igb/igc 保险网卡需要 |

后续 AI：**不要**把上面「勿动」两项当零头再删；若后续 seed 审计的「seed 没写却开启」里新出现本批包名，说明有隐藏依赖，先查清再决定，不要无视。本批是否真消失，以 r20 构建的审计报告为准。

## 二十七、第二批清收：显示栈 / 摄像头 / 音频 / 隧道群 / 老式交换机 / nbd / 工具 / 非保险网卡（2026-10-16，用户明确要求「继续删，最后一起编」）

§二十六 推送后，用户指示把剩余可删组一次做完，之后只编一轮。本批共从 seed 删 26 行（`=y` 582 → **556**）、钉 8 行 `# ... is not set`（全部是 x86/64 profile `DEVICE_PACKAGES` 塞进来的默认包）。未用路由器 `opkg whatdepends`，依据与 §二十六 相同（本地构建树反向依赖核查 + CI 审计兜底，逐项见文末）。

### 功能视角

| 变更后设备不能再做什么 | 本批动的东西 | 影响 / 替代方案 |
|---|---|---|
| 用 i915 核显做显示/视频加速 | `kmod-drm-i915` 钉关（连带 drm/fb/backlight/acpi-video/i915-firmware 全链消失） | 纯网关无此场景；OpenWrt x86 内核本就 `CONFIG_VT=n`，接显示器也不会有控制台。要恢复须从 seed 撤钉重编（kmod 与固件内核绑定，不能只 opkg 装回） |
| 插 USB 摄像头拍图/视频 | `kmod-video-core`、`kmod-video-uvc`、`kmod-video-videobuf2`、`kmod-media-controller`、`kmod-dma-buf` | 无此场景；恢复方式同上（撤行重编） |
| 插 USB 声卡（内核音频） | `kmod-sound-core`、`kmod-usb-audio` | 同上 |
| 用 DS-Lite / MAP / SIT 等 IPv6 过渡隧道 | `ds-lite`、`map`、`kmod-sit`、`kmod-ip6-tunnel`、`kmod-iptunnel6`、`kmod-nat46`、`kmod-siit`（连带隐藏 `kmod-iptunnel`/`kmod-iptunnel4` 消失） | 原生 IPv6 不受影响（odhcp6c/odhcpd 留）；6in4/6to4/6rd 本来就没进固件 |
| 配置老式交换机芯片（家用路由 SoC 那种） | `kmod-swconfig`、`kmod-switch-ip17xx`、`kmod-switch-rtl8306`、`kmod-switch-rtl8366-smi`、`kmod-switch-rtl8366rb`、`kmod-switch-rtl8366s`、`kmod-switch-rtl8367b`、`kmod-spi-ks8995` | x86 无这些芯片；本机 4 口是 igc 直连 |
| 用 nbd 网络块设备 | `kmod-nbd` | 无此用法 |
| 用 htop / strace 诊断 | `htop`、`strace` | `tcpdump` 保留；htop/strace 是纯用户态，可 opkg/商店装回 |
| 用华为 LTE 棒（cdc-ncm 模式）上网 | `kmod-usb-net-huawei-cdc-ncm` | 其他 USB 网卡 / 手机共享（rndis/ipheth/cdc-*）仍留 |
| 换用 Broadcom / 10G 等非保险网卡 | 钉关 `kmod-tg3`、`kmod-ixgbe`、`kmod-bnx2`、`kmod-amd-xgbe`、`kmod-amazon-ena`、`kmod-forcedeth`、`kmod-dwmac-intel` | 保险网卡定型：`kmod-igc`（本机）＋ `kmod-e1000`/`kmod-e1000e`/`kmod-igb`/`kmod-r8125`/`kmod-r8169` ＋ USB 网卡保留；要换的卡不在其中时从 seed 撤钉重编 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 删行（26 行） | `ds-lite`、`map`、`htop`、`strace`、`kmod-dma-buf`、`kmod-ip6-tunnel`、`kmod-iptunnel6`、`kmod-media-controller`、`kmod-nat46`、`kmod-nbd`、`kmod-siit`、`kmod-sit`、`kmod-sound-core`、`kmod-spi-ks8995`、`kmod-swconfig`、`kmod-switch-ip17xx`、`kmod-switch-rtl8306`、`kmod-switch-rtl8366-smi`、`kmod-switch-rtl8366rb`、`kmod-switch-rtl8366s`、`kmod-switch-rtl8367b`、`kmod-usb-audio`、`kmod-usb-net-huawei-cdc-ncm`、`kmod-video-core`、`kmod-video-uvc`、`kmod-video-videobuf2` |
| 钉关（8 行 `is not set`，均为 x86/64 profile 默认包） | `kmod-amazon-ena`、`kmod-amd-xgbe`、`kmod-bnx2`、`kmod-drm-i915`、`kmod-dwmac-intel`、`kmod-forcedeth`、`kmod-ixgbe`、`kmod-tg3` |
| 预期连带消失（本不在 seed） | 显示全链 drm/fb/backlight/`i915-firmware-{dmc,guc,huc}` 等、`bnx2-firmware`、`stmmac-core`、`pcs-xpcs`、隐藏 `kmod-iptunnel`/`kmod-iptunnel4`——以 r20 审计实际为准 |
| 保留 / 勿动 | `kmod-udptunnel4/6`（WireGuard 硬依赖）、保险网卡 `kmod-igc`/`kmod-e1000`/`kmod-e1000e`/`kmod-igb`/`kmod-r8125`/`kmod-r8169`、`kmod-i2c-algo-bit`/`kmod-i2c-core`/`kmod-ptp`（igb/igc 需要）、`kmod-mdio`/`kmod-mdio-devres`（r8169 等在用）、`tcpdump`、`openssh-sftp-server`（scp 需要它） |

### 依据（本地构建树反向依赖核查摘要）

- **钉关项为什么改 seed 就能生效**：`DEVICE_PACKAGES` 走「设备符号 `select DEFAULT_<pkg>` ＋ 包侧 `default y if DEFAULT_<pkg>`」（`scripts/target-metadata.pl`、`scripts/package-metadata.pl`），`default` 撼不动 .config 里的显式 `is not set`（同 dnsmasq 先例）；且反向核查确认没有任何启用包以 `+` 依赖（=select）这些包本身——唯一引用 `kmod-ixgbe` 的 `kmod-ixgbevf` 未启用。
- **删行项**：`+kmod-*` 反向依赖均无启用者——`kmod-media-controller` 仅被 `kmod-video-core`/`kmod-usb-audio` 引用（同批删）；`kmod-dma-buf` 仅被 drm 与 `kmod-video-videobuf2` 引用（钉/删）；`kmod-sit`（引用者 6in4/6to4/6rd）、`kmod-ip6-tunnel`（ds-lite/map/ipsec6/mlxsw 等）、`kmod-iptunnel6`（ip6-tunnel/ipsec6）在本批之外全未启用；`kmod-swconfig` 的引用者全在本批删除集；`kmod-nbd`、`kmod-siit`、`kmod-usb-audio`、`kmod-usb-net-huawei-cdc-ncm` 无任何引用者。
- **kmod 与用户态的区别**：htop/strace 可 opkg/商店装回；kmod 与固件内核 ABI 绑定，恢复方式是从 seed 撤行重编。

后续 AI：r20 构建后先看审计——「预期连带消失」没消失、或「seed 没写却开启」新增本批包名，说明有构建树外（feeds）的隐藏依赖，按报告再修；**不要**把「保留 / 勿动」里的东西当零头再删。

## 二十八、第三批清收：crypto 残留 / Broadcom PHY / USB 外设 / 杂项（2026-10-17，用户指挥执行器重审、Claude 验收）

用户要求「指挥 DeepSeek 重新做一遍审计，Claude 验收」。审计由 opencode 免费模型 `deepseek-v4.1-flash-free` 做（只读，read/glob/grep；它跑不了命令，审计也不需要）。它交回约 40 行候选，Claude **逐条拿本地构建树重新坐实**后，这批落 23 行（r21 审计再带出 3 行孤儿，合计 26 行，见文末「r21 连带」）、保留两组、留一组后续。未用路由器 `opkg whatdepends`，依据是本地构建树反向依赖核查（`+kmod-*` select + `imply`）+ CI 审计兜底，与 §二十六/§二十七 相同。

执行器出网说明：DeepSeek 本轮用 opencode 的沙箱 JS 工具发了网络请求（grep.app/sourcegraph/openwrt downloads 查用户态库反向依赖）。其网取结论 Claude **一律未采信**，只当线索；进本节的 23 行每条都有本仓库 `.mk` 内证据。opencode 的 `permission` 键里没有管沙箱 JS 的项，堵口子改用 `tools` 开关，见 skill 侧 `opencode-delegate.json`。

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 跑 MPPE/PPTP、NFS-krb5、CIFS、IPsec、rxrpc、无线 TKIP 的内核加密 | `kmod-crypto-{arc4,cts,des,echainiv,fcrypt,michael-mic,pcbc}` | 这些协议本就不在固件（mppe/ipsec/rxrpc/fs-cifs/fs-smb-server/fs-nfs-common-rpcsec/ath10k·11k 均未启用）；WireGuard 用的 crypto 链（curve25519/chacha20/poly1305/ecb/ctr/gcm 等）全保留 |
| 换 Broadcom 网卡 / 用 BCM84881 PHY | `kmod-phy-bcm84881`、`kmod-phy-broadcom`、`kmod-phylib-broadcom` | tg3/bnx2 已 §二十七 钉关，这三条是配套 PHY 的尾巴；保险网卡（igc/e1000e/igb/r8169/r8125）的 PHY（realtek/microchip 等）保留 |
| 接 USB VoIP 话机 / USB 打印机 / CP2112 调试桥 / USB 蜂窝棒(QMI·MBIM) / USB 硬件 RNG | `kmod-usb-cm109`、`kmod-usb-printer`、`kmod-usb-hid-cp2112`、`kmod-usb-wdm`、`kmod-chaoskey` | 纯网关无这些外设；熵源用 urngd/getrandom。要时撤行重编（kmod 与内核绑定） |
| 在 ARM/SoC 用 DWC2/DWC3 USB 控制器 | `kmod-usb-dwc2`、`kmod-usb-dwc3`、`kmod-usb-roles` | x86 USB 走 xhci/ehci/uhci/ohci；dwc 只服务 ARM/SoC target，roles 删 dwc 后成孤儿 |
| 用 AMD 加密协处理器 / binfmt_misc 注册可执行格式 / GPIO 位拨 MDIO / SPI 挂 MMC 卡 | `kmod-crypto-hw-ccp`、`kmod-fs-binfmt-misc`、`kmod-mdio-gpio`、`kmod-mmc`、`kmod-mmc-spi` | CCP 是 AMD 专用（本机 Intel）；binfmt_misc 是 qemu-user/Java 场景；mdio-gpio/mmc 是嵌入式/无线驱动才用，x86 无 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除（23 行；seed `=y` 556 → 533） | `kmod-chaoskey`、`kmod-crypto-arc4`、`kmod-crypto-cts`、`kmod-crypto-des`、`kmod-crypto-echainiv`、`kmod-crypto-fcrypt`、`kmod-crypto-hw-ccp`、`kmod-crypto-michael-mic`、`kmod-crypto-pcbc`、`kmod-fs-binfmt-misc`、`kmod-mdio-gpio`、`kmod-mmc`、`kmod-mmc-spi`、`kmod-phy-bcm84881`、`kmod-phy-broadcom`、`kmod-phylib-broadcom`、`kmod-usb-cm109`、`kmod-usb-dwc2`、`kmod-usb-dwc3`、`kmod-usb-hid-cp2112`、`kmod-usb-printer`、`kmod-usb-roles`、`kmod-usb-wdm` |
| r21 审计连带再删（3 行；seed `=y` 533 → 530） | `kmod-crypto-rsa`（selector 只有 crypto-engine〔不在 seed〕和本批删的 crypto-hw-ccp）、`kmod-asn1-encoder`（唯一 selector 是 §二十六 删的 kmod-tpm）、`kmod-mdio`（裸 mdio，selector 全是老式网卡与本批删的 broadcom 链；保险网卡 r8169 用 `kmod-mdio-devres`、igb/igc/e1000e 不碰 mdio） |
| 评估后**保留**（候选但不删） | HID 输入簇 `kmod-hid`/`kmod-hid-generic`/`kmod-usb-hid`/`kmod-input-core`/`kmod-input-evdev`（无头网关虽无键鼠，但保留 USB-HID 兜底能力）；unetd 全家 `unetd`/`unet-cli`/`luci-proto-unet`（与 WireGuard+Tailscale 重叠，但用户选择保留 unet mesh 能力） |
| 留后续 | `kmod-usb-uhci`、`kmod-usb-ohci`、`kmod-usb-ohci-pci`——真机 J4125 USB 走 xhci/ehci 用不到，但 QEMU 老 i440fx 机型的 USB 控制器是 UHCI/OHCI，删了影响 QEMU 启动验证。等验证流程确认后再定 |
| 保留 / 勿动（本批核查确认承重） | ~~`kmod-crypto-kpp`——`kmod-crypto-lib-curve25519`（WireGuard 在用）有 `imply`，删了会被回加~~ **（§二十九 删 WireGuard 后 curve25519 一并删、imply 失效，kpp 已随之删除）**；`kmod-net-selftests`（usb-net-asix/smsc95xx 依赖）；`kmod-phy-realtek`/`kmod-phy-microchip`/`kmod-phy-ax88796b`/`kmod-phy-smsc`（保险网卡 PHY） |

### 依据（本地构建树反向依赖核查摘要）

- **crypto 残留 7 条**：`+kmod-crypto-{arc4,cts,des,echainiv,fcrypt,michael-mic,pcbc}` 的引用者——`mppe`(netsupport.mk:698)、`ipsec`(netsupport.mk:213)、`rxrpc`(netsupport.mk:1337/1341)、`fs-cifs`(fs.mk:126)、`fs-smb-server`(fs.mk:377)、`fs-nfs-common-rpcsec`(fs.mk:496-503)、`ath10k/ath11k`(mac80211/ath.mk:312/364)——在 seed 内**无一启用**；其余引用全在别的 target（lantiq/ixp4xx/stm32）不进 x86。七条均无 `imply` 回加路径、不在 x86 `DEVICE_PACKAGES`，是干净删行。
- **Broadcom PHY 三连**：`+kmod-phy-bcm84881` 与 `+kmod-phy-broadcom` 全树无引用者；`+kmod-phylib-broadcom` 唯一引用者是 `kmod-phy-broadcom`（netdevices.mk:317）——自封闭孤岛。
- **USB 外设**：`+kmod-usb-wdm` 的引用者 usb-net-qmi-wwan/cdc-mbim/huawei-cdc-ncm 均不在 seed（华为 §二十七 已删）；`+kmod-usb-roles` 只被 dwc2/dwc3（本批删）和 ath79 target 引用；`+kmod-usb-dwc2/dwc3` 引用者全在 ARM/SoC target；cm109/printer/hid-cp2112/chaoskey 无启用引用者。
- **kpp 陷阱确认**：`curve25519` 在 seed（WireGuard 用），其 `imply PACKAGE_kmod-crypto-kpp`（crypto.mk:628）会把 kpp 回加，故 kpp 不能删——这是 DeepSeek 正确逮住、Claude 坐实的一处。

### r21 连带（审计阶段暴露，同轮修）

删 23 行后 run 21（`ad09e0c4fb`，build number 21）在 **Apply custom config** 的 seed 审计红掉：`seed 想要 533 → defconfig 后 lost 3 行`——`kmod-crypto-rsa`、`kmod-asn1-encoder`、`kmod-mdio`（裸）。根因是这 3 个是「被 select 才出现」的库类 kmod，它们的消费者恰好本批（或 §二十六）删光了，defconfig 遂关掉，而 seed 仍写 `=y` → 账实不符，审计按 §十四 阻断（编译未开始，7 分钟即报，未浪费构建时长）。

这不是删错，是上一步漏删的孤儿 `=y`。逐条坐实：`kmod-crypto-rsa` 的 selector 只有 `crypto-engine`（不在 seed）与本批删的 `crypto-hw-ccp`；`kmod-asn1-encoder` 唯一 selector 是 §二十六 删的 `kmod-tpm`；裸 `kmod-mdio` 的 selector 全是老式网卡（alx/bnx2x/sfc…）与本批删的 broadcom 链，保险网卡里 r8169 依赖的是 `kmod-mdio-devres`（非裸 mdio）、igb/igc/e1000e 不碰 mdio。三行一并删，seed 533 → **530**。

**确认无二次级联**：`kmod-asn1-decoder` 仍被 seed 内的 `kmod-nf-nathelper-extra`（netfilter.mk:617）拉住、`kmod-oid-registry` 被 `kmod-fs-nfs-common`（fs.mk:470，可独立开启）拉住，删 rsa/asn1-encoder 后它们不变孤儿，下一轮审计应只剩 `kmod-thermal`/`kmod-xdp-sockets-diag` 两个已知项（不阻断）。

后续 AI：删「被 select 才出现」的 kmod（crypto-*、phy-*、asn1-*、库类）时，要同查它反向拉入的下层库是否也随之失去全部消费者，一并清掉，别留 `=y` 孤儿等审计来报；HID 簇与 unetd 是**有意保留**，不要当零头再删；`kmod-usb-uhci/ohci` 待 QEMU 验证流程确认后另议。

## 二十九、删除 WireGuard + unetd 全家：远程只走 Tailscale（2026-10-17，用户明确拍板）

§二十一/§六 曾把 WireGuard 列为「Tailscale 之外的另一条远程入口，完整保留」。2026-10-17 用户复核后改口：**远程只走 Tailscale**，内核 WireGuard 与 unetd 组网都不再需要（Tailscale 自带 userspace WireGuard，删内核 WireGuard 不影响它）。这触及远程访问能力（本文档「必须先确认」范围），由用户明确拍板。

这是一次级联删除，典型的「删 `kmod-wireguard` 一行会被 unetd 的依赖回加、且连带一串 HIDDEN 库变孤儿」。一次删干净需 **13 行**（显式 6 + 级联 7），逐条反向依赖均已在本地构建树坐实无其他启用消费者。

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 在路由器上建 WireGuard 服务端/接口、家人设备用 WireGuard 客户端直连回家 | `kmod-wireguard`、`wireguard-tools`、`luci-proto-wireguard` | 远程改走 **Tailscale**（exit node，已烘焙 §二十二）；公网仍有 DDNS-Go + 防火墙手动端口转发 |
| 用 unetd 做 WireGuard-based mesh 组网 | `unetd`、`unet-cli`、`luci-proto-unet` | 与 Tailscale 功能重叠，不再保留；要组网用 Tailscale |
| 内核态 WireGuard 的加解密/隧道底座 | 级联库 `kmod-udptunnel4/6`、`kmod-crypto-lib-{chacha20poly1305,chacha20,poly1305,curve25519}`、`kmod-crypto-kpp` | 这些都是 WireGuard 在本固件里唯一消费者的 HIDDEN 库，随之删除 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除（13 行；seed `=y` 530 → **517**） | 显式 6：`kmod-wireguard`、`wireguard-tools`、`luci-proto-wireguard`、`unetd`、`unet-cli`、`luci-proto-unet`；级联 7：`kmod-udptunnel4`、`kmod-udptunnel6`、`kmod-crypto-lib-chacha20poly1305`、`kmod-crypto-lib-chacha20`、`kmod-crypto-lib-poly1305`、`kmod-crypto-lib-curve25519`、`kmod-crypto-kpp` |
| 保留 / 勿动 | `tailscale`＋`luci-app-tailscale`（远程唯一入口，§二十二）、`ddns-go`（公网，§十五）、`firewall4`（端口转发底座）、WireGuard 之外仍有消费者的 crypto 链（ecb/ctr/gcm/sha* 等，被 IPsec 外的多处用）|

### 依据（本地构建树反向依赖核查）

- **显式 6 无外部消费者**：`+kmod-wireguard` 只被 `wireguard-tools`(utils/wireguard-tools:40) 与 `unetd`(services/unetd:35) 引用，两者都在删除集；`+unetd` 只被 `unet-cli`(unetd:58) 引用，也在删除集。删这 6 个不会被谁回加。
- **级联 7 全是 HIDDEN 库、WireGuard 是唯一在固件里的消费者**：
  - `kmod-udptunnel4/6`：其余消费者 vxlan/geneve/fou/l2tp/sctp/rxrpc（netsupport.mk:110/131/421/1188/1256/1342）**无一在 seed**；
  - `kmod-crypto-lib-chacha20poly1305`、`kmod-crypto-lib-curve25519`：全树除 wireguard 外无 `+` 引用者；
  - `kmod-crypto-lib-chacha20`、`kmod-crypto-lib-poly1305`：仅被 chacha20poly1305（本批删）引用；
  - `kmod-crypto-kpp`：真 DEPENDS 消费者 crypto-ecdh/crypto-akcipher/crypto-rsa 均不在 seed，唯一 lifeline 是 `curve25519` 的 `imply`（crypto.mk:628）——curve25519 本批删后 imply 失效，kpp 不再被回加，故一并删（反而消解了 §二十八「kpp 勿删」的前提）。
- **Tailscale 不受影响**：`tailscale` 包（官方 amd64 预编译，§二十二）不依赖 `kmod-wireguard`，远程入口照常。

后续 AI：**不要**再据 §二十一/§六 旧表述把 WireGuard 加回；§二十六/§二十七/§二十八 里「`kmod-udptunnel4/6` 是 WireGuard 硬依赖、勿动」「`kmod-crypto-kpp` 勿删」的注记**已被本节取代**（WireGuard 没了，它们随之删）。远程能力若要恢复 WireGuard，须用户再次明确要求，并连 13 行一起加回。

## 三十、删除 SMART 三件套：网关无数据盘（2026-10-17，用户确认不插盘）

用户确认 J4125 网关**除系统盘外不插任何数据硬盘**（文件服务全在 9400F/N100，WebDAV 存的 Clash 等配置体积小、靠备份而非盘健康监控保护）。`smartd` 是监控物理硬盘 SMART 健康/温度的后台守护，无盘场景下它天天轮询一块不存在或不在乎的盘，是纯冗余。删除三件套。

**辨析**：smartd 管「盘会不会坏」（硬件寿命预警），**不**保护「数据不丢」（那靠备份）；也**不是**温控——温控是 `lm-sensors`+`kmod-hwmon-it87/pwmfan`（读 CPU/主板/风扇），本批**全保留**。

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 后台监控硬盘 SMART 健康、温度，坏盘前告警 | `smartd` | 无数据盘，无监控对象；将来真插盘要监控，从 opkg/iStore 装回 `smartmontools`（含 smartd） |
| 手动 `smartctl` 查盘健康、按型号数据库解读属性 | `smartmontools`、`smartmontools-drivedb` | 同上，装回即有 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除（3 行；seed `=y` 517 → **514**） | `smartd`、`smartmontools`、`smartmontools-drivedb` |
| 保留 / 勿动 | `lm-sensors`+`lm-sensors-detect`、`kmod-hwmon-{core,it87,pwmfan,vid}`、`kmod-thermal`（CPU/风扇温控，与硬盘无关）；`kmod-ata-ahci`/`kmod-scsi-core`（SATA 控制器驱动，无盘也留——ISO LiveCD 与将来插盘需要）|
| 关联候选（无盘，本批**未删**，列备后续） | `kmod-hwmon-drivetemp`（硬盘温度传感器，无盘闲置）；`libcap-ng`（疑似 smartmontools 在固件内唯一消费者，但 feeds 未装、本地读不到其 Makefile，属 §二十八「需 N100 `opkg whatdepends` 验证」档，不盲删）|

### 依据

- 三件套在 **git 树**里没有 `+smartmontools`/`+smartd` 的 DEPENDS（当时 grep 只扫了仓库）。**漏了**：`pin-quickstart.sh` clone 进来的 `quickstart/Makefile` 硬依赖 `+smartmontools +smartd +smartmontools-drivedb +mdadm`，r28 因此又把三件套和 mdadm 编进镜像，侧栏出现「网络存储 / 磁盘阵列 / S.M.A.R.T.」。2026-10-17 晚已在 pin 脚本拆掉这四项 DEPENDS 并删菜单，审计见到 smartd/mdadm=`y` 就红。
- `libcap-ng` 即便真成「编进去没人用」，也是普通包 `=y`、保持开启，**不会**让审计红——所以它是独立的下一步清理候选，不是本批阻断项，等 N100 `opkg whatdepends libcap-ng` 为空再删。

后续 AI：**不要**把 `lm-sensors`/`hwmon-it87`/`pwmfan` 当 SMART 一起删（那是 CPU/风扇温控，不是硬盘）。`smartmontools`/`smartd` 已按 §三十二/§三十五 加回（首页磁盘信息要），**不要**再拆掉；侧栏 SMART 页仍然不要。

## 三十一、删除挂载点和文件传输（2026-10-17，用户明确要求）

用户确认网关不插数据盘、文件服务在 9400F/N100，侧栏「系统 → 挂载点」和「系统 → 文件传输」都用不上。

**挂载点**是 `luci-mod-system` 的 `admin/system/mounts` 页面，和「备份与更新」同一个包。seed 删不掉这一页（删包会把备份/本地刷机入口一起拿掉）。按第三条构建例外，在 `pin-quickstart.sh` clone 出来的 `luci-app-quickstart` 里写一条 menu.d 覆盖，`enabled: false`。`block-mount` / `lsblk` / `parted` 仍留（QuickStart 磁盘信息还要用）。首页磁盘卡片若仍链到 `/cgi-bin/luci/admin/system/mounts`，点进去会没有菜单入口，等磁盘信息那条单独定。

**文件传输**是独立包 `luci-app-filetransfer`（网页把文件传到 `/tmp`，不是 Samba/网盘）。从 seed 删除即可。`openssh-sftp-server` 保留，WinSCP/scp 照旧。

### 功能视角

| 变更后设备不能再做什么 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| 在 LuCI「系统 → 挂载点」里给额外分区配挂载路径 | `luci-mod-system` 的 mounts 菜单（包本身保留） | 无数据盘。真要挂盘：SSH `mount`，或商店装 `diskman` |
| 在 LuCI「系统 → 文件传输」网页上传 ipk/文件到 `/tmp` | `luci-app-filetransfer` 及中文包 | scp / sftp（`openssh-sftp-server` 仍在）或 WinSCP |

### 包名明细

| 动作 | 内容 |
|---|---|
| 从 config-custom.seed 删除（2 行；seed `=y` 514 → **512**） | `luci-app-filetransfer`、`luci-i18n-filetransfer-zh-cn` |
| 构建脚本 | `pin-quickstart.sh` 写入 `package/luci-app-quickstart/root/usr/share/luci/menu.d/drop-system-mounts.json`，关掉 `admin/system/mounts` |
| 审计 | `seed-audit.sh` 若再看到 `luci-app-filetransfer=y` 就红 |
| 保留 / 勿动 | `luci-mod-system`（备份与更新、启动项等）；`block-mount`、`lsblk`、`parted`；`openssh-sftp-server`；`luci-lib-fs`（不随 filetransfer 盲删） |

后续 AI：**不要**为了藏挂载点去删 `luci-mod-system` 或 `block-mount`；**不要**把 sftp 当文件传输一起删。工作区改完时用户要求先不推送、不构建。

## 三十二、首页磁盘信息 loading：加回 smartctl（2026-10-17，用户明确要求修复）

r29 把 QuickStart Makefile 里 `+smartmontools +smartd +smartmontools-drivedb +mdadm` 四项全拆了，侧栏 SMART/RAID 没了，但首页「磁盘信息」一直转圈。这块调的是守护进程 `GET /nas/disk/status/`，预编译二进制要跑 `smartctl`。r28 磁盘信息能出来，是因为当时这四项被 defconfig 加回去了。

用户要修 loading，不要侧栏 SMART、不要 `smartd` 后台轮询。当时只加回 `smartmontools`+`drivedb`，**没加 `mdadm`**。r30 已刷仍 loading，补记于 §三十三。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：首页「磁盘信息」列出系统盘容量/使用，不再一直 loading | `smartmontools`、`smartmontools-drivedb` | 给 QuickStart 调 `smartctl`；不是侧栏 S.M.A.R.T. 页 |
| **仍不能**（当时口径，已被 §三十三 修正）：不装 `mdadm` | r30 因此 RAID 列表一直不返回 | 见 §三十三 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 往 config-custom.seed 加回（2 行；seed `=y` 512 → **514**） | `smartmontools`、`smartmontools-drivedb` |
| 构建脚本 | `pin-quickstart.sh` 把 Makefile 依赖从四项改成只留 `+smartmontools +smartmontools-drivedb` |
| 审计（当时） | 见 §三十三（`mdadm` 改为必须有） |
| 当时不加 | `smartd`（仍不要）；`mdadm` 已改口加回 |

后续 AI：**不要**为了「无数据盘」再把 `smartmontools` 或 `mdadm` 从 seed 拿掉，首页磁盘信息会再转圈。侧栏 RAID/SMART 菜单仍然不要。

## 三十三、首页磁盘信息仍 loading：加回 mdadm（2026-10-18，用户明确要求）

r30 已含 `smartctl`，N100 从闪迪 U 盘启动后首页仍显示「正在获取磁盘信息...」。用户怀疑是外置 U 盘、不是「系统盘那种接法」。不是：那根闪迪就是系统盘（整盘 dd、从它启动），只是走 USB 口。

首页磁盘信息组件 `Promise.all([G.Nas.Disk.Status.GET(), G.Raid.List.GET()])`，两个都返回才结束 loading。缺 `mdadm` 时 `/raid/list/` 不回来，就会一直转。没数据盘时成功文案是「检测不到挂载的磁盘信息，请先插上磁盘」，和「正在获取」不是同一句。U 盘 SMART 最多让 `smartctl` 变慢，不是这句挂死的主因；J4125 机内盘缺 `mdadm` 同样会转。

侧栏「磁盘阵列」仍然不显示（controller 那条 `entry` 已删）。只把查询工具 `mdadm` 加回 seed。`smartd` 仍不要。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：首页磁盘信息等 RAID 列表也能返回，不再因 `/raid/list/` 一直 loading | `mdadm` | 给 QuickStart 调空阵列列表；不是侧栏磁盘阵列页，也不能组 RAID |
| **仍不能**：侧栏「磁盘阵列 / S.M.A.R.T.」；后台 `smartd` 轮询 | 菜单仍删；`smartd` 不在 seed | 无数据盘不需要告警守护 |
| **可能**：成功后仍看到「请先插上磁盘」 | 首页按 NAS 找额外数据盘，系统盘（USB 或机内）常被排除 | 网关不插数据盘时这是空状态，不是 loading |

### 包名明细

| 动作 | 内容 |
|---|---|
| 往 config-custom.seed 加回（1 行；seed `=y` 514 → **515**） | `mdadm` |
| 构建脚本 | `pin-quickstart.sh` Makefile 依赖改为 `+smartmontools +smartmontools-drivedb +mdadm`（仍去掉 `+smartd`） |
| 审计 | `smartd`/`luci-app-filetransfer=y` 仍红；`smartmontools`/`smartmontools-drivedb`/`mdadm` **必须**是 `=y` |
| 不加 | `smartd`；侧栏 RAID/SMART 菜单；不主动写 `kmod-md-*`（mdadm 的 DEPENDS 可能被 defconfig 加回，属查询底座不是组 RAID 页） |

后续 AI：**不要**再把 `mdadm` 当「无盘所以多余」删掉；**不要**为了 `mdadm` 把侧栏磁盘阵列加回来。r31 空白不是缺 mdadm，见 §三十四。

## 三十四、首页磁盘信息空白：等到 Disk.Status（2026-10-18，用户明确要求菜单不要、磁盘信息要）

r28 在 N100 上磁盘信息正常（U 盘 `sda` 系统根目录、使用率），左边仍有「网络存储 / 磁盘阵列 / S.M.A.R.T.」。用户要菜单不要、磁盘信息还要。

r29 同一轮既藏菜单又拆掉 `smartctl`/`mdadm`，卡片一直「正在获取磁盘信息...」。r30 只加回 smartctl 仍 loading；r31 再加回 mdadm，圈停了但红框里没有用量条。r28 已证明不是「U 盘认不成系统盘」。

首页磁盘卡片（不是 RAID 向导那个 `Promise.all`）初始 `disks=null, raidList=null`，官方用 `!disks && !raidList` 显示转圈。`mdadm` 让 `/raid/list/` 很快返回空阵列 `[]`，空数组在 JS 里是 truthy，转圈立刻结束；`Disk.Status`（`smartctl`）还没到时 `disks` 仍是 `null`，系统根目录和已挂载都不画 → 空白。r28 工具齐全时 Disk.Status 赶在看见之前回来了，所以看起来正常。

侧栏 RAID/SMART 继续从 controller 删除。当时 `smartd` 仍不要，只改 loading 条件。r32 已刷，卡片改回「正在获取...」，见 §三十五。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：首页磁盘信息列出系统根目录用量（与 r28 相同），不再空白或假结束 loading | `pin-quickstart.sh` 改 `index.js` loading 条件 | 等 `/nas/disk/status/`；空 RAID 列表不再提前收掉转圈 |
| **仍不能**：侧栏「网络存储 / 磁盘阵列 / S.M.A.R.T.」 | controller 仍删那两条 `entry` | 无数据盘不要这些页 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 构建脚本 | `pin-quickstart.sh`：`index.js` 把 `!e(l).disks&&!e(l).raidList` 改成 `e(l).disks==null`；RAID/SMART 菜单删除、Makefile 依赖不变 |
| seed | 当时不动；`smartd` 已由 §三十五 加回 |
| 不加 | 侧栏 RAID/SMART 菜单 |

后续 AI：**不要**为了磁盘信息把 RAID/SMART 菜单加回；**不要**再把 r31 空白写成「U 盘不是系统盘」。r33 已验证见 §三十五。

## 三十五、首页磁盘信息仍转圈：加回 smartd 包（2026-10-18，用户明确要求菜单不要、磁盘信息要）

r32 已含 smartctl、mdadm、§三十四 的 loading 补丁，N100 首页仍显示「正在获取磁盘信息...」。说明 `GET /nas/disk/status/` 一直没返回，不是前端假结束。

对照 r28（能出系统根目录用量）和 r32 的 manifest：磁盘相关只差 **`smartd` 这个包**。QuickStart 预编译守护进程会跑 `smartctl`，字符串里还有 `/etc/smartd.conf` 和 `/etc/init.d/smartd`。更具体的线索是缺 `/etc/smartd.conf`（随 `smartd` 包进来）；**仍不能认定必须运行 smartd 后台服务**。本批把包加回 seed、Makefile 不再拆 `+smartd`，侧栏 RAID/SMART 仍删。

**2026-10-18 夜 N100 验证 r33**：首页磁盘信息有系统根目录用量，侧栏没有 RAID/SMART。用户确认「可以了」。

旧构建树可能已跳过 clone、Makefile 还停在拆掉 `+smartd` 的裁剪版：`pin-quickstart.sh` 先把 `+smartd` 加回去，再检查官方四项都在。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**（r33 N100 已验证）：首页磁盘信息列出系统根目录用量 | `smartd` 包（含 `/etc/smartd.conf`）+ `smartctl`/`mdadm` | 给 QuickStart Disk.Status；不是侧栏 S.M.A.R.T. 页。不认定必须跑 smartd 守护进程 |
| **仍不能**：侧栏「网络存储 / 磁盘阵列 / S.M.A.R.T.」 | controller 仍删那两条 `entry` | 无数据盘不要这些页 |
| **可能有**：若包默认启用 init，后台会出现 smartd 进程 | `smartd` 包自带 init | 这是包的默认行为，不是本批要的功能；r33 只验证了首页卡片，没拆证是 conf 还是守护进程 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 往 config-custom.seed 加回（1 行；seed `=y` 515 → **516**） | `smartd` |
| 构建脚本 | `pin-quickstart.sh`：若 Makefile 是旧裁剪（无 `+smartd`）先加回，再要求官方 `+smartmontools +smartd +smartmontools-drivedb +mdadm`；RAID/SMART 菜单仍删；loading 仍等 Disk.Status |
| 审计 | `luci-app-filetransfer=y` 仍红；`smartmontools`/`drivedb`/`smartd`/`mdadm` **必须**是 `=y` |
| 不加 | 侧栏 RAID/SMART 菜单 |

后续 AI：**不要**再把 `smartd` 包当「无盘所以多余」从 seed/Makefile 拆掉；**不要**为了这个包把侧栏 SMART 页加回来；**不要**把本批写成「已经证实必须跑 smartd 后台」（N100 只验证了加回这个包之后卡片正常）。
