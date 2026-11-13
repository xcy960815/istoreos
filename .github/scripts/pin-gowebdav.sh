#!/usr/bin/env bash
# Built-in standalone WebDAV; preserve opt-in activation and adapt its old init to fw4.
set -euo pipefail
SOURCE_REPO=https://github.com/linkease/istore-packages.git
SOURCE_COMMIT=dc60ee0b25f01dbc0a072f4a5ed1a944f7c3c053
script_dir=$(cd "$(dirname "$0")" && pwd)
root=${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}
cd "$root"
grep -qx 'CONFIG_TARGET_x86_64=y' config-custom.seed || { echo '::error::GoWebDav integration is reviewed for x86_64 only'; exit 1; }
grep -qxF '# CONFIG_GOWEBDAV_COMPRESS_UPX is not set' config-custom.seed || { echo '::error::GoWebDav UPX must stay disabled unless its host dependency is reviewed'; exit 1; }
for name in gowebdav luci-app-gowebdav; do
  dst="package/$name"
  if [ -e "$dst" ]; then
    [ -f "$dst/.istoreos-gowebdav-source" ] && [ "$(cat "$dst/.istoreos-gowebdav-source")" = "$SOURCE_COMMIT" ] || {
      echo "::error::$dst already exists without the expected source marker"; exit 1;
    }
  fi
done
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git init -q "$tmp/source"
git -C "$tmp/source" remote add origin "$SOURCE_REPO"
git -C "$tmp/source" sparse-checkout set gowebdav luci-app-gowebdav
git -C "$tmp/source" fetch -q --depth 1 --filter=blob:none origin "$SOURCE_COMMIT"
git -C "$tmp/source" checkout -q --detach FETCH_HEAD
[ "$(git -C "$tmp/source" rev-parse HEAD)" = "$SOURCE_COMMIT" ]
grep -qxF 'PKG_VERSION:=0.0.3' "$tmp/source/gowebdav/Makefile"
grep -qxF 'PKG_HASH:=1e75071216baa5b26aa111771ad87e865a5aacacf7abb8f0e5a2b7b8cb7fd8b3' "$tmp/source/gowebdav/Makefile"
grep -qxF 'PKG_VERSION:=1.0' "$tmp/source/luci-app-gowebdav/Makefile"
grep -q "option enable '0'" "$tmp/source/gowebdav/files/gowebdav.config"
grep -q "option allow_wan '0'" "$tmp/source/gowebdav/files/gowebdav.config"
python3 - "$tmp/source" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
path = root / 'gowebdav/Makefile'
text = path.read_text()
if text.count('PKG_RELEASE:=2\n') != 1:
    raise SystemExit('::error::GoWebDav package release anchor changed')
text = text.replace('PKG_RELEASE:=2\n', 'PKG_RELEASE:=3\n', 1)
anchor = '$(eval $(call GoBinPackage,gowebdav))'
if text.count(anchor) != 1:
    raise SystemExit('::error::GoWebDav package anchor changed')
text = text.replace(anchor, 'define Package/gowebdav/conffiles\n/etc/config/gowebdav\nendef\n\n' + anchor, 1)
path.write_text(text)
path = root / 'luci-app-gowebdav/Makefile'
text = path.read_text()
if text.count('PKG_RELEASE:=1\n') != 1:
    raise SystemExit('::error::GoWebDav LuCI package release anchor changed')
path.write_text(text.replace('PKG_RELEASE:=1\n', 'PKG_RELEASE:=2\n', 1))
translations = {'Status': '状态', 'RUNNING': '运行中', 'NOT RUNNING': '未运行', 'Collecting data...': '正在收集数据…'}
for path in (root / 'luci-app-gowebdav/po').glob('*/gowebdav.po'):
    if path.parent.name not in ('zh-cn', 'zh_Hans'):
        continue
    text = path.read_text()
    for msgid, msgstr in translations.items():
        if f'msgid "{msgid}"' not in text:
            text += f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'
    path.write_text(text)

# Move the app and status endpoint together; do not register a NAS parent menu.
path = root / 'luci-app-gowebdav/luasrc/controller/gowebdav.lua'
text = path.read_text()
parent = '\tentry({"admin", "nas"}, firstchild(), _("NAS") , 45).dependent = false\n'
if text.count(parent) != 1 or text.count('{"admin", "nas", "gowebdav"}') != 1 or text.count('{"admin","nas","gowebdav","status"}') != 1:
    raise SystemExit('::error::GoWebDav menu/status route anchors changed')
text = text.replace(parent, '', 1).replace('{"admin", "nas", "gowebdav"}', '{"admin", "services", "gowebdav"}').replace('{"admin","nas","gowebdav","status"}', '{"admin","services","gowebdav","status"}')
path.write_text(text)
PY
install -m 0755 "$script_dir/gowebdav-durable/gowebdav.init" "$tmp/source/gowebdav/files/gowebdav.init"
install -m 0644 "$script_dir/openlist-status/gowebdav_status.htm" "$tmp/source/luci-app-gowebdav/luasrc/view/gowebdav/gowebdav_status.htm"
# Replace obsolete fw3 include registration with ucitrack only. The init owns fw4 rules.
cat > "$tmp/source/luci-app-gowebdav/root/etc/uci-defaults/gowebdav" <<'EOF'
#!/bin/sh
uci -q batch <<-EOF_UCI >/dev/null
	delete ucitrack.@gowebdav[-1]
	add ucitrack gowebdav
	set ucitrack.@gowebdav[-1].init=gowebdav
	commit ucitrack
EOF_UCI
/etc/init.d/gowebdav enable
rm -f /tmp/luci-indexcache
exit 0
EOF
sh -n "$tmp/source/gowebdav/files/gowebdav.init"
sh -n "$tmp/source/luci-app-gowebdav/root/etc/uci-defaults/gowebdav"
mkdir -p package
for name in gowebdav luci-app-gowebdav; do
  printf '%s\n' "$SOURCE_COMMIT" > "$tmp/source/$name/.istoreos-gowebdav-source"
  rm -rf "package/$name"
  cp -a "$tmp/source/$name" "package/$name"
done
echo "GoWebDav 0.0.3 + LuCI pinned at ${SOURCE_COMMIT:0:12}; disabled until configured; fw4 compatible"
