# iStoreOS 定制裁剪记录（面向后续 AI 助手 / 维护者）

> **必读**。本仓库是 `xcy960815` 对 iStoreOS 官方源（`istoreos/istoreos`）的 fork，
> 用于为家里的 J4125 四口 2.5G 软路由（LAN IP `192.168.100.1`）构建裁剪版固件。
> 用户在 2026-10-05 明确要求删除下列功能，**除非用户再次明确要求，不得在 seed 中加回**。

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
| DDNS（三套） | ddns-scripts 全系列（含 cloudflare/dnspod/services/aliyun）、luci-app-ddns、ddns-go、app-meta-ddnsgo、luci-app-ddns-go、ddnsto、luci-app-ddnsto 及 i18n | 远程访问统一走 Tailscale，不需要公网 DDNS，减少暴露面 |
| UPnP | miniupnpd-nftables、luci-app-upnp、libminiupnpc 及 i18n | 无使用需求，减少暴露面 |
| Linkease 系 | linkease、luci-app-linkease、ddnsto 同属 Linkease 生态 | 未使用 |

## 三、保留清单（有实际使用证据，后续 AI 不要当成"没用"误删）

> ⚠️ 本清单是**功能**层面"别丢"，不等于"固件里已烘焙"。r4 审计实测：其中 openclash、luci-app-tailscale-community、quickstart、app-meta-*、luci-app-{cpufreq,fan,eqos,oaf,diskman,gowebdav,fastnet,floatip,openclawmgr} 等在 `feeds.conf.default` 的六个 feed 里**没有对应 kconfig 符号**，seed 中的行一直是死行；刷机后要经 iStore 商店装回（商店本体 `luci-app-store`+`dkml`+`tailscale` 守护进程确实在固件里）。明细与证据见 §九。

- **openclash**：全家主力代理，GeoIP 数据齐全、多份配置备份（用户本机代理 7897 与之同源）
- **tailscale + luci-app-tailscale-community**：全家远程入口，路由器是 exit node
- **aria2 / transmission**：85 行 / 74 行实际配置，在用的下载工具
- **openlist / gowebdav / vlmcsd / eqos / oaf / ttyd / wol(etherwake) / cpufreq / luci-fan / fastnet / floatip**：均有活跃配置
- **istore / quickstart / luci-app-store / argon 主题**：系统管理骨架，勿动
- **kmod-igc**：四个 2.5G i226-V 网卡的驱动，删了机器变砖
- **irqbalance**：定制新增，为四张 2.5G 网卡分摊中断

## 四、硬件与拓扑上下文

| 设备 | 角色 |
|---|---|
| J4125 四口 2.5G（本固件目标机） | 纯网关 + Tailscale 入口 + VLAN 分段 |
| 9400F + 1060（192.168.100.10） | 主服务器：原数据中台全部 Docker 服务 |
| 零刻 N100 | 哨兵节点（备份/监控/备用入口），待 DDR5 内存降价上岗 |
| 12600KF | 用户新主力机（与本项目无关） |

四口规划：口1 WAN｜口2 LAN 主交换机｜口3 服务器 2.5G 专线｜口4 备胎。

## 五、改回/新增某功能的正确姿势

1. 临时：刷好系统后在 iStore 商店装回
2. 长期：往 `config-custom.seed` 加一行 `CONFIG_PACKAGE_xxx=y`，提交到 custom-24.10，Actions 重编

## 六、二次裁剪（2026-10-05，按"纯网关"定位再减法）

首轮 seed = 官方镜像清单做减法，官方清单里大量包是为**通用硬件**准备的。按目标机最终定位
（无无线的纯网关 + Tailscale 入口 + VLAN，文件服务归 9400F/N100）做第二轮减法。
仍在 seed 内完成，未动源码；§三保留清单**原封未动**。seed 包配置行数 1078 → 697。

### 功能视角：二次裁剪后这台路由器"不能再做什么"

