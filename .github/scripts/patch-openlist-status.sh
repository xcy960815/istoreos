#!/usr/bin/env bash
# luci feed luci-app-openlist 设置页/日志页换皮 + GoWebDav 状态页皮肤投递（§四十七/§五十一）。
set -euo pipefail
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"
d=
for p in package/feeds/luci/luci-app-openlist feeds/luci/luci-app-openlist; do
  [ -f "$p/htdocs/luci-static/resources/view/openlist/config.js" ] && d=$p && break
done
[ -n "$d" ] || { echo "::error::找不到 luci-app-openlist"; exit 1; }
python3 "$script_dir/openlist-status/apply.py" "$d/htdocs/luci-static/resources/view/openlist/config.js"
python3 "$script_dir/openlist-status/apply-log.py" "$d/htdocs/luci-static/resources/view/openlist/log.js"

# Stage GoWebDav status template into rootfs so store-installed / restored luci-app-gowebdav gets skinned
install -d "$d/root/usr/share/istoreos-ui" "$d/root/etc/uci-defaults"
install -m 0644 "$script_dir/openlist-status/gowebdav_status.htm" "$d/root/usr/share/istoreos-ui/gowebdav_status.htm"
cat > "$d/root/etc/uci-defaults/99-istoreos-gowebdav-skin" <<'EOF'
#!/bin/sh
SRC="/usr/share/istoreos-ui/gowebdav_status.htm"
DST="/usr/lib/lua/luci/view/gowebdav/gowebdav_status.htm"
if [ -f "$SRC" ] && [ -f "$DST" ] && ! grep -q 'data-ui-skin="gowebdav"' "$DST" 2>/dev/null; then
	cp -a "$SRC" "$DST"
	rm -rf /tmp/luci-indexcache /tmp/luci-modulecache 2>/dev/null || true
fi
exit 0
EOF
chmod 0755 "$d/root/etc/uci-defaults/99-istoreos-gowebdav-skin"
echo "openlist & gowebdav UI patch done ($d)"
