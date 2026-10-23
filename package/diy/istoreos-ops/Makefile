include $(TOPDIR)/rules.mk

PKG_NAME:=istoreos-ops
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=Apache-2.0
PKG_MAINTAINER:=xcy960815 <xcy960815@users.noreply.github.com>

include $(INCLUDE_DIR)/package.mk

define Package/istoreos-ops
  SECTION:=utils
  CATEGORY:=Base system
  TITLE:=iStoreOS pre-OTA backup + health check
  DEPENDS:=+jsonfilter
  PKGARCH:=all
endef

define Package/istoreos-ops/description
  Curated config backup before OTA flash (openclash/tailscale/network/…)
  and daily-capable health checks (Tailscale, fw4, durable helper, DNS poison).
endef

define Build/Configure
endef

define Build/Compile
endef

define Package/istoreos-ops/install
	$(INSTALL_DIR) $(1)/usr/sbin $(1)/etc/uci-defaults
	$(INSTALL_BIN) ./files/istoreos-bak $(1)/usr/sbin/istoreos-bak
	$(INSTALL_BIN) ./files/istoreos-health $(1)/usr/sbin/istoreos-health
	$(INSTALL_DATA) ./files/99-istoreos-ops $(1)/etc/uci-defaults/99-istoreos-ops
endef

$(eval $(call BuildPackage,istoreos-ops))
