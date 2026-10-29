#!/usr/bin/env bash
# Post-clone LuCI patches for asvow luci-app-tailscale (called by pin-tailscale-prebuilt.sh).
# 1) authKey → authkey (init/config option name)
# 2) NeedsLogin UI: clear button; zh_Hans 「授权登录」
set -euo pipefail

luci=${1:?luci-app-tailscale package dir}
SETTING_JS="$luci/htdocs/luci-static/resources/view/tailscale/setting.js"
[ -f "$SETTING_JS" ] || { echo "::error::缺少 $SETTING_JS"; exit 1; }

if grep -q "form.Value, 'authKey'" "$SETTING_JS"; then
  tmp=$(mktemp)
  sed "s/form.Value, 'authKey'/form.Value, 'authkey'/" "$SETTING_JS" > "$tmp"
  mv "$tmp" "$SETTING_JS"
fi
grep -q "form.Value, 'authkey'" "$SETTING_JS" || { echo "::error::setting.js authkey 补丁失败"; exit 1; }
if grep -q "form.Value, 'authKey'" "$SETTING_JS"; then
  echo "::error::setting.js 仍含 authKey"
  exit 1
fi

python3 - "$SETTING_JS" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
t = p.read_text()
old = (
    "\tif (loginStatus === \"NeedsLogin\") {\n"
    "\t\trenderHTML = String.format('<a href=\"%s\" target=\"_blank\">%s</a>', authURL, _('Need to log in'));\n"
    "\t} else if (loginStatus === \"Running\") {"
)
new = (
    "\tif (loginStatus === \"NeedsLogin\") {\n"
    "\t\tif (authURL) {\n"
    "\t\t\trenderHTML = String.format('<a class=\"cbi-button cbi-button-apply\" href=\"%s\" target=\"_blank\" rel=\"noopener noreferrer\">%s</a>', authURL, _('Need to log in'));\n"
    "\t\t} else {\n"
    "\t\t\trenderHTML = String.format('<span style=\"color:orange\">%s</span>', _('Need to log in'));\n"
    "\t\t}\n"
    "\t} else if (loginStatus === \"Running\") {"
)
if old not in t:
    if "cbi-button-apply" in t and "Need to log in" in t:
        print("setting.js NeedsLogin UI already patched")
    else:
        raise SystemExit("setting.js NeedsLogin block not found for UI patch")
else:
    p.write_text(t.replace(old, new, 1))
    print("setting.js NeedsLogin UI patched")
PY

PO_ZH="$luci/po/zh_Hans/tailscale.po"
if [ -f "$PO_ZH" ]; then
  python3 - "$PO_ZH" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
lines = p.read_text().splitlines(keepends=True)
out = []
i = 0
changed = False
while i < len(lines):
    out.append(lines[i])
    if lines[i].rstrip("\n") == 'msgid "Need to log in"':
        i += 1
        if i < len(lines) and lines[i].startswith("msgstr "):
            out.append('msgstr "授权登录"\n')
            changed = True
            i += 1
            continue
    i += 1
p.write_text("".join(out))
if not changed and 'msgstr "授权登录"' not in p.read_text():
    raise SystemExit("zh_Hans 授权登录 patch failed")
print("zh_Hans Need to log in → 授权登录")
PY
fi
