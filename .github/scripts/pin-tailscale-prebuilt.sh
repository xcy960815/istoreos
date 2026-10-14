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
set -euo pipefail

TS_VERSION=1.104.1
TS_HASH=108d1d96ecf410d305571e173516f27038f870919a9b89c914a9a7c6d33a4528
LUCI_REPO=https://github.com/asvow/luci-app-tailscale.git
LUCI_TAG=v1.2.6

root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"

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

define Package/tailscale/conffiles
/etc/config/tailscale
/etc/tailscale/
endef

define Build/Compile
endef

define Package/tailscale/install
	\$(INSTALL_DIR) \$(1)/usr/sbin \$(1)/etc/init.d \$(1)/etc/config
	\$(INSTALL_BIN) \$(PKG_BUILD_DIR)/tailscaled \$(1)/usr/sbin/
	\$(INSTALL_BIN) \$(PKG_BUILD_DIR)/tailscale \$(1)/usr/sbin/
	\$(INSTALL_BIN) ./files/tailscale.init \$(1)/etc/init.d/tailscale
	\$(INSTALL_DATA) ./files/tailscale.conf \$(1)/etc/config/tailscale
endef

\$(eval \$(call BuildPackage,tailscale))
EOF

# 1.104.1 起关掉往 log.tailscale.com 打点（openwrt/packages master 同改）
cat > "$d/files/tailscale.init" <<'EOF'
#!/bin/sh /etc/rc.common

# Copyright 2020 Google LLC.
# Copyright (C) 2021 CZ.NIC z.s.p.o. (https://www.nic.cz/)
# SPDX-License-Identifier: Apache-2.0

USE_PROCD=1
START=80

export TS_NO_LOGS_NO_SUPPORT=true

start_service() {
  local state_file
  local port
  local std_err std_out

  config_load tailscale
  config_get_bool std_out "settings" log_stdout 1
  config_get_bool std_err "settings" log_stderr 1
  config_get port "settings" port 41641
  config_get state_file "settings" state_file /etc/tailscale/tailscaled.state
  config_get fw_mode "settings" fw_mode nftables

  /usr/sbin/tailscaled --cleanup

  procd_open_instance
  procd_set_param command /usr/sbin/tailscaled

  procd_set_param env TS_DEBUG_FIREWALL_MODE="$fw_mode"
  procd_append_param env TS_NO_LOGS_NO_SUPPORT=true

  procd_append_param command --port "$port"
  procd_append_param command --state "$state_file"

  procd_set_param respawn
  procd_set_param stdout "$std_out"
  procd_set_param stderr "$std_err"

  procd_close_instance
}

stop_service() {
  /usr/sbin/tailscaled --cleanup
}
EOF

grep -q "PKG_VERSION:=${TS_VERSION}" "$m" && grep -q 'tailscale_$(PKG_VERSION)_amd64.tgz' "$m" || {
  echo "::error::tailscale Makefile 写入后校验失败"
  exit 1
}

luci=package/luci-app-tailscale
if [ -f "$luci/Makefile" ]; then
  echo "luci-app-tailscale 已在 $luci，跳过 clone"
else
  git clone --depth 1 --branch "$LUCI_TAG" "$LUCI_REPO" "$luci"
fi
grep -q 'LUCI_TITLE:=LuCI for Tailscale' "$luci/Makefile" || {
  echo "::error::$luci 不是 asvow/luci-app-tailscale，拒绝继续"
  exit 1
}

echo "tailscale -> official ${TS_VERSION} amd64; luci-app-tailscale ${LUCI_TAG} at $luci"
