#!/usr/bin/env bash
# luci-app-firewall (forwards.js 端口转发) 换皮
set -euo pipefail
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"

d=
for p in package/feeds/luci/luci-app-firewall feeds/luci/luci-app-firewall; do
  [ -f "$p/htdocs/luci-static/resources/view/firewall/forwards.js" ] && d=$p && break
done
[ -n "$d" ] || { echo "::error::找不到 luci-app-firewall"; exit 1; }

python3 "$script_dir/firewall-ui/apply-forwards.py" "$d/htdocs/luci-static/resources/view/firewall/forwards.js"
echo "luci-app-firewall forwards UI patch done ($d)"
