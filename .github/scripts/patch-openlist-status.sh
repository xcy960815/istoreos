#!/usr/bin/env bash
# luci feed luci-app-openlist 设置页运行状态+打开 Web UI 局部换皮（§四十七）。
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
echo "openlist status UI patch done ($d)"
