#!/usr/bin/env bash
# luci-mod-system (reboot.js / flash.js / crontab.js / startup.js) + luci-mod-network (diagnostics.js) 换皮（§四十七/§五十一）
set -euo pipefail
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"
d=
for p in package/feeds/luci/luci-mod-system feeds/luci/luci-mod-system; do
  [ -f "$p/htdocs/luci-static/resources/view/system/reboot.js" ] && d=$p && break
done
[ -n "$d" ] || { echo "::error::找不到 luci-mod-system"; exit 1; }
python3 "$script_dir/luci-mod-system-ui/apply-reboot.py" "$d/htdocs/luci-static/resources/view/system/reboot.js"
python3 "$script_dir/luci-mod-system-ui/apply-flash.py" "$d/htdocs/luci-static/resources/view/system/flash.js"
python3 "$script_dir/luci-mod-system-ui/apply-crontab.py" "$d/htdocs/luci-static/resources/view/system/crontab.js"
python3 "$script_dir/luci-mod-system-ui/apply-startup.py" "$d/htdocs/luci-static/resources/view/system/startup.js"

net_d=
for p in package/feeds/luci/luci-mod-network feeds/luci/luci-mod-network; do
  [ -f "$p/htdocs/luci-static/resources/view/network/diagnostics.js" ] && net_d=$p && break
done
[ -n "$net_d" ] || { echo "::error::找不到 luci-mod-network"; exit 1; }
python3 "$script_dir/luci-mod-system-ui/apply-diagnostics.py" "$net_d/htdocs/luci-static/resources/view/network/diagnostics.js"
echo "luci-mod-system & diagnostics UI patch done ($d, $net_d)"
