#!/usr/bin/env bash
# 只把 QuickStart 首页铺进构建树，不拉 nas-packages / app-hub 整仓。
#
# 六个默认 feed 里没有 luci-app-quickstart。写成 seed 是死行（§九）。
# 官方带首页是因为商店运行时装了它；本 fork 要开箱首页，但 Samba/易有云/
# 下载器/OTA/Docker/ddnsto 仍然禁止加回。做法：只 clone 两个包，从首页
# 渲染里删掉存储/下载/远程域名整块（不是开关隐藏，免得留空位），并拦住
# auto_setup 从商店把它们装回来。
#
# 必须在 feeds install 之后、make defconfig 之前跑（LuCI 符号这时才进 kconfig）。
# clone 的副本不进 git，不算改源码。见 docs/CUSTOM-TRIMMING.md §二十三
set -euo pipefail

NAS_REPO=https://github.com/linkease/nas-packages.git
NAS_COMMIT=c82c458b61e531d85524099c6864b0641e7e866a
LUCI_REPO=https://github.com/linkease/nas-packages-luci.git
LUCI_COMMIT=7e5083e2ca4cfa4d31f312026f46e5213c5b03f5
QS_VERSION=0.13.0
LUCI_VERSION=0.12.10-r1

root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"

clone_sparse() {
  local repo=$1 commit=$2 sparse=$3 dest=$4
  local tmp
  tmp=$(mktemp -d)
  git clone --filter=blob:none --sparse --no-checkout "$repo" "$tmp"
  git -C "$tmp" sparse-checkout set "$sparse"
  git -C "$tmp" fetch --depth 1 origin "$commit"
  git -C "$tmp" checkout --detach FETCH_HEAD
  rm -rf "$dest"
  mkdir -p "$(dirname "$dest")"
  cp -a "$tmp/$sparse" "$dest"
  rm -rf "$tmp"
}

qs=package/quickstart
if [ -f "$qs/Makefile" ]; then
  echo "quickstart 已在 $qs，跳过 clone"
else
  clone_sparse "$NAS_REPO" "$NAS_COMMIT" network/services/quickstart "$qs"
fi
grep -q "^PKG_NAME:=quickstart$" "$qs/Makefile" || {
  echo "::error::$qs 不是 linkease nas-packages 的 quickstart，拒绝继续"
  exit 1
}
grep -q "^PKG_VERSION:=${QS_VERSION}$" "$qs/Makefile" || {
  echo "::error::$qs PKG_VERSION 不是钉死的 ${QS_VERSION}，上游改了要人工复核"
  exit 1
}

luci=package/luci-app-quickstart
if [ -f "$luci/Makefile" ]; then
  echo "luci-app-quickstart 已在 $luci，跳过 clone"
else
  clone_sparse "$LUCI_REPO" "$LUCI_COMMIT" luci/luci-app-quickstart "$luci"
fi
grep -q 'LUCI_TITLE:=LuCI support for quickstart' "$luci/Makefile" || {
  echo "::error::$luci 不是 luci-app-quickstart，拒绝继续"
  exit 1
}
grep -q "^PKG_VERSION:=${LUCI_VERSION}$" "$luci/Makefile" || {
  echo "::error::$luci PKG_VERSION 不是钉死的 ${LUCI_VERSION}，上游改了要人工复核"
  exit 1
}
# 侧栏「网络向导」是 luci-app-quickstart 自带的，不是首页卡片。删存储/下载模块时禁止动它。
ctrl=$luci/luasrc/controller/quickstart.lua
grep -q 'admin", "network_guide"' "$ctrl" || {
  echo "::error::$ctrl 没有 admin/network_guide，左侧「网络向导」会丢"
  exit 1
}
grep -q '_("NetworkGuide")' "$ctrl" || {
  echo "::error::$ctrl 没有 NetworkGuide 菜单标题"
  exit 1
}
grep -q 'msgstr "网络向导"' "$luci/po/zh-cn/quickstart.po" || {
  echo "::error::中文包没有「网络向导」，侧栏会显示英文"
  exit 1
}

js=$luci/htdocs/luci-static/quickstart/index.js
[ -f "$js" ] || {
  echo "::error::找不到 QuickStart 前端 $js"
  exit 1
}

python3 - "$js" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")

