#!/usr/bin/env bash
# luci-light 硬依赖 luci-theme-bootstrap。seed 里删掉 =y 不够，defconfig 会加回来。
# 构建树里改成不依赖它（界面已经用 Argon，istoreos-files 会拉 luci-theme-argon）。
# 必须在 feeds install 之后、make defconfig 之前跑。见 docs/CUSTOM-TRIMMING.md §二十四
set -euo pipefail

root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"

m=
for p in \
  package/feeds/luci/collections/luci-light/Makefile \
  package/feeds/luci/luci-light/Makefile \
  feeds/luci/collections/luci-light/Makefile
do
  [ -f "$p" ] && m=$p && break
done
[ -n "$m" ] || {
  echo "::error::找不到 luci-light Makefile，feeds install 了吗？"
  exit 1
}

grep -q 'luci-theme-bootstrap' "$m" || {
  echo "luci-light 已不依赖 luci-theme-bootstrap，跳过 ($m)"
  exit 0
}

# 只删这一条依赖，别动别的 +luci-* 行
tmp=$(mktemp)
sed '/+luci-theme-bootstrap/d' "$m" > "$tmp"
mv "$tmp" "$m"

if grep -q 'luci-theme-bootstrap' "$m"; then
  echo "::error::$m 里还有 luci-theme-bootstrap，依赖写法变了要人工复核"
  exit 1
fi
grep -q 'luci-theme-argon\|luci-mod-admin-full\|uhttpd' "$m" || {
  echo "::error::$m 删完依赖后不像 luci-light 了，拒绝继续"
  exit 1
}

echo "luci-light ($m): 去掉 luci-theme-bootstrap 依赖，界面走 Argon"
