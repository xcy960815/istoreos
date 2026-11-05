#!/usr/bin/env bash
# luci-mod-status syslog.js + dmesg.js 只换皮（§五十一）。
set -euo pipefail
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"
d=
for p in package/feeds/luci/luci-mod-status feeds/luci/modules/luci-mod-status feeds/luci/luci-mod-status; do
  [ -f "$p/htdocs/luci-static/resources/view/status/syslog.js" ] && d=$p && break
done
[ -n "$d" ] || { echo "::error::找不到 luci-mod-status"; exit 1; }
python3 "$script_dir/status-logs-ui/apply-syslog.py" "$d/htdocs/luci-static/resources/view/status/syslog.js"
python3 "$script_dir/status-logs-ui/apply-dmesg.py" "$d/htdocs/luci-static/resources/view/status/dmesg.js"
echo "luci-mod-status logs UI patch done ($d)"
