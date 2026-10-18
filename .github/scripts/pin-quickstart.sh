#!/usr/bin/env bash
# 只把 QuickStart 首页铺进构建树，不拉 nas-packages / app-hub 整仓。
#
# 六个默认 feed 里没有 luci-app-quickstart。写成 seed 是死行（§九）。
# 官方带首页是因为商店运行时装了它；本 fork 要开箱首页，但 Samba/易有云/
# 下载器/OTA/Docker/ddnsto 仍然禁止加回。做法：只 clone 两个包，首页保留
# 磁盘信息 + 存储服务（模块里只留 WebDAV 卡片，易有云/Samba 从渲染删除
# 不留空位），下载/远程域名整块仍删掉；快捷入口「家长控制」未装 oaf
# 也显示（点进去再商店装 luci-app-oaf）。侧栏不要「网络存储」下的 RAID /
# S.M.A.R.T.，也不要 luci-mod-system 的「挂载点」（无数据盘；那个包还带着备份
# 与更新，只能 menu.d 关掉，不能从 seed 删）。Makefile 保留官方四项 DEPENDS
# （smartmontools/smartd/drivedb/mdadm）。旧构建树可能已经拆过 +smartd
# （跳过 clone），脚本先加回再检查。r32 对照 r28：拆掉 smartd 包后
# Disk.Status 一直不回来，更具体线索是缺 /etc/smartd.conf，尚不能认定
# 必须跑 smartd 后台（§三十五；r33 N100 已验证首页卡片正常）。首页磁盘信息等到
# Disk.Status；官方 !disks&&!raidList 会把空 RAID 列表当加载完（r31 空白），
# 补丁改成 disks==null 才转圈（§三十四）。侧栏 RAID/SMART 菜单仍删。
# auto_setup 允许 gowebdav，拦住 samba/linkease/下载器/Docker/ddnsto。
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
# 官方四项 DEPENDS。旧构建树可能已跳过 clone、Makefile 还停在拆掉 +smartd
# 的裁剪版：先加回，再检查。侧栏菜单另删。
python3 - "$qs/Makefile" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
official = "+smartmontools +smartd +smartmontools-drivedb +mdadm "
stripped = "+smartmontools +smartmontools-drivedb +mdadm "
if official not in s and stripped in s:
    s = s.replace(stripped, official, 1)
    p.write_text(s, encoding="utf-8")
    print("quickstart Makefile: 从旧裁剪加回 +smartd")
if official not in s:
    raise SystemExit("::error::quickstart Makefile 没有官方四项 DEPENDS（要有 smartd+smartctl+mdadm）")
print("quickstart Makefile: 官方四项 DEPENDS 都在（侧栏菜单另删）")
PY

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
python3 - "$ctrl" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
raid = '        entry({"admin", "nas", "raid"}, call("quickstart_index", {index={"admin", "nas"}}), _("RAID"), 10).leaf = true\n'
smart = '        entry({"admin", "nas", "smart"}, call("quickstart_index", {index={"admin", "nas"}}), _("S.M.A.R.T."), 11).leaf = true\n'
changed = False
for line in (raid, smart):
    if line in s:
        s = s.replace(line, "", 1)
        changed = True
if changed:
    p.write_text(s, encoding="utf-8")
    print("quickstart.lua: 去掉侧栏 RAID / S.M.A.R.T.（网络存储父菜单随子项消失）")
if 'admin", "nas", "raid"' in s or 'admin", "nas", "smart"' in s:
    raise SystemExit("::error::controller 还注册 RAID/SMART 菜单，拒绝继续")
if 'admin", "network_guide"' not in s:
    raise SystemExit("::error::删 RAID/SMART 时把网络向导弄丢了")
PY
# luci-mod-system 不能删（备份与更新在里面）。无数据盘，侧栏「挂载点」用 menu.d 关掉。
menu_dir=$luci/root/usr/share/luci/menu.d
mkdir -p "$menu_dir"
cat > "$menu_dir/drop-system-mounts.json" <<'EOF'
{
	"admin/system/mounts": {
		"enabled": false
	}
}
EOF
grep -q '"admin/system/mounts"' "$menu_dir/drop-system-mounts.json" || {
  echo "::error::没写出挂载点菜单覆盖"
  exit 1
}
echo "luci-app-quickstart menu.d: 侧栏关掉系统 → 挂载点"

