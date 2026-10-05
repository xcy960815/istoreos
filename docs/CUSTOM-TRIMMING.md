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

## 二、删除清单（2026-10-05，用户要求）

| 类别 | 被删的包 | 原因 |
|---|---|---|
| Docker 全家桶 | containerd、docker、dockerd、docker-compose、runc、tini、libdevmapper、libseccomp、docker-deps、luci-app-dockerman、luci-app-dpanel、app-meta-dpanel、luci-lib-docker 及 i18n | Docker 服务已全部迁往 9400F Ubuntu 服务器（192.168.100.10），路由器不再跑容器 |
| Samba/文件共享 | samba4-server、samba4-libs、luci-app-samba4、kmod-fs-ksmbd、unishare、luci-app-unishare 及 i18n | 路由器不再做 NAS/文件共享；文件服务归 9400F/N100 |
| DDNS（三套） | ddns-scripts 全系列（含 cloudflare/dnspod/services/aliyun）、luci-app-ddns、ddns-go、app-meta-ddnsgo、luci-app-ddns-go、ddnsto、luci-app-ddnsto 及 i18n | 远程访问统一走 Tailscale，不需要公网 DDNS，减少暴露面 |
| UPnP | miniupnpd-nftables、luci-app-upnp、libminiupnpc 及 i18n | 无使用需求，减少暴露面 |
| Linkease 系 | linkease、luci-app-linkease、ddnsto 同属 Linkease 生态 | 未使用 |

## 三、保留清单（有实际使用证据，后续 AI 不要当成"没用"误删）

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

1. `make defconfig` 会把"仍被保留包硬依赖"的项自动加回 `=y`——刷前 diff 展开的 `.config` 与 seed，多出的行即被拉回的依赖（已知候选：libiwinfo 被 rpcd-mod-iwinfo 拉回、mdadm 可能被 luci-app-diskman 拉回，均无害）
2. **软依赖**（脚本 shell 调用而非包依赖）不会被自动拉回——QEMU 启动验证 + 刷机后核对 LuCI 各页（重点：quickstart、磁盘管理、iStore 商店）照 BUILD-CUSTOM.md 流程走
3. `dkml`（iStoreOS 动态内核模块加载器，package/diy/dkml）**保留**：iStore 商店装内核模块类应用的基础设施
