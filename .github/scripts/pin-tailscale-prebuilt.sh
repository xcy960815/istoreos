#!/usr/bin/env bash
# 把 packages feed 里的 tailscale 从源码编译换成官方 amd64 预编译，并烘焙 LuCI。
#
# 为什么不从源码升到「最新」：istoreos-24.10 的 golang 是 1.23.12 且 GOTOOLCHAIN=local。
# Tailscale 1.80.3（feed 现版本）要 Go 1.23.1，能编；1.82+ 要 1.24，最新 1.104.1 要 1.27.1。
# 升 golang 会牵动所有 Go 包（含已钉死的 DDNS-Go v6.12.2），r8 已经为此炸过一次。
# 本 fork 只做 x86_64，官方 amd64 tgz 可直接装。升版本：改下面三个常量和 HASH。
#
# 必须在 feeds install 之后、make defconfig 之前跑（LuCI 符号这时才进 kconfig）。
# 改的是 feeds 生成的副本，不进 git，不算改源码。见 docs/CUSTOM-TRIMMING.md §二十二
#
# 耐久补丁（与线上路由器一致）：asvow helper 默认会建 netifd network.tailscale（static）
# 并用 firewall.tszone.network= 绑定，导致地址打架 / fw4 同名 zone 重定义。
# 本脚本在 clone 后覆盖 helper，并烘焙 ensure-helper-fix.sh + START=89 开机守护。
#  overlays 在 .github/scripts/tailscale-durable/（进 git）。
set -euo pipefail

TS_VERSION=1.104.1
TS_HASH=108d1d96ecf410d305571e173516f27038f870919a9b89c914a167c6d33a4528
LUCI_REPO=https://github.com/asvow/luci-app-tailscale.git
# 钉 commit 而不是 tag：tag 可被上游移动，内容会悄悄换掉。下面这个 commit 就是 v1.2.6。
LUCI_COMMIT=534eb3f3acba24dac4e6fee9fa33049b004ef121

root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"

DURABLE="$root/.github/scripts/tailscale-durable"
[ -f "$DURABLE/tailscale_helper" ] || {
  echo "::error::缺少 $DURABLE/tailscale_helper"
  exit 1
}
[ -f "$DURABLE/ensure-helper-fix.sh" ] || {
  echo "::error::缺少 $DURABLE/ensure-helper-fix.sh"
  exit 1
}
[ -f "$DURABLE/tailscale-fixup" ] || {
  echo "::error::缺少 $DURABLE/tailscale-fixup"
  exit 1
}
[ -f "$DURABLE/41_tailscale-durable" ] || {
  echo "::error::缺少 $DURABLE/41_tailscale-durable"
  exit 1
}
[ -f "$DURABLE/luci-app-tailscale.json" ] || {
  echo "::error::缺少 $DURABLE/luci-app-tailscale.json"
  exit 1
}
[ -f "$DURABLE/patch-luci-setting.sh" ] || {
  echo "::error::缺少 $DURABLE/patch-luci-setting.sh"
  exit 1
}

grep -qx 'CONFIG_TARGET_x86_64=y' config-custom.seed || {
  echo "::error::官方 Tailscale 预编译是 amd64，seed 不是 x86_64，拒绝替换"
  exit 1
}

m=
for p in package/feeds/packages/tailscale/Makefile package/feeds/packages/net/tailscale/Makefile; do
  [ -f "$p" ] && m=$p && break
done
[ -n "$m" ] || {
  echo "::error::找不到 feeds 里的 tailscale Makefile，feeds install 了吗？"
  exit 1
}
d=$(dirname "$m")
[ -f "$d/files/tailscale.init" ] || {
  echo "::error::$d/files/tailscale.init 不存在，feed 布局变了"
  exit 1
}

# 覆盖 Makefile：不再依赖 golang/host，解压官方 tgz 后把两个二进制装进 /usr/sbin
cat > "$m" <<EOF
include \$(TOPDIR)/rules.mk

PKG_NAME:=tailscale
PKG_VERSION:=${TS_VERSION}
PKG_RELEASE:=1

PKG_SOURCE:=tailscale_\$(PKG_VERSION)_amd64.tgz
PKG_SOURCE_URL:=https://pkgs.tailscale.com/stable/
PKG_HASH:=${TS_HASH}

PKG_LICENSE:=BSD-3-Clause
PKG_CPE_ID:=cpe:/a:tailscale:tailscale
PKG_BUILD_DIR:=\$(BUILD_DIR)/tailscale_\$(PKG_VERSION)_amd64

include \$(INCLUDE_DIR)/package.mk

define Package/tailscale
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=VPN
  TITLE:=Zero config VPN
  URL:=https://tailscale.com
  DEPENDS:=+ca-bundle +kmod-tun
  PROVIDES:=tailscaled
endef

define Package/tailscale/description
  Official amd64 build ${TS_VERSION} (prebuilt). iStoreOS 24.10 golang is
  1.23.12 and cannot compile Tailscale >= 1.82 from source.
endef

define Build/Compile
endef

define Package/tailscale/install
	\$(INSTALL_DIR) \$(1)/usr/sbin
	\$(INSTALL_BIN) \$(PKG_BUILD_DIR)/tailscaled \$(1)/usr/sbin/
	\$(INSTALL_BIN) \$(PKG_BUILD_DIR)/tailscale \$(1)/usr/sbin/
endef

\$(eval \$(call BuildPackage,tailscale))
EOF