js=$luci/htdocs/luci-static/quickstart/index.js
[ -f "$js" ] || {
  echo "::error::找不到 QuickStart 前端 $js"
  exit 1
}

python3 - "$js" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")

# 首页：磁盘信息 + 存储服务留下；docker/下载/远程域名从渲染删除（不是 hidden）。
orig_push = 'f.value.diskInfo&&R.push({key:"diskInfo",component:$g}),f.value.storage&&R.push({key:"storage",component:jf}),Qt("dockerd")&&f.value.docker&&R.push({key:"docker",component:Wv}),f.value.downloadService&&R.push({key:"downloadService",component:n1}),f.value.remoteDomain&&R.push({key:"remoteDomain",component:s5}),R'
old_push = 'f.value.diskInfo&&R.push({key:"diskInfo",component:$g}),R'
new_push = 'f.value.diskInfo&&R.push({key:"diskInfo",component:$g}),f.value.storage&&R.push({key:"storage",component:jf}),R'
if s.count(orig_push) == 1:
    s = s.replace(orig_push, new_push, 1)
    print("index.js: 首页保留 diskInfo + storage，去掉 docker / download / remoteDomain")
elif s.count(old_push) == 1 and "f.value.storage&&R.push" not in s:
    s = s.replace(old_push, new_push, 1)
    print("index.js: 从旧裁剪加回 storage 模块")
elif s.count(new_push) == 1 and "f.value.downloadService&&R.push" not in s:
    print("index.js 首页已是 diskInfo + storage")
else:
    raise SystemExit("::error::index.js 首页模块 push 对不上，前端改版了要人工复核")

# 默认开关留下 storage，去掉 docker/download/remoteDomain
for a, b in (
    (",storage:!0,docker:!0,downloadService:!0,remoteDomain:!0", ",storage:!0"),
    (",storage:!1,docker:!1,downloadService:!1,remoteDomain:!1", ",storage:!1"),
    ("diskInfo:!0,systemInfo:!0", "diskInfo:!0,storage:!0,systemInfo:!0"),
    ("diskInfo:!1,systemInfo:!1", "diskInfo:!1,storage:!1,systemInfo:!1"),
):
    if a in s:
        s = s.replace(a, b)
if "downloadService:!" in s or "remoteDomain:!" in s or ",docker:!" in s:
    raise SystemExit("::error::index.js 仍有下载/远程域名/Docker 开关，拒绝半成品补丁")
if "storage:!0" not in s:
    raise SystemExit("::error::index.js 没有 storage 默认开，首页会不显示存储服务")

storage_blob = '{key:"storage",title:n("\\u5B58\\u50A8\\u670D\\u52A1"),description:n("\\u5171\\u4EAB\\u4E0E\\u5B58\\u50A8\\u670D\\u52A1\\u6982\\u89C8")},'
disk_blob = '{key:"diskInfo",title:n("\\u78C1\\u76D8\\u4FE1\\u606F"),description:n("\\u78C1\\u76D8\\u4F7F\\u7528\\u60C5\\u51B5\\u4E0E\\u5BB9\\u91CF\\u6982\\u89C8")},'
for blob in (
    '{key:"downloadService",title:n("\\u4E0B\\u8F7D\\u670D\\u52A1"),description:n("\\u4E0B\\u8F7D\\u4EFB\\u52A1\\u4E0E\\u670D\\u52A1\\u72B6\\u6001")},',
    '{key:"remoteDomain",title:n("\\u8FDC\\u7A0B\\u57DF\\u540D"),description:n("\\u8FDC\\u7A0B\\u8BBF\\u95EE\\u57DF\\u540D\\u7BA1\\u7406")},',
):
    c = s.count(blob)
    if c > 1:
        raise SystemExit("::error::index.js 设置列表项重复，前端改版了要人工复核")
    if c == 1:
        s = s.replace(blob, "", 1)
