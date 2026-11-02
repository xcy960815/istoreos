#!/usr/bin/env bash
# 把 third feed 的 luci-app-vlmcsd 状态条换成 UI-STYLE 卡片皮（§四十六）：
#   ① 去掉 <font color=…> / fieldset 老皮
#   ② 保留 id=vlmcsd_status、XHR.poll(3, …/status)、running 分支逻辑
#   ③ 英文 msgid + zh-cn po 同步
# 必须在 feeds install 之后、make defconfig 之前跑。
# 改的是 feeds 生成的副本，不进 git（第 ⑥ 条构建例外，AGENTS.md 有清单）。
# 任何锚点对不上 = third feed 改了模板，报错人工复核，不许静默跳过。
set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
cd "$root"

src_dir="$script_dir/vlmcsd-status"
src_htm="$src_dir/vlmcsd_status.htm"
[ -f "$src_htm" ] || {
  echo "::error::缺少皮肤源文件 $src_htm"
  exit 1
}

d=
for p in package/feeds/third/luci-app-vlmcsd feeds/third/luci-app-vlmcsd; do
  [ -f "$p/luasrc/view/vlmcsd/vlmcsd_status.htm" ] && d=$p && break
done
[ -n "$d" ] || {
  echo "::error::找不到 luci-app-vlmcsd（feeds install 了吗？third feed 的包改名/换位置了？）"
  exit 1
}

dst_htm="$d/luasrc/view/vlmcsd/vlmcsd_status.htm"
dst_po="$d/po/zh-cn/vlmcsd.zh-cn.po"

python3 - "$src_htm" "$dst_htm" "$dst_po" "$src_dir/zh-cn-additions.po" <<'PYEOF'
import sys, pathlib, re

src_htm, dst_htm, dst_po, add_po = map(pathlib.Path, sys.argv[1:5])
new = src_htm.read_text(encoding="utf-8")
cur = dst_htm.read_text(encoding="utf-8")

if "#cbi-vlmcsd" in cur and 'id="vlmcsd_status"' in cur and "XHR.poll(3" in cur:
    print("SKIP  htm: already skinned under #cbi-vlmcsd")
elif 'id="vlmcsd_status"' in cur and "XHR.poll(3" in cur and "data.running" in cur:
    dst_htm.write_text(new, encoding="utf-8")
    print("OK    htm: replaced upstream vlmcsd_status.htm")
else:
    print("::error::htm 锚点对不上：预期含 id=vlmcsd_status / XHR.poll(3) / data.running（third feed 可能改了模板）", file=sys.stderr)
    sys.exit(1)

htm = dst_htm.read_text(encoding="utf-8")
for must in ("#cbi-vlmcsd", 'id="vlmcsd_status"', "XHR.poll(3", "data.running", "KMS is running", "KMS is not running"):
    if must not in htm:
        print(f"::error::终检失败：模板缺少 {must}", file=sys.stderr)
        sys.exit(1)
if re.search(r"<font\s+color=", htm, re.I):
    print("::error::终检失败：模板仍含 <font color=", file=sys.stderr)
    sys.exit(1)

if not dst_po.is_file():
    print(f"::error::找不到 {dst_po}", file=sys.stderr)
    sys.exit(1)

po = dst_po.read_text(encoding="utf-8")
add_text = add_po.read_text(encoding="utf-8")
ids = re.findall(r'msgid "(.*?)"\nmsgstr "(.*?)"', add_text, re.S)
changed = False
for mid, mstr in ids:
    if f'msgid "{mid}"' in po:
        print(f"SKIP  po: {mid}")
        continue
    po += f'\nmsgid "{mid}"\nmsgstr "{mstr}"\n'
    changed = True
    print(f"OK    po: add {mid}")
if changed:
    dst_po.write_text(po, encoding="utf-8")
else:
    print("SKIP  po: all msgids present")

needed = set(re.findall(r"<%:([^%]*)%>", htm))
po2 = dst_po.read_text(encoding="utf-8")
missing = [i for i in sorted(needed) if f'msgid "{i}"' not in po2]
if missing:
    print(f"::error::po 缺少 msgid: {missing}", file=sys.stderr)
    sys.exit(1)

print(f"vlmcsd status 样式补丁 OK ({dst_htm})")
PYEOF

echo "vlmcsd status UI patch done ($d)"
