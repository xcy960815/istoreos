#!/usr/bin/env bash
# luci-mod-system reboot.js + flash.js 外层换皮（§四十七）
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
echo "luci-mod-system UI patch done ($d)"