| 不能再做的功能 | 涉及（已删） | 影响 / 替代方案 |
|---|---|---|
| 无线 AP / 无线中继 / USB 无线网卡 | mac80211、hostapd、wpa-supplicant、全系无线驱动+固件 | 机器本来就没无线网卡；日后插 USB 无线网卡需往 seed 加回 mac80211+wpa-supplicant |
| 3G/4G/5G 上网模组、随身 WiFi 拨号 | modemmanager、libmbim/libqmi、comgt、usb-modeswitch、mhi/qrtr | 无此硬件；**断网应急改用手机 USB 共享网络**（rndis/ipheth/cdc-ncm 已保留，插 iPhone/Android 可当 WAN） |
| USB 转串口设备（调试线/串口模块） | kmod-usb-serial 全系 | 需要时 iStore 临时装回或往 seed 加一行 |
| 接显示器看图形界面、GPU 工具 | i915/amdgpu/radeon 固件、DRM/fb 全系、nvtop | 无头设备无影响；GRUB 菜单和 VGA 文本控制台仍可用，QEMU 验证不受影响 |
| 当 NFS/Samba/WebDAV 服务器；挂载别人的网络盘 | NFS 服务端全家、cifsmount、davfs2（Samba 首轮已删） | 文件服务归 9400F/N100；**gowebdav 服务端仍在用** |
| RAID / 多盘合并 / 硬盘休眠 / iSCSI / USB over IP | mdadm+kmod-md、kmod-dm、mergerfs、hd-idle、iscsi/aoe、usbip | 单盘直用完全不受影响 |
| L2TP/PPTP/SSTP VPN 拨号、GRE/IPIP 隧道、IPsec、链路聚合、中继 | 各协议 kmod+用户态、bonding、relayd | 远程统一走 Tailscale；**WireGuard 完整保留** |
| 跑 KVM 虚拟机 | kvm/vfio/vhost（容器首轮已删） | 虚拟化归 9400F/N100 |
| 识别老式/服务器级网卡（万兆、FC、古董 PCI） | 对应驱动+固件 | 常用保险已留：**igc + e1000/e1000e/igb/r8169/r8125** + 主流 USB 网卡（asix/ax88179/aqc111/rtl8152） |
| ISDN/ATM 电话线拨号 | misdn/hfc/atm/solos | 古董功能，无影响 |
| UPnP NAT 映射（首轮已删）的残留客户端库 | libnatpmp1 | 无影响 |

### 仍然完好、一个没动的功能

openclash、tailscale（路由器仍作 exit node）、aria2+ariang、transmission、openlist、gowebdav、
vlmcsd、eqos、oaf、ttyd、wol、cpufreq、luci-app-fan、fastnet、floatip、iStore 商店+quickstart、
argon 主题、zram、smartd+lm-sensors（温控）、wireguard、dnsmasq-full、flow offload（kmod-nf-flow）。

### 包名明细（按批次）

| 批次 | 删除内容 | 依据 |
|---|---|---|
| A 无线全家 | mac80211/cfg80211、ath/mt76/rtl/rtw/iwlwifi 全系 kmod+固件（含 iwlwifi-firmware×8、rtl-固件×15）、hostapd、wpa-supplicant/wpa-cli、wifi-scripts、wireless-regdb、iw/iwinfo/libiwinfo | J4125 盒子无无线网卡，四口全有线 |
| A 蜂窝 modem 全家 | modemmanager、libmbim/libqmi/libqrtr-glib/uqmi/umbim/qmi-utils、comgt×3、usb-modeswitch、adb/adb-enablemodem、chat、kmod-mhi/qrtr/wwan/mtk-t7xx、全部 kmod-usb-serial、usb-acm/usb-atm、kmod-atm/solos-pci、usb-net 中的 mbim/qmi/hso/sierra/kalmia/kaweth | 无蜂窝硬件；**USB 网卡与手机共享网络保留**（rndis/ipheth/cdc-ncm/asix/ax88179/aqc111/rtl8152 等） |
| A GPU/显示 | amdgpu/radeon/i915 固件、kmod-drm 全系、kmod-fb 全系、kmod-acpi-video/backlight、nvtop、libdrm | 无头路由；GRUB/QEMU 文本控制台不受影响（kmod-ata-piix 专门留作 QEMU 默认 IDE 启动） |
| B 文件/存储服务 | nfs-kernel-server 全家+rpcbind+kmod-fs-nfs×5、cifsmount/luci-app-cifs-mount/kmod-fs-cifs+kmod-fs-smbfs-common/wsdd2、davfs2+libneon、mergerfs+luci-app-mergerfs、hd-idle+luci-app-hd-idle、mdadm+kmod-md×7+kmod-dm(-raid)+kmod-dax、iscsi/aoe/mpt3sas/mvsas/libsas/scsi-tape/scsi-raid/libfc/libfcoe、usbip×3 | 文件服务已归 9400F/N100，单盘无 RAID（对应 §四 拓扑） |
| C 隧道/协议/虚拟化 | l2tp×3/ppptp(mppe)/sstp/gre/ipip/ipsec/macsec/tls 的 kmod+用户态、gre/ipip 协议处理器、bonding+proto-bonding、relayd+luci-proto-relay、trelay、kmod-kvm×3/vfio×2/vhost×2/irqbypass、kmod-9p×3、kmod-misdn/hfc×2 | 远程只走 Tailscale，不做虚拟化宿主，无 ISDN/隧道拨号 |
| C Docker/UPnP 孤儿 | kmod-veth/macvlan/ipvlan/vxlan/br-netfilter/nf-ipvs、libnatpmp1 | 原为已删 Docker/UPnP 的依赖（首轮漏网） |
| C 老式网卡 | 3c59x/8139/tulip/via/sis/skge/sky2/tg3/bnx2*/mlx4/5/ixgbe/i40e/iavf/qed×4/sfc/ena/amd-xgbe/atl×5/alx/b44/e100/forcedeth/natsemi/ne2k/pcnet32/niu/pcs-xpcs/stmmac/dwmac/ethoc/et131x/dm9000/r6040/vmxnet3、kmod-r8168/r8126/r8127、ssb 及 bnx2/bnx2x/e100/qed/rtl/mwifiex 各固件 | **保险只留 igc（命根）+ e1000/e1000e/igb/r8169/r8125** |

