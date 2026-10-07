# iStoreOS 裁剪版构建指南（J4125 专用）

基于官方 `istoreos-24.10` 分支 + 本仓库 `config-custom.seed`，为我的 J4125（四口 2.5G i226-V）构建裁剪版固件。

## 裁剪原则

**改动只在 `config-custom.seed` 一个文件里，不改任何源码** —— 这样每次同步上游修复都是无痛合并。

| 处理 | 内容 | 理由 |
|---|---|---|
| ❌ 删除（首轮 2026-10-05） | Docker 全家桶 / Samba 文件共享 / DDNS 三套 / UPnP / Linkease 系 | Docker 已迁往 9400F，远程只走 Tailscale；包名明细见 `docs/CUSTOM-TRIMMING.md` §二 |
| ❌ 二次裁剪(2026-10-05) | 无线全家/蜂窝modem全家/GPU固件与DRM/NFS·SMB存储/l2tp-pptp-sstp-gre-ipip-ipsec隧道/KVM宿主/Docker孤儿kmod/老式网卡驱动 | J4125 无对应硬件；文件服务归 9400F/N100；远程只走 Tailscale。明细见 `docs/CUSTOM-TRIMMING.md` §六 |
| ✅ 保留（固件里确实有） | 基础网络栈 / kmod-igc / firewall4 / dnsmasq-full / IPv6 / tailscale 守护进程 / aria2+ariang / transmission / openlist / vlmcsd / ttyd / wol / zram / smartd+lm-sensors / wireguard / argon 主题 / iStore 商店本体（luci-app-store、dkml） | 路由器命根子 + 确实在用的服务 |
| 📦 刷机后从 iStore 商店装回（**不在构建期**） | openclash、tailscale 的 LuCI 配置页、quickstart、eqos、oaf、cpufreq、luci-app-fan、diskman、gowebdav、fastnet、floatip | 这些名字在六个 feed 里没有 kconfig 符号，写进 seed 也进不了镜像；证据与逐条清单见 `docs/CUSTOM-TRIMMING.md` §九/§十 |
| ➕ 新增 | irqbalance | 四张 2.5G 网卡中断分摊到 4 核 |

参数与官方镜像对齐：EFI+BIOS 双引导、squashfs、root 分区 224MB、中文界面。

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
m=package/feeds/third/vlmcsd/Makefile
sed -e 's|^PKG_SOURCE_URL_FILE:.*|PKG_SOURCE_URL_FILE:=svn$(PKG_VERSION).tar.gz|' \
    -e 's|^PKG_BUILD_DIR:.*|PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-svn$(PKG_VERSION)|' \
    "$m" > "$m.tmp" && mv "$m.tmp" "$m"

# 4. 应用裁剪配置
cp config-custom.seed .config
make defconfig            # 展开成完整 .config（实际包数以首次构建日志为准）

# 5. 下载源码包 + 编译
make download -j8
make -j$(nproc)
# 本地失败后可以 make -j1 V=s 重跑细看；CI 里不能这么干，原因见 docs/CUSTOM-TRIMMING.md §十二

# 6. 产物
ls bin/targets/x86/64/
# istoreos-24.10-x86_64-squashfs-combined-efi.img.gz  ← 就是这个
```

## 上线路径（主路由！先验证再刷）

1. **QEMU 验证**：`qemu-system-x86_64 -nographic -hda bin/targets/x86/64/istoreos-*-combined-efi.img` 确认可启动、包齐全
2. **备份现系统**：LuCI → 系统 → 备份升级（导出 `/etc/config`）；稳妥起见把系统盘整盘 dd 备份一份
3. **写盘**：新镜像 gz 解压后 dd 到系统盘（或 LuCI sysupgrade）
4. **恢复配置**：`/etc/config` 里的 network/firewall/dhcp/tailscale 等恢复回去（dockerd/dpanel/samba/ddns 相关配置直接不要了）
5. 验证 WAN 拨号、四个 2.5G 口、Tailscale 连通；**openclash / tailscale UI / quickstart / eqos / cpufreq / fan / diskman 这些不在固件里**，先在 LuCI → iStore 商店装回再验（原因见 `docs/CUSTOM-TRIMMING.md` §九/§十）
6. 旧盘留作回滚

## 上游同步工作流（fork 维护）

- 本仓库 origin = `xcy960815/istoreos`（我的 fork），upstream = `istoreos/istoreos`（官方）
- 同步官方修复（网页版：fork 页面点 **Sync fork**；或命令行）：

```bash
git fetch upstream
git checkout istoreos-24.10
git merge --ff-only upstream/istoreos-24.10   # 本分支只做 ff，保持零冲突
git checkout custom-24.10
git rebase istoreos-24.10                    # 裁剪分支只有一个 seed 文件，rebase 无痛
git push origin custom-24.10
```

- 由于全部定制收敛在一个 seed 文件，上游 99% 的提交都与它无冲突；`make defconfig` 后如遇符号改名（罕见），构建时会提示，按提示改 seed 即可
- 云端构建走本仓库自己的 workflow（不引 P3TERX 等第三方模板；注意它至今还没有一次成功的 run）：`.github/workflows/build-istoreos.yml` 手动触发，seed 审计逻辑在 `.github/scripts/seed-audit.sh`（装好 feeds、跑过 defconfig 后可本地执行）。取舍理由见 `docs/CUSTOM-TRIMMING.md` §十二

## 备注

- seed 基准取自 2026-10-05 路由器实际安装清单（`opkg list-installed` 1122 包）。可核实的数字：seed 自身 `CONFIG_PACKAGE_*` 行 首轮 1078 → 二次裁剪 697 → 清死行后 593（现值，`grep -c '^CONFIG_PACKAGE_' config-custom.seed` 可复核）；r4 那次 `make defconfig` 展开选中 **705**（含 defconfig 自行加回的 114 个）。镜像最终包数以成功构建的 `manifest` 为准
- **商店应用不在构建期**：上面「📦 刷机后从 iStore 商店装回」那一行的包名，在 `feeds.conf.default` 的六个 feed 里根本没有对应 kconfig 符号，写进 seed 也是死行。证据见 `docs/CUSTOM-TRIMMING.md` §九，逐条清单见 §十——包名只在那两处维护，本文不再重列
- **上面第 3、4 步的顺序不能调换**：`make defconfig` 早于 `feeds install` 会静默删掉所有 feed 包的 `=y` 行（符号还不存在），那次构建的产物连 LuCI 都没有。`make download` 也有坑：它对失败包只打 ERROR、退出码仍是 0。两道坑的机制与修法复盘在 §七、§八
- **云构建现状（r7 = run 37470180070 冷缓存实测）**：tools 1h14m43s + toolchain 20m55s + target 12m57s + package/compile 约 2h，全量冷编 **约 4h15m–4h45m**（此前"7h+ 装不下 350 分钟"的推断来自被 timeout 杀掉的 r6，它从没测到终点，已更正）。`dl` 缓存收益确定（省掉实测那 28m01s 的下载）；`staging_dir` 缓存"靠 stamp 续编"已被 `rules.mk`/`package.mk` 证伪，判据是下次 run 的 `tools/compile` 时长（见 `docs/CUSTOM-TRIMMING.md` §十一「复核更正」与 §十三）
- 恢复某个删除的功能：iStore 商店装回（临时），或往 seed 加一行 `CONFIG_PACKAGE_xxx=y`（长期，仅对该符号确实存在于 feed 时有效）
