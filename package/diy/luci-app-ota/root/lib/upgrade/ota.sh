# Trimmed-fork OTA: real logic is in /bin/ota (GitHub Releases).
# Keep export_ota_url for any leftover callers; do NOT point at koolcenter.
export_ota_url() {
	export -n OTA_URL_BASE="https://github.com/xcy960815/istoreos/releases"
	return 0
}