### D 档（查清依赖后另批处理，本次未动）

- `ruby` 全家（libruby3.3+ruby-*×8）、`git/git-http`、`taskd/luci-lib-taskd`、`linkmount`、`sqlite3-cli`：官方镜像里某处在用，无法本地查依赖
- `lm-sensors-detect` + `perl` + perlbase-*×31：perl 疑似仅被 lm-sensors-detect（Perl 脚本）拉入；**lm-sensors 本体必须留**（luci-app-fan 温控）
- 文件系统类待确认数据盘实际格式：btrfs/ntfs3/f2fs/xfs/reiserfs/jfs/hfs/hfsplus/isofs/udf/cramfs/minix/msdos + exfat/vfat（U 盘建议留）
- 其他低价值但便宜：swconfig/switch-*、map/ds-lite/sit/siit/nat46、kmod-sctp/tpm/udptunnel/ppdev 等

**验证方法（路由器上执行）**：`opkg whatdepends ruby git taskd linkmount perl lm-sensors-detect`；`df -T /mnt/sata1-4`

### 安全网（为什么敢删）

1. `make defconfig` 会把"仍被保留包硬依赖"的项自动加回 `=y`——刷前 diff 展开的 `.config` 与 seed，多出的行即被拉回的依赖（已知候选：libiwinfo 被 rpcd-mod-iwinfo 拉回、mdadm 可能被 luci-app-diskman 拉回，均无害）。**但不止这些**：它还会加回 **profile 默认包**（`DEFAULT_PACKAGES`），这类可能与有意替换的实现冲突，见 §七
2. **`make defconfig` 必须在 `./scripts/feeds install -a` 之后跑**，否则所有 feed 包的 `CONFIG_PACKAGE_*=y` 行被静默丢弃（符号还不存在），后果见 §七 原因 1
3. **软依赖**（脚本 shell 调用而非包依赖）不会被自动拉回——QEMU 启动验证 + 刷机后核对 LuCI 各页（重点：iStore 商店；quickstart、磁盘管理、openclash、tailscale UI 这些**先按 §九 从商店装回**再核对）照 BUILD-CUSTOM.md 流程走
4. `dkml`（iStoreOS 动态内核模块加载器，package/diy/dkml）**保留**：iStore 商店装内核模块类应用的基础设施

## 七、CI 首次构建失败复盘（2026-10-05，run 37324148570）

失败点不在编译而在 **rootfs 装配**：`make[2]: *** [package/Makefile:99: package/install] Error 255`，
opkg 报 `Collected errors`。该 run 用的是**首轮 seed**（HEAD=eea07ec0f3，早于二次裁剪）；同日 15:28Z 另有一次
基于二次裁剪 seed（706d20bfe1）的 run，步骤顺序未修，会挂在同一处。两条互相独立的原因：

