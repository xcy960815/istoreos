#!/usr/bin/env bash
# ddnsgo feed luci-app-ddns-go 设置页与日志页换皮（§五十一）。
set -euo pipefail
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"
d=
for p in package/feeds/ddnsgo/luci-app-ddns-go feeds/ddnsgo/luci-app-ddns-go; do
  [ -f "$p/htdocs/luci-static/resources/view/ddns-go/config.js" ] && d=$p && break
done
[ -n "$d" ] || { echo "::error::找不到 luci-app-ddns-go"; exit 1; }
python3 "$script_dir/ddnsgo-ui/apply-config.py" "$d/htdocs/luci-static/resources/view/ddns-go/config.js"
python3 "$script_dir/ddnsgo-ui/apply-log.py" "$d/htdocs/luci-static/resources/view/ddns-go/log.js"
echo "ddns-go UI patch done ($d)"