if storage_blob not in s:
    if disk_blob not in s:
        raise SystemExit("::error::index.js 找不到磁盘信息设置项，无法加回存储服务")
    s = s.replace(disk_blob, disk_blob + storage_blob, 1)
    print("index.js: 设置列表加回 storage")
else:
    print("index.js 设置列表保留 storage")

cloud_item = 't("div",{class:lt(["item cloud",{active:m.value==0}]),onClick:F[1]||(F[1]=H=>y(0))},[Y(qp,{color:"#155dfc",class:"icon2"}),t("div",Mf,i(e(n)("\\u6613\\u6709\\u4E91")),1),(h=(w=l.value)==null?void 0:w.linkease)!=null&&h.enabel?(r(),s("span",Lf,i(e(n)("\\u5DF2\\u914D\\u7F6E")),1)):(r(),s("span",Of,i(e(n)("\\u672A\\u914D\\u7F6E")),1))],2),'
samba_item = 't("div",{class:lt(["item memory",{active:m.value==1}]),onClick:F[2]||(F[2]=H=>y(1))},[Y(eo,{color:"#0bab47",class:"icon2"}),Nf,t("span",null,i((x=(_=l.value)==null?void 0:_.sambas)!=null&&x.length?e(n)("\\u5DF2\\u542F\\u7528"):e(n)("\\u672A\\u542F\\u7528")),1)],2),'
samba_menu = 't("div",null,[t("a",Pf,i(e(n)("SAMBA\\u9AD8\\u7EA7\\u914D\\u7F6E")),1)]),'
webdav_item = 't("div",{class:lt(["item network",{active:m.value==2}]),onClick:F[3]||(F[3]=H=>y(2))},[Y(xe,{color:"#9810fa",class:"icon2"}),Vf,'
m_pick = 'm=E(0),v=E(!1),b=()=>{var w,h,_,x,C,S;if(v.value)return;const F=[Boolean((h=(w=l.value)==null?void 0:w.linkease)==null?void 0:h.enabel),Boolean((x=(_=l.value)==null?void 0:_.sambas)==null?void 0:x.length),Boolean((S=(C=l.value)==null?void 0:C.webdav)==null?void 0:S.path)].findIndex(Boolean);m.value=F===-1?0:F}'
m_webdav = 'm=E(2),v=E(!1),b=()=>{if(v.value)return;m.value=2}'
cfg_old = 'const k=()=>{Wa({setup:0})},g=()=>{a.value=!a.value},p=()=>{g(),zt.installAndGo("app-meta-gowebdav"'
cfg_new = 'const k=()=>{zt.installAndGo("app-meta-gowebdav","GoWebDAV","/cgi-bin/luci/admin/nas/gowebdav")},g=()=>{a.value=!a.value},p=()=>{g(),zt.installAndGo("app-meta-gowebdav"'

if s.count(cloud_item) == 1:
    s = s.replace(cloud_item, "", 1)
    print("index.js: 存储服务里去掉易有云卡片")
elif s.count(cloud_item) == 0 and webdav_item in s:
    print("index.js 存储服务已无易有云卡片")
else:
    raise SystemExit("::error::index.js 易有云卡片删不掉，前端改版了要人工复核")

if s.count(samba_item) == 1:
    s = s.replace(samba_item, "", 1)
    print("index.js: 存储服务里去掉 Samba 卡片")
elif s.count(samba_item) == 0 and webdav_item in s:
    print("index.js 存储服务已无 Samba 卡片")
else:
    raise SystemExit("::error::index.js Samba 卡片删不掉，前端改版了要人工复核")

if s.count(samba_menu) == 1:
    s = s.replace(samba_menu, "", 1)
    print("index.js: 去掉 SAMBA 高级配置")
elif s.count(samba_menu) == 0:
    print("index.js 已无 SAMBA 高级配置")
else:
    raise SystemExit("::error::index.js SAMBA 高级配置删不掉")

if s.count(m_pick) == 1:
    s = s.replace(m_pick, m_webdav, 1)
    print("index.js: 存储服务默认打开 WebDAV")