| # | 日志现象 | 根因 | 修法 |
|---|---|---|---|
| 1 | `cannot find dependency attr for base-files`、`curl for opkg`、`libgcrypt for ntfsprogs`、`luci-theme-argon for istoreos-files` | workflow 把 `make defconfig` 排在 `feeds update/install` **之前**。此刻 feed 符号尚不存在，kconfig `--defconfig` 把这些行**静默丢弃**（`CONFIG_LUCI_LANG_zh_Hans` 等信息类行同样被丢）。attr/curl/libgcrypt/luci-theme-argon 四个依赖全是 feed 包，核心树里没有；`base-files`(Makefile:45)、`opkg`(:41)、`package/diy/ntfsprogs`(:51)、`package/istoreos-files`(:20) 对它们的 `+xxx` 依赖在符号不可见时 select 落空 → 既没 `=y` 也没构建候选 | workflow 改为先装 feeds 再 `cp seed .config && make defconfig`；seed 头部"用法"行补上 feeds 步骤（原来漏写，正是它带偏了 CI） |
| 2 | `check_data_file_clashes: dnsmasq-full wants to install .../usr/sbin/dnsmasq`（等 10 个文件）`already provided by dnsmasq` | seed 只要 `dnsmasq-full`；`dnsmasq`(非 full) 是 **profile 默认包**——`include/target.mk:13` `DEVICE_TYPE?=router` → `DEFAULT_PACKAGES.router` 含 dnsmasq → 生成的 kconfig `default y if DEFAULT_dnsmasq` 把它加回 `=y`，两个变体装同一批文件 | seed 在 `dnsmasq-full` 前钉 `# CONFIG_PACKAGE_dnsmasq is not set` |

**kconfig 语义实测**（用本仓库 `scripts/config/conf` 复现生成规则，不是推断）：

- `# CONFIG_X is not set` 扛得住 `default y if DEFAULT_X`（defconfig 尊重显式关闭）→ 原因 2 的修法成立
- 扛不住其他包的 `select PACKAGE_X`（会被强制回 `=y`）→ 若某个保留包硬依赖非 full 变体，冲突会复发
- 符号不存在时 `CONFIG_...=y` 行被无警告删除 → 原因 1 只能靠步骤顺序防。CI 现已在 defconfig 后做审计：按 `tmp/.config-package.in` 把未生效的 seed 行分成「符号不存在」与「符号存在但没开成」两类，报告连同展开的 `.config` 一起作 artifact 上传；**审计本身不阻断构建**（要让它同时回答"能不能出镜像"），只有 `CONFIG_PACKAGE_dnsmasq=y` 复现时才硬失败

**功能视角**：本次**没有增删任何功能**，只修构建正确性。设备能做的事仍与 §六「仍然完好、一个没动的功能」清单一致；`dnsmasq` 非 full 变体从来不在路由器实装清单里，钉死它不改变行为（dnsmasq-full 以 `PROVIDES:=dnsmasq` 满足依赖）。

**查构建状态的坑**：本目录配了 `upstream=istoreos/istoreos`，`gh run list` 不带 `--repo` 会解析到**上游仓库并返回空数组**，看着像"从没跑过"。必须 `gh run list --repo xcy960815/istoreos --workflow "Build iStoreOS trimmed"`。

### 修复后复查（run 37345712561，17:04Z）

顺序修好 + dnsmasq 钉死后，构建停在新增的审计步骤（几分钟，不再烧 2 小时）。已验证生效的部分：`attr`/`curl`/`libgcrypt`/`luci-theme-argon` 不再出现在丢失列表，`CONFIG_PACKAGE_dnsmasq` 也没被加回。

审计同时打出 **105 行 `CONFIG_PACKAGE_*=y` 未生效**，workflow 现在按 `tmp/.config-package.in` 把它们自动分成两类并上传 `.config`+报告为 artifact：

