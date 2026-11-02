#!/usr/bin/env bash
# luci feed luci-app-wol 换皮（§四十七）
set -euo pipefail
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"
d=
for p in package/feeds/luci/luci-app-wol feeds/luci/luci-app-wol; do
  [ -f "$p/htdocs/luci-static/resources/view/wol.js" ] && d=$p && break
done
[ -n "$d" ] || { echo "::error::找不到 luci-app-wol"; exit 1; }
python3 "$script_dir/wol-ui/apply.py" "$d/htdocs/luci-static/resources/view/wol.js"
echo "wol UI patch done ($d)"
