#!/usr/bin/env bash
# FastNet defaults: import only four reviewed packages, never the full app-hub.
# Run after feeds install and before defconfig. See CUSTOM-TRIMMING §六十一.
set -euo pipefail

SOURCE_REPO=https://github.com/istoreos/istoreos-app-hub.git
SOURCE_COMMIT=56d1630cfc1d0391be2baa61758e6fdd7c78f422
script_dir=$(cd "$(dirname "$0")" && pwd)
root=${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}
cd "$root"
grep -qx 'CONFIG_TARGET_x86_64=y' config-custom.seed || {
  echo "::error::FastNet prebuilt integration is reviewed for x86_64 only"; exit 1;
}

names=(fastnet luci-app-fastnet linkease-app-entry luci-lib-linkeaseauth)
paths=(apps/fastnet/fastnet apps/fastnet/luci-app-fastnet
       apps/linkeasefull/linkease-app-entry apps/linkeasefull/luci-lib-linkeaseauth)
versions=(0.8.9 0.8.9-r2 3.0.23 1.2.1-r3)
for name in "${names[@]}"; do
  dst="package/$name"
  if [ -e "$dst" ]; then
    [ -f "$dst/.istoreos-fastnet-source" ] &&
      [ "$(cat "$dst/.istoreos-fastnet-source")" = "$SOURCE_COMMIT" ] || {
        echo "::error::$dst already exists without the expected source marker; refusing to overwrite"; exit 1;
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
for i in "${!names[@]}"; do
  name=${names[$i]}
  src="$tmp/source/${paths[$i]}"
  grep -qxF "PKG_VERSION:=${versions[$i]}" "$src/Makefile" || {
    echo "::error::$name package version differs from reviewed source"; exit 1;
  }
  cp -a "$src" "$tmp/stage/$name"
  printf '%s\n' "$SOURCE_COMMIT" > "$tmp/stage/$name/.istoreos-fastnet-source"
done

python3 - "$tmp/stage" <<'PY'
from pathlib import Path
import sys

stage = Path(sys.argv[1])
expected = {
    'fastnet': '14214f92b0564df5d930ebcff8b10cc62c0cdaa83ff17fd7984ddd81dfd2a18d',
    'linkease-app-entry': 'f5a974187ca1c50f043459150e52195c85799673f9ebc18221e9f5d206a4fb3c',
}
for name, checksum in expected.items():
    if f'PKG_HASH:={checksum}' not in (stage / name / 'Makefile').read_text():
        raise SystemExit(f'::error::{name} prebuilt hash differs from reviewed source')

# The stock package opens WAN TCP/3200 on first boot. Including a network test
# tool must not implicitly publish it. Keep existing user firewall rules intact.
path = stage / 'fastnet/files/fastnet.uci-default'
text = path.read_text()
wan = '''\tdelete firewall.fastnet
\tset firewall.fastnet=rule
\tset firewall.fastnet.name="fastnet"
\tset firewall.fastnet.target="ACCEPT"
\tset firewall.fastnet.src="wan"
\tset firewall.fastnet.proto="tcp"
\tset firewall.fastnet.dest_port="3200"
\tcommit firewall
'''
if text.count(wan) != 1:
    raise SystemExit('::error::FastNet WAN rule anchor changed; review defaults first')
text = text.replace(wan, '', 1)
if 'firewall.' in text:
    raise SystemExit('::error::unexpected firewall changes remain in FastNet defaults')
path.write_text(text)

# Package revisions distinguish these defaults / UI from the unmodified store build.
path = stage / 'fastnet/Makefile'
text = path.read_text()
if text.count('PKG_RELEASE:=2\n') != 1:
    raise SystemExit('::error::FastNet package release anchor changed')
path.write_text(text.replace('PKG_RELEASE:=2\n', 'PKG_RELEASE:=3\n', 1))
path = stage / 'luci-app-fastnet/Makefile'
text = path.read_text()
path.write_text(text.replace('PKG_VERSION:=0.8.9-r2\n', 'PKG_VERSION:=0.8.9-r3\n', 1))

# The shared entry is a loopback /apps gateway, not the LinkEase NAS daemon.
entry_config = (stage / 'linkease-app-entry/files/linkease-app-entry.config').read_text()
if "option listen '127.0.0.1:19290'" not in entry_config:
    raise SystemExit('::error::application entry no longer listens on loopback')
for makefile in stage.glob('*/Makefile'):
    for line in makefile.read_text().splitlines():
        if 'DEPENDS:=' in line and any('+' + p in line.split() for p in ('linkease', 'linkeasefull', 'luci-app-linkease')):
            raise SystemExit('::error::FastNet unexpectedly depends on the full LinkEase service')
PY

# Bake the reviewed status skin into the LuCI package; no first-boot copy needed.
stock="$tmp/stage/luci-app-fastnet/luasrc/view/fastnet/status.htm"
fingerprint=$(shasum -a 256 "$stock" 2>/dev/null || sha256sum "$stock")
[ "${fingerprint%% *}" = 7bf774f85167f5eb9b19662baabbbaa1a4ebb0d65f361578e3579a417736dab6 ] || {
  echo "::error::FastNet status template changed; review skin compatibility first"; exit 1;
}
install -m 0644 "$script_dir/openlist-status/fastnet_status.htm" "$stock"
for path in "$tmp/stage/fastnet/files/fastnet.init" "$tmp/stage/fastnet/files/fastnet.uci-default"; do
  sh -n "$path"
done

mkdir -p package
for name in "${names[@]}"; do
  rm -rf "package/$name"
  cp -a "$tmp/stage/$name" "package/$name"
done
echo "FastNet 0.8.9 + LuCI + lightweight entry pinned at ${SOURCE_COMMIT:0:12}; no automatic WAN rule"
