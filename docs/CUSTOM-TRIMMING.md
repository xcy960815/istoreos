# iStoreOS 定制裁剪记录（面向后续 AI 助手 / 维护者）

> **必读**。本仓库是 `xcy960815` 对 iStoreOS 官方源（`istoreos/istoreos`）的 fork，
> 用于为家里的 J4125 四口 2.5G 软路由（LAN IP `192.168.100.1`）构建裁剪版固件。
> 用户在 2026-10-05 明确要求删除下列功能，**除非用户再次明确要求，不得在 seed 中加回**。

## 当前进度（2026-10-16 晚，后续 AI 先读这里）

**两套状态不要混：** 已经能刷的是 **r17**；带官方首页、去掉 Bootstrap 的改动已提交并推送（`5612b37936`），但**还没有构建出镜像**：r18 触发后因给 workflow 加「构建成功发 Release」（§二十五）被取消，改由 **r19 重跑**（SHA `9d5f97ef56`，只含首页/主题改动）。其后两批 seed 瘦身已推送（§二十六 删 7 行、§二十七 删 26 行钉 8 行），**r20 一并编入、排队在 r19 后自动开跑**。N100 已经用 r17 的 U 盘开过机。用户上次装官方也是 **img** 整盘写入，不必等 ISO。

**后续 seed 变更（2026-10-10，§二十）**：用户已要求移除 Aria2/Transmission 及其页面入口，当前 seed 已关闭 9 个包（596 → 587 个 `=y`）。r12 起的镜像已不含下载器（r10、r11 仍含）。

**后续 seed 变更（2026-10-12，§二十一）**：用户要求删除「在线升级」页面，seed 再关 2 个包（587 → 585 个 `=y`）。r13 起的镜像已不含 OTA。

**后续 seed 变更（2026-10-14，§二十二）**：用户要求内置最新 Tailscale。守护进程本来就在（r13 是 1.80.3）；本轮换成官方 **1.104.1** amd64 预编译，并烘焙 LuCI（asvow `luci-app-tailscale` v1.2.6）。不能从源码编最新版（要 Go 1.27，本树 golang 1.23.12）。seed 585 → 587。

**后续 seed 变更（2026-10-16，§二十三，`5612b37936` 已推送）**：用户要官方那种 QuickStart 首页，但不要 Samba/易有云/下载器/OTA。第三条构建例外 `.github/scripts/pin-quickstart.sh`：只 clone 两个包，从首页渲染里**删掉**存储/下载/远程域名/Docker 整块（不是开关隐藏）。侧栏「网络向导」保留。seed 587 → 590。**r17 没有这些**，还是 Argon 概览。

**后续 seed 变更（2026-10-16，§二十四，`5612b37936` 已推送）**：用户要求去掉第二主题 Bootstrap。seed 再关 1 个包（590 → 589）。`luci-light` 硬依赖它，所以还有 `.github/scripts/drop-luci-theme-bootstrap.sh`。界面只留 Argon。**r17 仍带 Bootstrap。**

**产物去处（2026-10-16 起，§二十五）**：构建成功后，镜像除 Actions artifact（14 天过期、下载要登录）外，自动发 GitHub Releases（tag `r<run_number>`，长期公开下载）。r17 及更早只在 artifact 里。

**后续 seed 变更（2026-10-16，§二十六）**：用户要求先清「杂项零头」。seed 删除 7 行（589 → 582）：`kmod-igbvf`、`kmod-ipt-physdev`（连带 br-netfilter）、`kmod-keys-encrypted`、`kmod-keys-trusted`、`kmod-ppdev`、`kmod-sctp`、`kmod-tpm`。**尚未构建**，编入 r19 之后的下一轮（r20）。

**后续 seed 变更（2026-10-16，§二十七）**：用户要求「继续删，最后一起编」。第二批清收一次做完：删 26 行、钉 8 行（seed 582 → **556**）——显示栈（钉 `kmod-drm-i915`）/USB 摄像头/USB 音频/隧道群（sit·ip6-tunnel·iptunnel6·nat46·siit·ds-lite·map）/老式交换机（swconfig＋6 驱动＋spi-ks8995）/nbd/htop·strace/华为 LTE 驱动/非保险网卡（钉 tg3·ixgbe·bnx2·amd-xgbe·amazon-ena·forcedeth·dwmac-intel）。**尚未构建**，与 §二十六 一起编入 **r20**。

| 事实 | 细节 |
|---|---|
| 可用固件 | GitHub Actions **r17** 成功（run [`38561237293`](https://github.com/xcy960815/istoreos/actions/runs/38561237293)，提交 `597a40aba3`），产物 `istoreos-x86_64-trimmed-r17`。刷 **EFI img**：gz 解压后的 `*-squashfs-combined-efi.img` 整盘 dd。r10 已过时，别再刷 |
| r17 里面有什么 | DDNS-Go **6.12.2**、Tailscale **1.104.1** + LuCI（VPN → Tailscale）；WireGuard、网络唤醒、OpenList、Argon + Bootstrap。**没有** Docker/Samba/UPnP/ddnsto/下载器/OTA。登录是 Argon 状态概览，**没有** QuickStart 首页，侧栏**没有**「网络向导」。默认 `root` / 空密码 |
| 已写到哪 | 64G SanDisk 当 N100 系统盘（整盘 dd）。Finder「无法读取磁盘」正常，**不要初始化**。macOS 要用终端.app 完全磁盘访问后 `sudo dd`，Cursor `osascript` 会被 TCC 拦 |
| **禁止** | **不要刷正在用的 J4125**（和 N100 都是 `192.168.100.1`）。N100 的 LAN **不要**插家里交换机。**不要**用双公头 USB 线连 Mac↔N100 |
| N100 | **已经用这根 U 盘开过机**，能进 LuCI。双网口、无显示器、机内 16G 傲腾（RST 缓存条当不了系统盘就别写）。BIOS：U 盘优先、Secure Boot 关。Mac 无内置网口：网线接 N100 **第二口**，`192.168.100.2/24`、**网关留空**。家里关 Wi‑Fi；公司 USB 网卡（用过 AX88179A）必须排在 Wi‑Fi 下面，否则 `192.168.100.1` 会被公司网抢走 |
| 官方截图 | 家里 **J4125** 上的官方整包 QuickStart（Samba/易有云/固件更新卡片），不是 r17，也不是选错分支。`custom-24.10` 跟踪的就是 `istoreos-24.10` |
| 已推送未构建 | seed **556**。三块改动都在 `origin/custom-24.10`：① `5612b37936`——`pin-quickstart.sh` 烘焙首页（删 Docker/下载/存储/ddnsto 卡片，保留侧栏网络向导，§二十三）＋`drop-luci-theme-bootstrap.sh` 去第二主题（§二十四）；② 杂项零头 7 行（§二十六）；③ 第二批清收 26 删 8 钉（§二十七）。r19 基于 `9d5f97ef56` **构建中**（只含①）；②③编入 **r20**（排队在 r19 后自动开跑）。出镜像后自动进 Releases（§二十五） |
| 本机编 | Mac 是 M1 Max，编不了这份 x86 树。9400F 还没装 Ubuntu |
| 还没做 | r19 出镜像后写 U 盘验首页（随后 r20 验两批清收：审计里显示栈/摄像头/隧道/交换机/br-netfilter 等应消失、「seed 没写却开启」不应新增）；D 档剩余项（ruby/git/taskd/sqlite3-cli/lm-sensors-detect、冷门 fs，§十六）等 N100 证据；**J4125 仍禁止刷** |

后续 AI：**不要**把已推送未构建的 QuickStart 写成「r17 已有首页」；**不要**只删 seed 里的 bootstrap 就以为主题没了；**不要**再拿 r10 试刷；**不要**把双公头线当刷机方案。

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
- **istore / luci-app-store / argon 主题 / QuickStart 首页**：系统管理骨架，勿动。首页方案见 §二十三（r17 还没有；改动已推送、r19 构建中）；Samba/易有云/下载器/ddnsto 卡片要从页面去掉，不要加回 Bootstrap（§二十四）
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
| L2TP/PPTP/SSTP VPN 拨号、GRE/IPIP 隧道、IPsec、链路聚合、中继 | 各协议 kmod+用户态、bonding、relayd | 不用这些拨号协议；远程走 Tailscale 或公网端口转发。**WireGuard 完整保留** |
| 跑 KVM 虚拟机 | kvm/vfio/vhost（容器首轮已删） | 虚拟化归 9400F/N100 |
| 识别老式/服务器级网卡（万兆、FC、古董 PCI） | 对应驱动+固件 | 常用保险已留：**igc + e1000/e1000e/igb/r8169/r8125** + 主流 USB 网卡（asix/ax88179/aqc111/rtl8152） |
| ISDN/ATM 电话线拨号 | misdn/hfc/atm/solos | 古董功能，无影响 |
| UPnP NAT 映射（首轮已删）的残留客户端库 | libnatpmp1 | 无影响 |

### 仍然完好、一个没动的功能

本节写于 r4 审计之前，当时把"路由器在用的功能"和"固件里已烘焙的包"混为一谈，按 §九/§十 的口径重列。以下清单已按 §二十 更新为当前 seed 的预期，r10 等旧镜像仍含 Aria2/Transmission：

- **固件里确实有（r17）**：**tailscale 1.104.1 + luci-app-tailscale（见 §二十二）**、**ddns-go + luci-app-ddns-go（见 §十五）**、openlist（含 WebDAV）、
  vlmcsd、ttyd、wol、iStore 商店本体（`luci-app-store`+`dkml`）、argon 主题、zram、smartd+lm-sensors（温控）、
  wireguard、dnsmasq-full、flow offload（kmod-nf-flow）
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

用户同时问过 WireGuard、网络唤醒、备份与升级：这三项与上游同步无关，**全部保留**。WireGuard 是公网 DDNS-Go 之外的另一条远程入口（Tailscale 自带 userspace WireGuard，不依赖它）；网络唤醒用来叫醒 9400F/N100；备份与升级是 `luci-mod-system` 自带页面，刷机前导出 `/etc/config`、本地上传自编镜像都靠它。

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
| 首页卡片：网络向导 / 局域网设备 / 测速 / 商店 / 内网·DNS·日志·终端 | 保留 | 这就是用户要的首页 |
| 磁盘信息 | 保留 | 只读概览，不是 Samba |
| Docker | 前端已按 `/etc/init.d/dockerd` 是否存在决定；本镜像没有 dockerd，卡片不出现 | 不装 Docker |
| 固件更新 / 沙箱 | 前端已按 `ota` 二进制、`/ext_overlay` 决定；本镜像都没有 | OTA 已删（§二十一） |
| 存储服务（易有云 / Samba / WebDAV） | 从首页渲染和模块表删除，格子让给磁盘信息 | 文件服务归 9400F/N100；OpenList 自带的 WebDAV 走它自己的页面，不是这块 NAS 向导 |
| 下载服务（Aria2 / Transmission） | 同上删除 | §二十 |
| 远程域名（ddnsto） | 同上删除 | 公网走 DDNS-Go，禁止 ddnsto |
| 点「快速配置」从商店装回上述包 | `auto_setup.sh` 直接拒绝 | 即使用户以后从别处进向导，也不能把已删服务装回来 |

`quickstart` 的 Makefile 声明依赖 `mdadm` 等磁盘工具。二次裁剪曾从 seed 拿掉 mdadm（§六 B，单盘无 RAID）；这次 defconfig 会把它作为依赖加回二进制，**不是**把 Samba 加回来。不要为了「首页」去改 `package/istoreos-files` 源码。

### 功能视角

| 变更后设备能做 / 不能做 | 涉及 | 影响 / 替代方案 |
|---|---|---|
| **能**：登录就是官方那种 QuickStart 首页；侧栏有「首页」和「网络向导」 | `quickstart` + `luci-app-quickstart` + 中文包 | 不再默认停在 Argon 状态概览；网络向导走 `admin/network_guide` |
| **仍不能**：在首页看到或配置 Samba / 易有云 / NAS WebDAV / Aria2 / Transmission / ddnsto | 首页渲染删除这些模块 + auto_setup 拒绝名单 | 文件服务用 9400F/N100；公网域名用 DDNS-Go；OpenList WebDAV 用 OpenList 自己的页面 |
| **仍不能**：开箱即有 OpenClash 等其它商店应用 | 未改 app-hub、未改 §十 | 刷机后商店装回，与本次无关 |

### 包名明细

| 动作 | 内容 |
|---|---|
| 构建脚本（feeds install 之后、defconfig 之前） | `.github/scripts/pin-quickstart.sh`：sparse clone `linkease/nas-packages@c82c458b61e5` 的 `network/services/quickstart`（预编译 0.13.0）到 `package/quickstart`；sparse clone `linkease/nas-packages-luci@7e5083e2ca4c` 的 `luci/luci-app-quickstart`（0.12.10-r1）到 `package/luci-app-quickstart`。再改构建树副本：从首页渲染删除 storage/downloadService/remoteDomain（含 Docker 块），模块表和设置列表也不留这几项，剩下的卡片按数量重新占宽；`auto_setup.sh` 拒绝 samba/linkease/aria2/transmission/docker/ddnsto 等，`disable_update_check=1` |
| seed 新增 `=y` | `quickstart`、`luci-app-quickstart`、`luci-i18n-quickstart-zh-cn`（seed `CONFIG_PACKAGE_*` 587 → 590） |
| defconfig 可能自行加回 | `mdadm` 等 `quickstart` 的 DEPENDS（seed 里没有这些行也不算死行） |
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
