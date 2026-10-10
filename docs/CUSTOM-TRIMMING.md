# iStoreOS 定制裁剪记录（面向后续 AI 助手 / 维护者）

> **必读**。本仓库是 `xcy960815` 对 iStoreOS 官方源（`istoreos/istoreos`）的 fork，
> 用于为家里的 J4125 四口 2.5G 软路由（LAN IP `192.168.100.1`）构建裁剪版固件。
> 用户在 2026-10-05 明确要求删除下列功能，**除非用户再次明确要求，不得在 seed 中加回**。

## 当前进度（2026-10-10 晚，后续 AI 先读这里）

**裁剪版已经编出来了，哪台机器都还没刷上。** 用户上次装官方 iStoreOS 用的就是 **img**（`dd` / Etcher 整盘写入），N100 试刷也走这套，不必等 ISO。

**后续 seed 变更（2026-10-10，§二十）**：用户已要求移除 Aria2/Transmission 及其页面入口，当前 seed 已关闭 9 个包（596 → 587 个 `=y`）。**r10 和基于旧提交启动的 ISO 构建仍含下载器**，本轮修改需新的构建验证后才进入镜像。

| 事实 | 细节 |
|---|---|
| 可用固件 | GitHub Actions **r10** 成功（run [`38017418688`](https://github.com/xcy960815/istoreos/actions/runs/38017418688)），产物 `istoreos-x86_64-trimmed-r10`，约 291MB。刷 **EFI** 这一张：`istoreos-x86-64-generic-squashfs-combined-efi.img.gz`（约 100MB）。Mac 上曾下到 `/tmp/istoreos-r10/images/`（`/tmp` 重启可能没） |
| 里面有什么 | DDNS-Go **6.12.2** 开箱；无 Docker/Samba/UPnP/ddnsto；OpenClash 等仍要刷完进商店装。分区 kernel 32MB / root 512MB，没打 ext4 根镜像 |
| **禁止** | **不要刷正在用的 J4125**。N100 的 LAN **不要**插家里交换机（和网关抢 `192.168.100.1`）。**不要**用双公头 USB 线连 Mac↔N100（两边都是主机口，刷不了机，可能烧口） |
| N100 试刷 | 双网口、无显示器、机内 **16G 英特尔傲腾**。把 img **写到一根普通 U 盘**（不要写到 Ventoy 那根），U 盘插 N100 开机。Mac 关 Wi‑Fi，网线接 N100 **第二口**，Mac 设 `192.168.100.2/24`，打开 http://192.168.100.1。无内存点不亮；要关 Secure Boot。傲腾若是 RST 缓存条，`lsblk` 没 nvme 就当不了系统盘 |
| ISO 那轮 | seed 已开 `CONFIG_ISO_IMAGES`（§十九）。run [`38052856173`](https://github.com/xcy960815/istoreos/actions/runs/38052856173) 在编。ISO 是 **LiveCD**，不是安装向导；用户已说明上次装的是 img，**试刷优先用 r10 的 img** |
| 本机编 | Mac 是 M1 Max，编不了这份 x86 树。9400F 还没装 Ubuntu，冷编也不比 Actions 快多少 |
| 还没做 | D 档再瘦 seed（§十六）；J4125 刷入；N100 实际开机仍未验证 |

后续 AI：**不要**把 r10 当失败；**不要**为清 Actions 黄条重编（§十八 已改 workflow，下次 run 才干净）；**不要**把双公头线当刷机方案。

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

> ⚠️ 本清单是**功能**层面"别丢"，不等于"固件里已烘焙"：其中 openclash、quickstart、`app-meta-*`、`luci-app-{cpufreq,fan,eqos,oaf,diskman,gowebdav,…}` 等不在构建期。除 QuickStart 外，按需从 iStore 商店装回；QuickStart 本轮不装回，以免恢复已删除的下载器、Samba、易有云首页卡片。哪些真在固件里、哪些要装回——唯一清单见 §六「仍然完好、一个没动的功能」和 §十，证据见 §九。

- **openclash**：全家主力代理，GeoIP 数据齐全、多份配置备份（用户本机代理 7897 与之同源）
- **ddns-go + luci-app-ddns-go**：公网 IP + 免费域名，**开箱即有**（第七条 feed `ddnsgo`）。勿删、勿改回「刷机后商店装」、勿用 `luci-app-ddns` 顶替
- **tailscale + luci-app-tailscale-community**：家人设备远程入口，路由器是 exit node（与公网 DDNS 并行，不是二选一）
- **openlist / vlmcsd / eqos / oaf / ttyd / wol(etherwake) / cpufreq / luci-fan / fastnet / floatip**：保留；2026-10-10 用户再次明确 OpenList 和它自带的 WebDAV 要留，不能随下载器删除
- **Aria2 / Transmission 已退出保留清单**：2026-10-10 用户明确不需要，连同管理页面和首页入口一起去掉，见 §二十。旧配置行数不再作为保留依据
- **istore / luci-app-store / argon 主题**：系统管理骨架，勿动；QuickStart 首页本轮不装回
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

- **固件里确实有**：tailscale（守护进程，路由器仍作 exit node）、**ddns-go + luci-app-ddns-go（2026-10-09 加回，见 §十五）**、openlist（含 WebDAV）、
  vlmcsd、ttyd、wol、iStore 商店本体（`luci-app-store`+`dkml`）、argon 主题、zram、smartd+lm-sensors（温控）、
  wireguard、dnsmasq-full、flow offload（kmod-nf-flow）
- **不在固件里、刷机后要从商店装回**：openclash、eqos、oaf、cpufreq、luci-app-fan、fastnet、floatip、
  quickstart、gowebdav、tailscale 的 LuCI 配置页——它们从来不是构建期候选，包名与证据见 §十

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
3. **软依赖**（脚本 shell 调用而非包依赖）不会被自动拉回——QEMU 启动验证 + 刷机后核对 LuCI 各页（重点：iStore 商店；磁盘管理、openclash、tailscale UI 这些**先按 §九 从商店装回**再核对；QuickStart 不装回）照 BUILD-CUSTOM.md 流程走
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

**已定（2026-10-06，用户选）**：**不**把整个 iStore 商店 / app-hub 追加进 `feeds.conf`，维持"固件只留路由栈 + 商店本体，刷机后按需从 iStore 商店装回 openclash / tailscale UI / eqos …"。QuickStart 因会带回已删除的首页卡片，本轮不装回。理由是镜像尺寸优先；随之把 104 行死 seed 清掉，见 §十。

**修订（2026-10-09）**：公网域名是硬需求，六个默认 feed 里又没有 DDNS-Go。允许也只允许 **一条** 例外 feed：`src-git ddnsgo https://github.com/sirpdboy/luci-app-ddns-go.git;v6.12.2`。这不是「商店 feed 开闸」——openclash 等仍不进构建期。见 §十五。

## 十、清掉 104 行"从未生效"的 seed 行（2026-10-06，697 → 593）

### 功能视角

**设备能做的事零变化**——这 104 行自写进 seed 起就是空转（符号不存在，defconfig 无警告删除），删掉它们不移除任何一块已烘焙的功能；固件产物与清理前逐包相同。

要交代的不是"删了什么"，而是**刷机后必须自己装回的东西**（原先误以为已在固件里）：OpenClash、Tailscale 的 LuCI 配置页（守护进程 `tailscale` 确实在，可先用 UCI/`/etc/config/tailscale` 配）、eqos IP 限速、oaf/appfilter 应用过滤、cpufreq 与风扇调节、diskman 磁盘管理、gowebdav/fastnet/floatip/webdav2。QuickStart 本轮不装回，因为其首页会带下载器、Samba、易有云卡片。装回途径：LuCI → iStore 商店（本体 `luci-app-store` + `dkml` 已在固件）。**2026-10-10 更正：Aria2/Transmission 及其入口与商店元数据不再装回**（§二十）；下方批次清单只记录历史清理，不是恢复清单。

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

#### 功能视角（候选，未执行）

| 若从 seed 删掉，设备不能再做什么 | 候选（仍在 seed） | 前提 / 必须留的 |
|---|---|---|
| 跑 ruby 脚本 | `ruby`、`ruby-bigdecimal/date/digest/enc/pstore/psych/stringio/yaml` | `opkg whatdepends ruby` 为空才砍 |
| 在路由器上 git clone | `git`、`git-http` | 纯网关不需要；whatdepends 为空才砍 |
| taskd 任务框架 | `taskd`、`luci-lib-taskd` | 同上 |
| sqlite 命令行 | `sqlite3-cli` | **库可能被别的包依赖，只砍 CLI** |
| `sensors-detect` 探测芯片 | `lm-sensors-detect`、`perl`、全部 `perlbase-*` | **`lm-sensors` 本体留**（风扇温控） |
| 挂冷门磁盘格式 | `kmod-fs-{hfs,hfsplus,jfs,reiserfs,minix,cramfs,isofs,udf,msdos}` 及对应用户态 | **必留**：squashfs、ext4、vfat/exfat（U 盘）、efivarfs。btrfs/xfs/ntfs3/f2fs 等 `df -T /mnt/sata1-4` 再说 |
| 老式交换机 / DS-Lite 等过渡隧道 | `map`、`ds-lite`、`kmod-sit`、`kmod-nat46`、`kmod-sctp`、`kmod-tpm` | IPv6 本体（odhcp6c/odhcpd）留 |
| 换一块非 Intel i226 的 PCI 网卡 | `kmod-e1000`、`kmod-e1000e`、`kmod-igb`、`kmod-igbvf`、`r8169-firmware`（及 r8169/r8125 若仍在） | **`kmod-igc` 绝对留**。USB 网卡 + 手机 RNDIS/iPhone 共享仍留。只在「这块板永远不换 PCI 网卡」时才收保险 |

#### 包名明细（仍在 seed，尚未删除）

执行时按上表分组从 `config-custom.seed` 去掉对应 `=y`（或钉 `is not set`），同一提交更新本节：把「候选」改成「已删」，并写清刷完机少了什么。

后续 AI：**不要**把本节当成授权去删 `target/linux` 或其他架构源码。r9 已证明打盘会挂，允许的 seed 改动只有 §十七 的镜像布局；D 档包仍等出镜像后再动。

## 十七、镜像布局：只出 squashfs，分区 32/512（r9，2026-10-09）

| seed 设置 | 原因 |
|---|---|
| `# CONFIG_TARGET_ROOTFS_EXT4FS is not set` | x86 默认还打一份 ext4 根镜像，`make_ext4fs` 按未压缩体积算，224MB 装不下，r9 挂在 `target/linux install`。刷机只用 `*-squashfs-combined-efi.img.gz`，ext4 根镜像用不上 |
| `CONFIG_TARGET_KERNEL_PARTSIZE=32`、`CONFIG_TARGET_ROOTFS_PARTSIZE=512` | 默认 16MB kernel 分区偏紧，root 224MB 不够 |

刷完机少的只是「另一份 ext4 根盘镜像」，LuCI、overlay、扩容不受影响。CI 遇到 `ERROR: target/linux` 会跑 `make target/linux/install -j1 V=s` 并上传 `logs/target`。i915 仍被 profile 的 `DEVICE_PACKAGES` 加回，属 §六 A 档漏网，出镜像后再收（未做）。

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