- **符号本就不存在**：绝大多数是 `libcurl4` `libgcc1` `libubus20250102` 这类**带 ABI 后缀的 opkg 二进制包名**。kconfig 符号是无后缀的 `libcurl`/`libgcc`/`libubus`，后缀只出现在打包出的包名上。这些行自写进 seed 起就是死行（历次构建都丢），不影响功能——库会作为依赖自动进镜像，但"清单"是假的，待清
- **符号存在却没开成**（依赖不满足/被隐藏）：已在 r4 定档，见下方「r4 审计定档」

**顺序错误的真实代价比原判断严重**（对 14:22Z 那次日志的实测计数，非推断）：全文 `openclash|tailscale` 出现 **0** 次、`Installing luci*` **0** 条、`Configuring luci-base` **0** 次——也就是说那次构建的产物根本没有 LuCI 和任何商店应用，是台裸路由；先前只看到 4 条 `cannot find dependency` 是因为核心包（base-files/opkg/istoreos-files/ntfsprogs）硬依赖 feed 包，是这批缺失里**最早撞墙**的一部分，不是全部。

## 八、第三次失败：上游源码 404（run 37347586447 = r4，17:19Z→21:08Z）

前两层已确认修好：`Collected errors` **0** 条、dnsmasq 没被加回、一路跑到编译并在 3.8 小时后挂掉。唯一失败点是 `package/feeds/third/vlmcsd`：

- feed 的 Makefile 用 `PKG_SOURCE_URL_FILE:=$(PKG_VERSION).tar.gz` 去抓 `…/archive/refs/tags/1113.tar.gz`，可上游 tag 实际叫 **`svn1113`**（`gh api repos/Wind4/vlmcsd/tags`）。GitHub + sources.cdn + sources.openwrt + mirror2 四路全 404 → `No more mirrors to try - giving up.`
- **内容没变，只是远端文件名错**：实测 `https://github.com/Wind4/vlmcsd/archive/refs/tags/svn1113.tar.gz` 的 sha256 = feed 里的 `PKG_HASH`（`62f55c48…42cc`）。

修法（**不改 feed 源码**，vlmcsd 是 §三 在用项也不从 seed 删）：CI 在 `make download` 前把它按 dl 目标名预放进 `dl/vlmcsd-1113.tar.gz`，哈希取自 feed 的 Makefile 现场校验。成立依据是 `include/download.mk:350` 的 `$(DL_DIR)/$(FILE)` 规则无前提——文件已在就视为最新；`include/package.mk:214` 的 `check_download_integrity` 只在**哈希不符**时才补 FORCE（:77）。离线三步验证过：首次落位、再跑跳过、内容错则 rc=1 且不留正式文件。

顺带堵第二道延迟：`make download` 对失败包只打 `ERROR: package/… failed to build`、**退出码仍是 0**（r4 步 9 绿，而日志 4448 行已经有这条 ERROR），所以 Download sources 现在自己扫日志并失败退出——死源码在几分钟内暴露，不再等 3.8 小时。

**功能视角**：没有增删任何功能，vlmcsd 仍在固件里。

## 九、r4 审计定档：106 行未生效的真实构成

`seed 想要 697 → defconfig 后开启 705 → 丢失 106`（展开 `.config` 在 artifact 里叫 `config-expanded.txt`；此前写 `.config` 上传不到，dot 文件被 glob 跳过了）。

**符号不存在 104 行**，两类：

