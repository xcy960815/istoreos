#!/bin/sh
# Apply only to the reviewed store template; never replace an unknown newer UI.
# Optional root prefix is for isolated local verification.
root=${1:-}
src="$root/usr/share/istoreos-ui/fastnet_status.htm"
dst="$root/usr/lib/lua/luci/view/fastnet/status.htm"
marker='data-ui-skin="fastnet-v1"'

[ -f "$src" ] && [ -f "$dst" ] || exit 0
grep -qF "$marker" "$src" || { echo "FastNet skin source marker missing" >&2; exit 1; }
grep -qF "$marker" "$dst" && exit 0

# istoreos-app-hub and nas-packages-luci ship the same 666-byte status.htm.
fingerprint=$(sha256sum "$dst") || exit 1
case "${fingerprint%% *}" in
	7bf774f85167f5eb9b19662baabbbaa1a4ebb0d65f361578e3579a417736dab6) ;;
	*) echo "FastNet skin skipped: unrecognized status.htm; review store update first" >&2; exit 0 ;;
esac

cp "$src" "$dst" || exit 1
rm -rf "$root/tmp/luci-indexcache" "$root/tmp/luci-modulecache"
echo "applied FastNet status skin"
