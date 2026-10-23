# Trimmed-fork OTA: real logic is in /bin/ota (GitHub Releases via luci-app-ota).
# Owned by base-files so luci-app-ota does not clash on /lib/upgrade/ota.sh.
# Do NOT point at koolcenter.
export_ota_url() {
	export -n OTA_URL_BASE="https://github.com/xcy960815/istoreos/releases"
	return 0
}
