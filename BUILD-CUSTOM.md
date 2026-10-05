# iStoreOS 裁剪版构建指南（J4125 专用）

基于官方 `istoreos-24.10` 分支 + 本仓库 `config-custom.seed`，为我的 J4125（四口 2.5G i226-V）构建裁剪版固件。

## 裁剪原则

**改动只在 `config-custom.seed` 一个文件里，不改任何源码** —— 这样每次同步上游修复都是无痛合并。

| 处理 | 内容 | 理由 |
|---|---|---|
| ❌ 删除 | containerd/docker/dockerd/docker-compose/runc/luci-app-dockerman/dpanel | Docker 已迁往 9400F 服务器 |
| ❌ 删除 | samba4-server/luci-app-samba4/kmod-fs-ksmbd/unishare | 路由器不再做文件共享 |
| ❌ 删除 | ddns-scripts 全家/ddns-go/ddnsto/luci-app-ddns* | 远程访问走 Tailscale，不需要 DDNS |
| ❌ 删除 | miniupnpd/luci-app-upnp | 减少暴露面，无使用需求 |
| ❌ 删除 | linkease/luci-app-linkease | 未使用 |
| ❌ 二次裁剪(2026-10-05) | 无线全家/蜂窝modem全家/GPU固件与DRM/NFS·SMB存储/l2tp-pptp-sstp-gre-ipip-ipsec隧道/KVM宿主/Docker孤儿kmod/老式网卡驱动 | J4125 无对应硬件；文件服务归 9400F/N100；远程只走 Tailscale。明细见 docs/CUSTOM-TRIMMING.md §六 |
| ✅ 保留 | 基础网络栈/kmod-igc/firewall4/dnsmasq/IPv6 | 路由器命根子 |
| ✅ 保留 | tailscale + luci-app-tailscale-community | 全家远程入口 |
| ✅ 保留 | openclash/aria2/transmission/openlist/gowebdav/vlmcsd/eqos/oaf/ttyd/wol/cpufreq/fan | 实际在用（有活跃配置） |
| ✅ 保留 | istore/quickstart/luci-app-store/argon | 系统管理骨架与应用商店 |
| ➕ 新增 | irqbalance | 四张 2.5G 网卡中断分摊到 4 核 |

参数与官方镜像对齐：EFI+BIOS 双引导、squashfs、root 分区 224MB、中文界面。

## 构建步骤（Ubuntu 22.04/24.04 x86_64，建议在 9400F 装好系统后进行）

```bash
# 1. 依赖
sudo apt update && sudo apt install -y build-essential clang flex bison g++ gawk \
  gcc-multilib g++-multilib gettext git libncurses-dev libssl-dev python3 \
  python3-distutils rsync unzip zlib1g-dev file wget curl

# 2. 进入源码
cd istoreos

# 3. 更新 feeds（国内网络建议挂代理：export http_proxy=http://路由器IP:7893 之类）
./scripts/feeds update -a
./scripts/feeds install -a

# 4. 应用裁剪配置
cp config-custom.seed .config
make defconfig            # 展开成完整 .config（实际包数以首次构建日志为准）

# 5. 下载源码包 + 编译
make download -j8
make -j$(nproc) V=s

# 6. 产物
ls bin/targets/x86/64/
# istoreos-24.10-x86_64-squashfs-combined-efi.img.gz  ← 就是这个
```

## 上线路径（主路由！先验证再刷）

1. **QEMU 验证**：`qemu-system-x86_64 -nographic -hda bin/targets/x86/64/istoreos-*-combined-efi.img` 确认可启动、包齐全
2. **备份现系统**：LuCI → 系统 → 备份升级（导出 `/etc/config`）；稳妥起见把系统盘整盘 dd 备份一份
3. **写盘**：新镜像 gz 解压后 dd 到系统盘（或 LuCI sysupgrade）
4. **恢复配置**：`/etc/config` 里的 network/firewall/dhcp/tailscale 等恢复回去（dockerd/dpanel/samba/ddns 相关配置直接不要了）
5. 验证 WAN 拨号、四个 2.5G 口、Tailscale 连通、openclash 可用
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
- 想云端编译可配 GitHub Actions（P3TERX/Actions-OpenWrt 模板），仓库里放 seed 即可，不受本地环境影响

## 备注

- seed 基准取自 2026-10-05 路由器实际安装清单（`opkg list-installed` 1122 包）。可核实的数字只有 seed 自身的 `CONFIG_PACKAGE_*` 行数：首轮 1078 → 同日二次裁剪后 697。`make defconfig` 展开后的**实际包数尚未实测**（Actions 至今 0 次运行），以首次构建日志为准
- `luci-app-tailscale-community` 等 store 源包在 feeds install 后自动可用；若个别符号在新版被改名，defconfig 会丢弃该行，构建后用 `opkg list-installed | grep tailscale` 核对
- **上面第 3、4 步的顺序不能调换**：`make defconfig` 早于 `feeds install` 会静默删掉所有 feed 包的 `=y` 行（符号还不存在），要到 rootfs 装配才炸。Actions workflow 现已在 defconfig 后 diff seed 与被丢弃的行，非空即失败；复盘见 `docs/CUSTOM-TRIMMING.md` §七
- 恢复某个删除的功能：iStore 商店装回（临时），或往 seed 加一行 `CONFIG_PACKAGE_xxx=y`（长期）
