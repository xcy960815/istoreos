# iStoreOS 裁剪版构建指南（J4125 专用）

基于官方 `istoreos-24.10` 分支 + 本仓库 `config-custom.seed`，为我的 J4125（四口 2.5G i226-V）构建裁剪版固件。

## 裁剪原则

**改动只在 `config-custom.seed` 一个文件里，不改任何源码** —— 这样每次同步上游修复都是无痛合并。

| 处理 | 内容 | 理由 |
|---|---|---|
| ❌ 删除（首轮 2026-10-05） | Docker 全家桶 / Samba 文件共享 / OpenWrt 自带 DDNS（luci-app-ddns） / UPnP / Linkease 系（含 ddnsto） | Docker 已迁往 9400F；公网域名用 DDNS-Go，不用自带那套也不用 ddnsto。包名明细见 `docs/CUSTOM-TRIMMING.md` §二、§十五 |
| ❌ 二次裁剪(2026-10-05) | 无线全家/蜂窝modem全家/GPU固件与DRM/NFS·SMB存储/l2tp-pptp-sstp-gre-ipip-ipsec隧道/KVM宿主/Docker孤儿kmod/老式网卡驱动 | J4125 无对应硬件；文件服务归 9400F/N100。明细见 `docs/CUSTOM-TRIMMING.md` §六 |
| ✅ 保留（固件里确实有） | 基础网络栈 / kmod-igc / firewall4 / dnsmasq-full / IPv6 / **tailscale 1.104.1 + luci-app-tailscale** / **ddns-go + luci-app-ddns-go** / openlist（含 WebDAV） / vlmcsd / ttyd / wol / zram / lm-sensors / argon 主题 / iStore 商店本体（luci-app-store、dkml） / **smartmontools + mdadm**（给首页磁盘信息查询，不是侧栏 SMART/RAID） | 路由器命根子 + 确实保留的服务。`smartd` 已删；filetransfer 已删、挂载点菜单已藏（§三十一），`luci-mod-system` 和 sftp 仍留 |
| 📦 刷机后从 iStore 商店装回（**不在构建期**） | openclash、eqos、oaf、cpufreq、luci-app-fan、diskman、gowebdav、fastnet、floatip | 这些名字在默认 feed 里没有 kconfig 符号，写进 seed 也进不了镜像。证据与逐条清单见 `docs/CUSTOM-TRIMMING.md` §九/§十。**DDNS-Go、Tailscale LuCI 不在此列**（r17 已烘焙）。**QuickStart 首页方案已推送、随 r19 构建（§二十三），r17 还没有** |
| ➕ 新增 | irqbalance；`feeds.conf.default` 的 `src-git ddnsgo`（sirpdboy/luci-app-ddns-go）；CI/本地在 defconfig 前跑 `pin-tailscale-prebuilt.sh`、`pin-quickstart.sh`、`drop-luci-theme-bootstrap.sh` | irqbalance：四张 2.5G 网卡中断分摊。ddnsgo feed：六个默认 feed 没有 DDNS-Go。Tailscale 最新稳定版不能用本树 Go 1.23.12 从源码编，改用官方 amd64 预编译 + asvow LuCI，见 `docs/CUSTOM-TRIMMING.md` §二十二。QuickStart 只 clone 两个包、首页去掉 Samba/易有云/下载/ddnsto，存储服务只留 WebDAV，侧栏不要 RAID/SMART、不要挂载点，留下 smartmontools+mdadm 给磁盘信息，见 §二十三/§三十一/§三十二/§三十三。Bootstrap 主题：`luci-light` 硬依赖，要脚本拆掉，见 §二十四 |

参数：EFI+BIOS 双引导、只要 squashfs（显式关掉 x86 默认的 ext4 根镜像）、kernel 分区 32MB、root 分区 512MB、另出一份 EFI LiveCD ISO（Ventoy 可启动，**不是**一键安装器）、中文界面。224MB+默认 ext4 会在 `make_ext4fs` 阶段把 `target/linux` 打挂，见 `docs/CUSTOM-TRIMMING.md` §十七。Ventoy 装到 N100 傲腾的步骤见 §十九。

## 构建步骤（Ubuntu 22.04/24.04 x86_64，建议在 9400F 装好系统后进行）