1. **带 ABI 后缀的 opkg 二进制包名** 61 行（`libcurl4` `libgcc1` `libubus20250102` `libruby3.3` …）。kconfig 符号是无后缀的 `libcurl`/`libubus`，后缀只出现在打包出的包名上。死行，库随依赖自动进镜像——已在 §十 清掉。
2. **iStoreOS 商店应用**（其余 43 行）：`luci-app-openclash`、`luci-app-tailscale-community`、`quickstart`/`luci-app-quickstart`/`luci-i18n-quickstart-zh-cn`、全部 `app-meta-*`、`luci-app-{cpufreq,fan,eqos,oaf,diskman,fastnet,floatip,gowebdav,openclawmgr}`、`luci-lib-mac-vendor`、`linkmount`、`fastnet`、`floatip`、`gowebdav`、`webdav2`、`appfilter`、`kmod-oaf`、`aria2-entry-deps`、`luci-js-deps`、`transmission-daemon-openssl`、`jansson4`。
   - **证据**：`feeds.conf.default` 与上游 `istoreos/istoreos@istoreos-24.10` 逐字相同（只有 packages/luci/routing/telephony/store/third 六个 feed），而 defconfig 后 `tmp/.config-package.in` 的 **11910** 个包符号里 `quickstart|openclash|app-meta|diskman|eqos|oaf|fastnet|floatip|linkmount|appfilter` 命中 **0**。
   - 这些应用住在**没写进 feeds.conf 的仓库**：`jjm2473/openwrt-app-meta`（`applications/app-meta-*`）、`jjm2473/openwrt-apps`（`luci-app-cpufreq`/`luci-app-fan`/`luci-lib-mac-vendor`）、`istoreos/quickstart`、`istoreos/istoreos-app-hub`（`apps/quickstart,fastnet,floatip,linkmount,webdav2,…`）。
   - 也就是说 §六 的基准（路由器 `opkg list-installed` 1122 包）**混入了刷机后从 iStore 商店运行时安装的包**，它们从来不是本仓库的构建期候选；裁剪台账里它们的"已删/保留"都是虚账。
   - 反面确认：商店自身在——`luci-app-store`、`dkml`、`istoreos-files`、`tailscale`（守护进程）都有符号且已开启，刷完机仍可从商店逐个装回。

**符号存在却没开成 2 行**：`kmod-thermal`、`kmod-xdp-sockets-diag`——内核内建符号没开（需 `make kernel menuconfig`，或该 target 未 support），与 feed 无关。

**已定（2026-10-06，用户选）**：**不**往 `feeds.conf` 追加商店 feed，维持"固件只留路由栈 + 商店本体，刷机后从 iStore 商店装回 openclash / tailscale UI / quickstart / eqos …"。理由是这台机器的定位是纯网关，镜像尺寸优先；随之把 104 行死 seed 清掉，见 §十。

## 十、清掉 104 行"从未生效"的 seed 行（2026-10-06，697 → 593）

### 功能视角

**设备能做的事零变化**——这 104 行自写进 seed 起就是空转（符号不存在，defconfig 无警告删除），删掉它们不移除任何一块已烘焙的功能；固件产物与清理前逐包相同。

要交代的不是"删了什么"，而是**刷机后必须自己装回的东西**（原先误以为已在固件里）：OpenClash、Tailscale 的 LuCI 配置页（守护进程 `tailscale` 确实在，可先用 UCI/`/etc/config/tailscale` 配）、iStoreOS 首页 quickstart、eqos IP 限速、oaf/appfilter 应用过滤、cpufreq 与风扇调节、diskman 磁盘管理、gowebdav/fastnet/floatip/webdav2、aria2 与 transmission 的入口与商店元数据。装回途径：LuCI → iStore 商店（本体 `luci-app-store` + `dkml` 已在固件）。

### 包名明细（全部为「符号不存在」的死行，按档位列全）

**A 库类——带 ABI 后缀的 opkg 包名（61）**：jansson4、libatomic1、libblkid1、libblobmsg-json20240329、libbpf1、libbz2-1.0、libcomerr0、libcurl4、libe2p2、libelf1、libevent2-7、libevent2-core7、libevent2-pthreads7、libext2fs2、libf2fs6、libfdisk1、libfuse1、libgcc1、libgmp10、libipset13、libiptext-nft0、libiptext0、libiptext6-0、libjson-c5、libjson-script20240329、libkeyutils1、liblua5.1.5、liblucihttp0、liblzo2、libmbedtls21、libmnl0、libmount1、libncurses6、libnetfilter-conntrack3、libnettle8、libnfnetlink0、libnftnl11、libnghttp2-14、libnl-tiny1、libopenssl3、libpcap1、libpopt0、libpsl5、libreadline8、libruby3.3、libsensors5、libsmartcols1、libsqlite3-0、libss2、libstdcpp6、libsysfs2、libubox20240329、libubus20250102、libuci20250120、libuclient20201210、libucode20230711、libusb-1.0-0、libustream-mbedtls20201210、libuuid1、libuv1、libxtables12

**B 商店元数据 app-meta-*（9）**：app-meta-{aria2,eqos,fastnet,floatip,gowebdav,openclawmgr,openlist,transmission,vlmcsd}