elif m_webdav in s:
    print("index.js 存储服务已默认 WebDAV")
else:
    raise SystemExit("::error::index.js 默认页签改不了，前端改版了要人工复核")

if s.count(cfg_old) == 1:
    s = s.replace(cfg_old, cfg_new, 1)
    print("index.js: 配置存储服务改走 GoWebDAV")
elif 'k=()=>{zt.installAndGo("app-meta-gowebdav"' in s:
    print("index.js 配置存储服务已走 GoWebDAV")
else:
    raise SystemExit("::error::index.js 配置存储服务入口改不了")

if new_push not in s or webdav_item not in s or storage_blob not in s:
    raise SystemExit("::error::首页存储服务/WebDAV 没有留下")
if cloud_item in s or samba_item in s or "f.value.downloadService&&R.push" in s:
    raise SystemExit("::error::易有云/Samba/下载服务还在首页")

# 官方前端：没装 luci-app-oaf 就不画「家长控制」。用户要这块入口，未安装也显示。
baby_hide = 'ot.icon!=="baby"||v.value?(r(),Z(E4,{key:0,card:ot,onClick:g},null,8,["card"])):D("",!0)'
baby_show = '(r(),Z(E4,{key:0,card:ot,onClick:g},null,8,["card"]))'
if s.count(baby_hide) == 1:
    s = s.replace(baby_hide, baby_show, 1)
    print("index.js: 家长控制未装 oaf 也显示")
elif 'ot.icon!=="baby"||v.value' not in s and '{icon:"baby"' in s:
    print("index.js 家长控制已始终显示")
else:
    raise SystemExit("::error::index.js 家长控制显示条件对不上，前端改版了要人工复核")
if '{icon:"baby"' not in s or "luci-app-oaf" not in s:
    raise SystemExit("::error::首页没有家长控制入口")

# 官方：!disks&&!raidList 才显示「正在获取」。raidList=[] 是 truthy，
# mdadm 把 /raid/list/ 很快返回空阵列时，Disk.Status 还没到就会空白。
load_old = "!e(l).disks&&!e(l).raidList"
load_new = "e(l).disks==null"
if s.count(load_old) == 1:
    s = s.replace(load_old, load_new, 1)
    print("index.js: 磁盘信息等到 Disk.Status 才结束 loading")
elif load_new in s and load_old not in s:
    print("index.js 磁盘信息已等 Disk.Status")
else:
    raise SystemExit("::error::index.js 磁盘信息 loading 条件对不上，前端改版了要人工复核")

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
old_case = "samba|samba4|linkease|aria2|transmission|qbittorrent|docker|dockerd|dpanel|ddnsto|unishare|gowebdav|webdav2"
new_case = "samba|samba4|linkease|aria2|transmission|qbittorrent|docker|dockerd|dpanel|ddnsto|unishare"
if old_case in s:
    s = s.replace(old_case, new_case, 1)
    p.write_text(s, encoding="utf-8")
    print("auto_setup.sh: 允许 gowebdav，仍拒绝 Samba/易有云/下载器/Docker/ddnsto")
    sys.exit(0)
if "trimmed firmware, not in this image" in s and new_case in s:
    print("auto_setup.sh 已有裁剪拦截（允许 gowebdav），跳过")
    sys.exit(0)
needle = "auto_setup_app() {\n    local pkg=$1\n    is-opkg install"
if needle not in s:
    raise SystemExit("::error::auto_setup.sh 找不到 auto_setup_app，脚本改版了要人工复核")
insert = """auto_setup_app() {
    local pkg=$1
    case "$pkg" in
        samba|samba4|linkease|aria2|transmission|qbittorrent|docker|dockerd|dpanel|ddnsto|unishare)
            echo "Refusing $pkg (trimmed firmware, not in this image)" >&2
            return 1
            ;;
    esac
    is-opkg install"""
p.write_text(s.replace(needle, insert, 1), encoding="utf-8")
print("auto_setup.sh: 拒绝从商店装回 Samba/易有云/下载器/Docker/ddnsto；允许 gowebdav")
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