# init/config 由 luci-app-tailscale 提供，这里只换二进制，避免两个包抢 /etc/init.d/tailscale
grep -q "PKG_VERSION:=${TS_VERSION}" "$m" && grep -q 'tailscale_$(PKG_VERSION)_amd64.tgz' "$m" || {
  echo "::error::tailscale Makefile 写入后校验失败"
  exit 1
}

luci=package/luci-app-tailscale
if [ -f "$luci/Makefile" ]; then
  echo "luci-app-tailscale 已在 $luci，跳过 clone"
else
  git init -q "$luci"
  git -C "$luci" remote add origin "$LUCI_REPO"
  git -C "$luci" fetch -q --depth 1 origin "$LUCI_COMMIT"
  git -C "$luci" checkout -q --detach FETCH_HEAD
fi
grep -q 'LUCI_TITLE:=LuCI for Tailscale' "$luci/Makefile" || {
  echo "::error::$luci 不是 asvow/luci-app-tailscale，拒绝继续"
  exit 1
}
grep -q '^PKG_VERSION:=1\.2\.6$' "$luci/Makefile" || {
  echo "::error::$luci PKG_VERSION 不是 1.2.6，上游布局/版本变了要人工复核"
  exit 1
}
got=$(git -C "$luci" rev-parse HEAD 2>/dev/null || true)
if [ -n "$got" ]; then
  [ "$got" = "$LUCI_COMMIT" ] || {
    echo "::error::$luci 的 HEAD=$got，与钉死的 $LUCI_COMMIT 不符"
    exit 1
  }
else
  echo "::warning::$luci 没有 .git（本地构建树），无法核对 commit；只校验了版本 1.2.6"
fi
[ -f "$luci/root/usr/sbin/tailscale_helper" ] || {
  echo "::error::$luci 缺少 root/usr/sbin/tailscale_helper，上游布局变了"
  exit 1
}

# --- durable overlay（每次跑都覆盖，旧构建树跳过 clone 也要打补丁）---
install -d "$luci/root/usr/sbin"
install -d "$luci/root/etc/tailscale"
install -d "$luci/root/etc/init.d"
install -d "$luci/root/etc/uci-defaults"
install -m 0755 "$DURABLE/tailscale_helper" "$luci/root/usr/sbin/tailscale_helper"
install -m 0755 "$DURABLE/tailscale_helper" "$luci/root/etc/tailscale/tailscale_helper.keep"
install -m 0755 "$DURABLE/ensure-helper-fix.sh" "$luci/root/etc/tailscale/ensure-helper-fix.sh"
install -m 0755 "$DURABLE/tailscale-fixup" "$luci/root/etc/init.d/tailscale-fixup"
install -m 0755 "$DURABLE/41_tailscale-durable" "$luci/root/etc/uci-defaults/41_tailscale-durable"
install -d "$luci/root/usr/share/luci/menu.d"
install -m 0644 "$DURABLE/luci-app-tailscale.json" "$luci/root/usr/share/luci/menu.d/luci-app-tailscale.json"

# LuCI: authkey spelling + 「授权登录」 button (every run, even when clone skipped)
bash "$DURABLE/patch-luci-setting.sh" "$luci"


grep -qF 'netifd skip: Tailscale owns addrs' "$luci/root/usr/sbin/tailscale_helper" || {
  echo "::error::durable helper 缺少 netifd skip 标记"
  exit 1
}
grep -qF 'NeedsLogin: keep tailscaled for AuthURL' "$luci/root/usr/sbin/tailscale_helper" || {
  echo "::error::durable helper 缺少 NeedsLogin/AuthURL 保活标记"
  exit 1
}
# Must not stop-on-no-IP blindly (old bug: kills AuthURL → LuCI 「未运行」)
if grep -q 'Failed to get Tailscale IPv4 address after 5 attempts' "$luci/root/usr/sbin/tailscale_helper"; then
  echo "::error::durable helper 仍含旧的 stop-on-no-IP 文案"
  exit 1
fi
grep -q "form.Value, 'authkey'" "$luci/htdocs/luci-static/resources/view/tailscale/setting.js" || {
  echo "::error::setting.js 未改成 authkey"
  exit 1
}
grep -q "add_list firewall.tszone.device='tailscale0'" "$luci/root/usr/sbin/tailscale_helper" || {
  echo "::error::durable helper 未绑定 device=tailscale0"
  exit 1
}
grep -q "set network.tailscale.proto='static'" "$luci/root/usr/sbin/tailscale_helper" && {
  echo "::error::durable helper 仍含 proto=static（应已禁用）"
  exit 1
}
grep -q "set firewall.tszone.network='tailscale'" "$luci/root/usr/sbin/tailscale_helper" && {
  echo "::error::durable helper 仍含 network=tailscale（应改 device）"
  exit 1
}
[ -f "$luci/root/etc/tailscale/ensure-helper-fix.sh" ] || {
  echo "::error::未装上 ensure-helper-fix.sh"
  exit 1
}
grep -q 'admin/services/tailscale' "$luci/root/usr/share/luci/menu.d/luci-app-tailscale.json" || {
  echo "::error::menu.d 未改到 admin/services/tailscale"
  exit 1
}
grep -q 'admin/vpn/tailscale' "$luci/root/usr/share/luci/menu.d/luci-app-tailscale.json" && {
  echo "::error::menu.d 仍含 admin/vpn/tailscale"
  exit 1
}

echo "tailscale -> official ${TS_VERSION} amd64; luci-app-tailscale ${LUCI_TAG} at $luci (+ durable helper/NeedsLogin + authkey + Services menu)"