**C 商店 LuCI 前端（24）**：luci-app-{cpufreq,diskman,eqos,fan,fastnet,floatip,gowebdav,oaf,openclash,openclawmgr,quickstart,tailscale-community}、luci-i18n-{cpufreq,diskman,eqos,fan,fastnet,floatip,gowebdav,oaf,openclawmgr,quickstart}-zh-cn、luci-js-deps、luci-lib-mac-vendor

**D 其他商店主包/入口（10）**：appfilter、aria2-entry-deps、fastnet、floatip、gowebdav、kmod-oaf、linkmount、quickstart、transmission-daemon-openssl、webdav2

**保留未动**：`kmod-thermal`、`kmod-xdp-sockets-diag`——这两行符号真实存在，只是内核内建项没开，属"真缺"而非"死行"，要恢复得动 `make kernel menuconfig`，不能从 seed 里一删了之。D 档（§六）里点名要查依赖的 `linkmount` 也在这批被清掉了：它根本不是构建期候选，路由器上那份是商店装的。

## 十一、第四次失败：缓存死锁——每次都被自家 timeout 杀在半路（run 37422215944，2026-10-06）

`conclusion: cancelled` 不是人取消的，是 workflow 自己的 `timeout-minutes: 350` 到点被 GitHub 杀掉：job 06:09:37Z 起跑、12:00:21Z 终止，正好 5h50m44s。前 10 步全绿，Compile（06:40:26 开始 `make world`）被杀时正在编 **ruby**。里程碑实测：tools/compile 1h25m → toolchain/compile 23m → target/compile 15m → package/compile 3h17m 才到 ruby 中段——**4 核托管 runner 上全量冷编译约需 7h+，350 分钟根本装不下**。

真正的病是**死循环**：`actions/cache@v4` 的缓存保存在 post 步骤里，`post-if: success()`——job 不成功就不存。而这个仓库 6 次 run 无一成功（`gh cache list` 实测 0 条），于是每次都全量冷编 → 每次都超时取消 → 永远存不上缓存 → 下次还是冷编。此前 §八 修的 vlmcsd 预置在本次 run 是生效的（step 9 绿），不是本症。

**GitHub Actions 取消语义实测**（本次 run 的步骤清单为证，非推断）：job 被 timeout 取消后，`if: always()` 的步骤**照常执行**（Report disk usage 在 12:00:17Z 留下了 df 输出），post 步骤里 `post-if: success()` 的被跳过（Post Cache conclusion=skipped）。所以出路是把"保存"从 post 挪到普通步骤并挂 `always()`。

**修法**（借鉴 draco-china/istoreos-actions 所用 `klever1988/cachewrtbuild` 的机制，不引入第三方 action，用官方 `actions/cache` 的 restore/save 拆分实现）：

- 缓存拆两对独立 restore+save，key 按用途分前缀（`istoreos-dl-<run_id>` / `istoreos-tc-<run_id>`，restore-keys 前缀滚动复用）：
  - `dl`：Save downloads cache 紧跟 Download sources，挂 `always()`——此刻 job 还健康，上传从容，编译超时也保住这 28 分钟的下载
  - `staging_dir`：Save toolchain cache 在 Compile 后，挂 `always()`——**被超时取消也会存**，下次 run 恢复后 tools/toolchain 靠 `staging_dir/*/stamp` 直接跳过，从 package/compile 续编（约 4.5–5h，350 分钟内可完成，死循环即破）
- 缓存路径去掉顶层 `toolchain/`（源码目录，无缓存价值，编译产物在 `staging_dir/`）；`staging_dir` 整目录保留（含 target-* 的内核 stamp）
- 恢复时 tools/toolchain 会逐个查 stamp 后空跑（几分钟 no-op 检查），不用 cachewrtbuild 那招 sed 改顶层 Makefile——不改源码树的文件，符合本仓库纪律

**参考项目的现状警示**：draco-china/istoreos-actions 最近 20 次 run 全 failure（多为 3 分钟早夭，另有一次 360.3 分钟撞 6h 平台上限），只能借鉴机制不能照抄现状；它的 cachewrtbuild 同样 `post-if: success()`，首次成功前的 bootstrap 问题在我们这里用 `always()` save 解决。

**功能视角**：没有增删任何功能、没有动 seed。构建基础设施修复，预期下一次 run 仍可能超时一次（存下 staging_dir），再下一次即可续编成功；成功一次后缓存齐备，后续构建显著缩短。