```bash
# 1. 依赖（清单与 CI 共用一份 .github/apt-packages.txt，只改那一处两边就都生效）
sudo apt update
sudo apt-get install -y $(grep -vE '^[[:space:]]*(#|$)' .github/apt-packages.txt)
# Ubuntu 22.04 另需：sudo apt-get install -y python3-distutils（24.04 已移除该包，所以不在清单里）

# 2. 进入源码
cd istoreos

# 3. 更新 feeds（国内网络建议挂代理：export http_proxy=http://路由器IP:7893 之类）
./scripts/feeds update -a
./scripts/feeds install -a

# 3b. 修 third feed 里 vlmcsd 的两处笔误（上游 tag 叫 svn1113 而 feed 写成 1113，构建目录名也少了 svn 前缀）。
#     不修的话编到 vlmcsd 必挂："No targets specified and no makefile found"，机制见 §十三
#     若 feed 已改写法（如 PKG_VERSION 自带 svn），这两条不会匹配，确认无 svnsvn 即可
m=package/feeds/third/vlmcsd/Makefile
sed -e 's|^PKG_SOURCE_URL_FILE:=\$(PKG_VERSION)\.tar\.gz$|PKG_SOURCE_URL_FILE:=svn$(PKG_VERSION).tar.gz|' \
    -e 's|^PKG_BUILD_DIR:=\$(BUILD_DIR)/\$(PKG_NAME)-\$(PKG_VERSION)$|PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-svn$(PKG_VERSION)|' \
    "$m" > "$m.tmp" && mv "$m.tmp" "$m" && grep -E '^PKG_(VERSION|SOURCE_URL_FILE|BUILD_DIR):=' "$m"

# 3c. Tailscale 换成官方 amd64 预编译 + 烘焙 LuCI（必须在 defconfig 之前，LuCI 符号这时才存在）
#     不跑的话固件仍是 feed 里的 1.80.3、没有 Tailscale 页面。见 docs/CUSTOM-TRIMMING.md §二十二
bash .github/scripts/pin-tailscale-prebuilt.sh

# 3d. QuickStart 首页（只 clone 两个包，不拉 app-hub）。不跑的话 seed 里 luci-app-quickstart 是死行，登录仍是 Argon 概览。见 §二十三
bash .github/scripts/pin-quickstart.sh

# 3e. luci-light 默认依赖 Bootstrap 主题。不改的话 seed 删了也会被 defconfig 加回。见 §二十四
bash .github/scripts/drop-luci-theme-bootstrap.sh

# 4. 应用裁剪配置
cp config-custom.seed .config
make defconfig            # 展开成完整 .config（实际包数以首次构建日志为准）

# 5. 下载源码包 + 编译
make download -j8
make -j$(nproc)
# 本地失败后可以 make -j1 V=s 重跑细看；CI 里不能这么干，原因见 docs/CUSTOM-TRIMMING.md §十二

# 6. 产物
ls bin/targets/x86/64/
# istoreos-*-x86-64-generic-squashfs-combined-efi.img.gz  ← 写进硬盘/U 盘（J4125、N100 傲腾）
# istoreos-*-x86-64-generic-image-efi.iso                 ← 丢进 Ventoy 的 LiveCD，见 docs/CUSTOM-TRIMMING.md §十九
```

## 上线路径（主路由！先验证再刷）

**2026-10-16**：能刷的是 **r17**（Tailscale 1.104.1 + DDNS-Go，Argon 概览、没有 QuickStart 首页）。**先 N100 试刷，不要刷 J4125**。N100 已经用 U 盘当系统盘开过机。用户装官方也是 **img 整盘写入**（不是 ISO、不是 Ventoy 菜单）。Mac 网线接 N100 第二口、`192.168.100.2`、网关留空，http://192.168.100.1。禁止双公头 USB 线连 Mac↔N100。首页/Bootstrap 改动已推送（`5612b37936`），r19 重跑中；构建成功后镜像自动发仓库 Releases（§二十五）。快照见 `docs/CUSTOM-TRIMMING.md` 文首。


