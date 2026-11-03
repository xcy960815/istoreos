#!/usr/bin/env bash
# 仅移除「状态 → 概况」的易有云重复入口，不改独立页面、服务或配置（§五十）。
set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"

template=
for candidate in \
  package/feeds/luci/luci-lua-runtime/luasrc/view/admin_status/luaindex.htm \
  feeds/luci/modules/luci-lua-runtime/luasrc/view/admin_status/luaindex.htm; do
  [ -f "$candidate" ] && template=$candidate && break
done
[ -n "$template" ] || { echo "::error::找不到概况页 Lua 模板加载器 luaindex.htm"; exit 1; }

python3 - "$template" <<'PY'
import sys
from pathlib import Path

file = Path(sys.argv[1])
text = file.read_text(encoding='utf-8')
old = 'if inc:match("%.htm$") then'
new = 'if inc ~= "linkease.htm" and inc:match("%.htm$") then'

if text.count(new) == 1 and old not in text:
    print(f'SKIP: overview already excludes linkease.htm ({file})')
elif text.count(old) == 1 and new not in text:
    file.write_text(text.replace(old, new, 1), encoding='utf-8')
    print(f'OK: overview excludes linkease.htm ({file})')
else:
    raise SystemExit('::error::概况页模板枚举锚点变化，需要人工复核，未修改文件')
PY