# 从首页格子里删掉整块，不是改成 hidden。剩下的磁盘信息按可见数量重新算宽度。
old_push = 'f.value.diskInfo&&R.push({key:"diskInfo",component:$g}),f.value.storage&&R.push({key:"storage",component:jf}),Qt("dockerd")&&f.value.docker&&R.push({key:"docker",component:Wv}),f.value.downloadService&&R.push({key:"downloadService",component:n1}),f.value.remoteDomain&&R.push({key:"remoteDomain",component:s5}),R'
new_push = 'f.value.diskInfo&&R.push({key:"diskInfo",component:$g}),R'
if s.count(old_push) == 1:
    s = s.replace(old_push, new_push, 1)
    print("index.js: 从首页渲染去掉 storage / docker / downloadService / remoteDomain")
elif s.count(new_push) == 1 and "f.value.storage&&R.push" not in s:
    print("index.js 首页渲染已去掉存储/下载/远程域名")
else:
    raise SystemExit("::error::index.js 首页模块 push 对不上，前端改版了要人工复核")

# 模块表里也不留这几项，避免「关掉但还占设置位」
for frag in (
    ",storage:!0,docker:!0,downloadService:!0,remoteDomain:!0",
    ",storage:!1,docker:!1,downloadService:!1,remoteDomain:!1",
):
    s = s.replace(frag, "")
if ",storage:!" in s or "downloadService:!" in s or "remoteDomain:!" in s:
    raise SystemExit("::error::index.js 仍有存储/下载/远程域名开关，拒绝半成品补丁")

blobs = (
    '{key:"storage",title:n("\\u5B58\\u50A8\\u670D\\u52A1"),description:n("\\u5171\\u4EAB\\u4E0E\\u5B58\\u50A8\\u670D\\u52A1\\u6982\\u89C8")},',
    '{key:"downloadService",title:n("\\u4E0B\\u8F7D\\u670D\\u52A1"),description:n("\\u4E0B\\u8F7D\\u4EFB\\u52A1\\u4E0E\\u670D\\u52A1\\u72B6\\u6001")},',
    '{key:"remoteDomain",title:n("\\u8FDC\\u7A0B\\u57DF\\u540D"),description:n("\\u8FDC\\u7A0B\\u8BBF\\u95EE\\u57DF\\u540D\\u7BA1\\u7406")},',
)
missing = [b for b in blobs if s.count(b) == 0]
present = [b for b in blobs if s.count(b) == 1]
wrong = [b for b in blobs if s.count(b) > 1]
if wrong:
    raise SystemExit("::error::index.js 设置列表项重复，前端改版了要人工复核")
if present and missing:
    raise SystemExit("::error::index.js 设置列表只删了一部分，拒绝半成品补丁")
if present:
    for blob in present:
        s = s.replace(blob, "", 1)
    print("index.js: 从设置列表删除 storage / downloadService / remoteDomain")
else:
    print("index.js 设置列表已去掉存储/下载/远程域名")
p.write_text(s, encoding="utf-8")
PY

setup=$luci/root/usr/libexec/quickstart/auto_setup.sh
[ -f "$setup" ] || {
  echo "::error::找不到 $setup"
  exit 1
}
python3 - "$setup" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
if "trimmed firmware, not in this image" in s:
    print("auto_setup.sh 已有裁剪拦截，跳过")
    sys.exit(0)
needle = "auto_setup_app() {\n    local pkg=$1\n    is-opkg install"
if needle not in s:
    raise SystemExit("::error::auto_setup.sh 找不到 auto_setup_app，脚本改版了要人工复核")
insert = """auto_setup_app() {
    local pkg=$1
    case "$pkg" in
        samba|samba4|linkease|aria2|transmission|qbittorrent|docker|dockerd|dpanel|ddnsto|unishare|gowebdav|webdav2)
            echo "Refusing $pkg (trimmed firmware, not in this image)" >&2
            return 1
            ;;
    esac
    is-opkg install"""
p.write_text(s.replace(needle, insert, 1), encoding="utf-8")
print("auto_setup.sh: 拒绝从商店装回 Samba/易有云/下载器/Docker/ddnsto")
PY

cfg=$qs/files/quickstart.config
[ -f "$cfg" ] || {
  echo "::error::找不到 $cfg"
  exit 1
}
if grep -q "disable_update_check" "$cfg"; then
  echo "quickstart.config 已关更新检查，跳过"
else
  cat > "$cfg" <<'EOF'
config quickstart 'main'
	option disable_update_check '1'
EOF
  echo "quickstart.config: disable_update_check=1（没有 luci-app-ota）"
fi

echo "quickstart ${QS_VERSION} @ ${NAS_COMMIT:0:12}; luci-app-quickstart ${LUCI_VERSION} @ ${LUCI_COMMIT:0:12}"