1. **QEMU 验证**：`qemu-system-x86_64 -nographic -hda bin/targets/x86/64/istoreos-*-combined-efi.img` 确认可启动、包齐全
2. **备份现系统**：LuCI → 系统 → 备份升级（导出 `/etc/config`）；稳妥起见把系统盘整盘 dd 备份一份
3. **写盘**：新镜像 gz 解压后 dd 到系统盘（或 LuCI sysupgrade）
4. **恢复配置**：`/etc/config` 里的 network/firewall/dhcp/tailscale/**ddns-go** 等恢复回去（dockerd/dpanel/samba、OpenWrt 自带 luci-app-ddns、ddnsto 相关配置直接不要了）
5. 验证 WAN 拨号、四个 2.5G 口、**LuCI 里已有 Tailscale 和 DDNS-Go**（r17 起不用进商店）。**QuickStart 首页和侧栏「网络向导」要等 r19 构建**（§二十三，已推送未构建）；有首页之后不应出现 Samba/易有云/下载器/OTA/Docker 卡片。**openclash / eqos / cpufreq / fan / diskman 这些不在固件里**，按需从 LuCI → iStore 商店装回再验
6. 旧盘留作回滚

## 上游同步工作流（fork 维护）

- 本仓库 origin = `xcy960815/istoreos`（我的 fork），upstream = `istoreos/istoreos`（官方）
- 同步官方修复（网页版：fork 页面点 **Sync fork**；或命令行）：

```bash
git fetch upstream
git checkout istoreos-24.10
git merge --ff-only upstream/istoreos-24.10   # 本分支只做 ff，保持零冲突
git push origin istoreos-24.10                 # fork 镜像分支也跟上（ff 推送）
git checkout custom-24.10
git rebase istoreos-24.10                    # 裁剪分支只有一个 seed 文件，rebase 无痛
git push --force-with-lease origin custom-24.10  # rebase 改写了已推送历史；--force-with-lease 远端被别处改过时会拒绝覆盖
```

- 由于全部定制收敛在一个 seed 文件，上游 99% 的提交都与它无冲突；符号改名（罕见）时 `make defconfig` 会静默丢掉那一行，本地不会有任何提示；CI 的 seed 审计会把"已知清单外的未生效行"判失败（几分钟内），看 artifact 里的 seed-audit.txt 按报告改 seed。本地构建后可自己跑 `bash .github/scripts/seed-audit.sh` 检查
- 云端构建走本仓库自己的 workflow（不引 P3TERX 等第三方模板；r10 起稳定出镜像，最近一次成功是 r17）：`.github/workflows/build-istoreos.yml` 手动触发，seed 审计逻辑在 `.github/scripts/seed-audit.sh`（装好 feeds、跑过 defconfig 后可本地执行）。取舍理由见 `docs/CUSTOM-TRIMMING.md` §十二。构建成功后镜像自动发 GitHub Releases（tag `r<run_number>`，长期下载位；Actions artifact 仍在、14 天过期），见 `docs/CUSTOM-TRIMMING.md` §二十五

## 备注

- seed 基准取自 2026-10-05 路由器实际安装清单（`opkg list-installed` 1122 包）。可核实的数字：seed 自身 `CONFIG_PACKAGE_*` 行 首轮 1078 → 二次裁剪 697 → 清死行后 593 → 2026-10-09 加回 DDNS-Go 后 596 → 2026-10-10 删 Aria2/Transmission 后 587 → 2026-10-12 删在线升级 OTA 后 585 → 2026-10-14 烘焙 Tailscale LuCI 后 587 → 2026-10-16 烘焙 QuickStart 后 590 → **去掉 Bootstrap 主题后 589**（`grep -c '^CONFIG_PACKAGE_' config-custom.seed` 可复核）；r4 那次 `make defconfig` 展开选中 **705**（含 defconfig 自行加回的 114 个）。镜像最终包数以成功构建的 `manifest` 为准
- **商店应用不在构建期**：上面「📦 刷机后从 iStore 商店装回」那一行的包名，在 `feeds.conf.default` 的默认 feed 里根本没有对应 kconfig 符号，写进 seed 也是死行。已烘焙的例外：`src-git ddnsgo`、`pin-tailscale-prebuilt.sh`、`pin-quickstart.sh`。证据见 `docs/CUSTOM-TRIMMING.md` §九，逐条清单见 §十——包名只在那两处维护，本文不再重列
- **上面第 3、4 步的顺序不能调换**：`make defconfig` 早于 `feeds install` 会静默删掉所有 feed 包的 `=y` 行（符号还不存在），那次构建的产物连 LuCI 都没有。`make download` 也有坑：它对失败包只打 ERROR、退出码仍是 0。两道坑的机制与修法复盘在 §七、§八
- **云构建现状（r7 = run 37470180070 冷缓存实测）**：tools 1h14m43s + toolchain 20m55s + target 12m57s + package/compile 约 2h，全量冷编 **约 4h15m–4h45m**（此前"7h+ 装不下 350 分钟"的推断来自被 timeout 杀掉的 r6，它从没测到终点，已更正）。`dl` 缓存收益确定（省掉实测那 28m01s 的下载）；`staging_dir` 缓存"靠 stamp 续编"已被 `rules.mk`/`package.mk` 证伪（`.built` 在 `build_dir`），CI 已删掉这份缓存省配额；`build_dir` 体积仍由 Report disk usage 实测，用于决定是否上 9400F 自建 runner（见 docs/CUSTOM-TRIMMING.md §十一、§十三）
- 恢复某个删除的功能：iStore 商店装回（临时），或往 seed 加一行 `CONFIG_PACKAGE_xxx=y`（长期，仅对该符号确实存在于 feed 时有效）
