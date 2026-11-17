#!/usr/bin/env bash
# luci-app-ttyd term.js 换皮与新窗口入口（§六十三）
set -euo pipefail
script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"
d=
for p in package/feeds/luci/luci-app-ttyd feeds/luci/applications/luci-app-ttyd feeds/luci/luci-app-ttyd; do
  [ -f "$p/htdocs/luci-static/resources/view/ttyd/term.js" ] && d=$p && break
done
[ -n "$d" ] || { echo "::error::找不到 luci-app-ttyd"; exit 1; }
python3 "$script_dir/ttyd-ui/apply-ttyd.py" "$d/htdocs/luci-static/resources/view/ttyd/term.js"
echo "luci-app-ttyd UI patch done ($d)"
