include $(TOPDIR)/rules.mk

LUCI_TITLE:=LuCI for iStoreOS health check notify
LUCI_DEPENDS:=+istoreos-ops +luci-compat
LUCI_PKGARCH:=all
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=Apache-2.0
PKG_MAINTAINER:=xcy960815 <xcy960815@users.noreply.github.com>

define Package/luci-app-istoreos-health/conffiles
/etc/config/istoreos-health
endef

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature
