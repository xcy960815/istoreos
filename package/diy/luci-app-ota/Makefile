
include $(TOPDIR)/rules.mk

LUCI_TITLE:=LuCI for OTA upgrade (GitHub Releases)
LUCI_DEPENDS:=+curl +jsonfilter
LUCI_PKGARCH:=all
PKG_VERSION:=2.0.0
PKG_RELEASE:=2
PKG_LICENSE:=Apache-2.0
PKG_MAINTAINER:=jjm2473 <jjm2473@gmail.com>

define Package/luci-app-ota/conffiles
/etc/config/ota
endef

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature
