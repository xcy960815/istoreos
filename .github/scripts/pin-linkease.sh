#!/usr/bin/env bash
# Classic file manager only; no LinkEaseFull / NAS desktop. See §六十二.
set -euo pipefail
SOURCE_REPO=https://github.com/istoreos/istoreos-app-hub.git
SOURCE_COMMIT=56d1630cfc1d0391be2baa61758e6fdd7c78f422
script_dir=$(cd "$(dirname "$0")" && pwd)
root=${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}
cd "$root"
grep -qx 'CONFIG_TARGET_x86_64=y' config-custom.seed || { echo '::error::LinkEase integration is reviewed for x86_64 only'; exit 1; }
names=(linkease luci-app-linkease linkease-common-bin luci-lib-linkeasefile)
paths=(apps/linkease/linkease apps/linkease/luci-app-linkease apps/linkease-common-bin/linkease-common-bin apps/linkeasefile/luci-lib-linkeasefile)
for name in "${names[@]}"; do
  dst="package/$name"
  if [ -e "$dst" ]; then
    [ -f "$dst/.istoreos-linkease-source" ] && [ "$(cat "$dst/.istoreos-linkease-source")" = "$SOURCE_COMMIT" ] || {
      echo "::error::$dst already exists without the expected source marker"; exit 1;
    }
  fi
done
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git init -q "$tmp/source"
git -C "$tmp/source" remote add origin "$SOURCE_REPO"
git -C "$tmp/source" sparse-checkout set "${paths[@]}"
git -C "$tmp/source" fetch -q --depth 1 --filter=blob:none origin "$SOURCE_COMMIT"
git -C "$tmp/source" checkout -q --detach FETCH_HEAD
[ "$(git -C "$tmp/source" rev-parse HEAD)" = "$SOURCE_COMMIT" ]
mkdir -p "$tmp/stage"
for i in "${!names[@]}"; do cp -a "$tmp/source/${paths[$i]}" "$tmp/stage/${names[$i]}"; done
python3 - "$tmp/stage" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
hashes = {
    'linkease': '2beab45ffd519f19e7dce62bbb06a4ddf63919e2ed69b1f8b4333134efbab03c',
    'linkease-common-bin': '608806ab0b2983c3abb9c55783673d74533fd56783327354faa246192909a78c',
}
for name, checksum in hashes.items():
    path = root / name / 'Makefile'
    text = path.read_text()
    if 'PKG_SOURCE_DATE:=1.7.6\n' not in text or f'PKG_HASH:={checksum}\n' not in text or text.count('PKG_RELEASE:=1\n') != 1:
        raise SystemExit(f'::error::{name} version/hash/release changed')
    path.write_text(text.replace('PKG_RELEASE:=1\n', 'PKG_RELEASE:=2\n', 1))
for name in ('luci-app-linkease', 'luci-lib-linkeasefile'):
    path = root / name / 'Makefile'
    text = path.read_text()
    if text.count('PKG_VERSION:=2.1.70-r4\n') != 1:
        raise SystemExit(f'::error::{name} version changed')
    if name == 'luci-app-linkease':
        path.write_text(text.replace('PKG_VERSION:=2.1.70-r4\n', 'PKG_VERSION:=2.1.70-r5\n', 1))
# The original common package unconditionally opens WAN TCP/8897, even with
# allowPublic=0. Do not publish a file service merely by baking it into an image.
path = root / 'linkease-common-bin/files/linkease-fw.uci-default'
text = path.read_text()
if 'set firewall.linkease.dest_port="8897"' not in text or 'set firewall.linkease.src="wan"' not in text:
    raise SystemExit('::error::LinkEase firewall defaults changed; review first')
path.write_text('#!/bin/sh\n# No automatic WAN rule; preserve existing user firewall configuration.\nexit 0\n')
config = (root / 'linkease/files/linkease.config').read_text()
if "option enabled '1'" not in config or "option allowPublic '0'" not in config:
    raise SystemExit('::error::LinkEase activation/public defaults changed')
translations = {
    'LinkEase Full is enabled. Please disable LinkEase Full before starting LinkEase.': 'LinkEase Full 已启用，请先停用后再启动易有云。',
}
for path in (root / 'luci-app-linkease/po').glob('*/linkease.po'):
    if path.parent.name in ('zh-cn', 'zh_Hans'):
        text = path.read_text()
        for msgid, msgstr in translations.items():
            if f'msgid "{msgid}"' not in text:
                text += f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'
        path.write_text(text)
PY
install -m 0644 "$script_dir/openlist-status/linkease_status.htm" "$tmp/stage/luci-app-linkease/luasrc/view/linkease_status.htm"
for name in linkease linkease-common-bin; do
  for file in "$tmp/stage/$name"/files/*.init "$tmp/stage/$name"/files/*.uci-default; do
    [ ! -f "$file" ] || sh -n "$file"
  done
done
mkdir -p package
for name in "${names[@]}"; do
  printf '%s\n' "$SOURCE_COMMIT" > "$tmp/stage/$name/.istoreos-linkease-source"
  rm -rf "package/$name"
  cp -a "$tmp/stage/$name" "package/$name"
done
echo "Classic LinkEase 1.7.6 + LuCI pinned at ${SOURCE_COMMIT:0:12}; no automatic WAN access"
