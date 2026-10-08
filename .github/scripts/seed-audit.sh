#!/usr/bin/env bash
# 审计裁剪 seed 在 `make defconfig` 之后还剩多少没生效。
#
# 必须在 `./scripts/feeds install -a` 之后跑：此刻 feed 符号才存在，defconfig 才会
# 把它们的 =y 行保留下来。defconfig 对"符号不存在"的行是无警告删除，所以不区分就会
# 把"名字写错/包已消失"（死行）和"符号存在但依赖不满足"（真缺包）混成一团，
# 前者无害、后者要到 rootfs 装配才炸。分类依据是 tmp/.config-package.in 里的符号表。
#
# 两种情况硬失败：dnsmasq 非 full 变体复现（它和 dnsmasq-full 抢同一批文件）；出现下面已知清单之外的
# 未生效行——上游/feed 改名或依赖变化时 defconfig 会静默丢行，不拦的话 CI 照样绿、镜像悄悄少包。
set -euo pipefail

# 已知未生效、有意保留在 seed 里的行（内核内建符号没开，见 docs/CUSTOM-TRIMMING.md §九）。
# 往这里加项必须同时在该文档记账
known='PACKAGE_kmod-thermal
PACKAGE_kmod-xdp-sockets-diag'

for f in config-custom.seed tmp/.config-package.in .config; do
  [ -f "$f" ] || { echo "::error::缺少 $f，审计前提不成立（feeds install -a 与 make defconfig 都要先跑）"; exit 1; }
done

grep -oE '(menu)?config PACKAGE_[A-Za-z0-9_.+-]+' tmp/.config-package.in | sed 's/.*config //' | sort -u > ksyms.txt
grep -oE '^CONFIG_PACKAGE_[A-Za-z0-9_.+-]+=y' config-custom.seed | sed 's/^CONFIG_//; s/=y$//' | sort -u > want.txt
grep -oE '^CONFIG_PACKAGE_[A-Za-z0-9_.+-]+=[ym]' .config | sed 's/^CONFIG_//; s/=[ym]$//' | sort -u > on.txt
comm -23 want.txt on.txt > lost.txt
grep -Fxf ksyms.txt lost.txt > lost_hidden.txt || true
comm -23 lost.txt lost_hidden.txt > lost_dead.txt

{
  echo "feed 包符号总数: $(wc -l < ksyms.txt)  seed 想要: $(wc -l < want.txt)  defconfig 后开启: $(wc -l < on.txt)  丢失: $(wc -l < lost.txt)"
  echo "defconfig 自行加回(seed 没写却开启)的包:"; comm -13 want.txt on.txt
  echo; echo "== 符号不存在（seed 写的是 opkg 二元包名/改名/包已消失），这些行一直是死行 =="
  cat lost_dead.txt
  echo; echo "== 符号存在但没能开启（依赖不满足或被隐藏）——这些是真的缺包 =="
  cat lost_hidden.txt
} | tee seed-audit.txt

echo "::warning::seed 有 $(wc -l < lost.txt) 行未生效，详见 seed-audit.txt"

fail=0
if grep -q '^CONFIG_PACKAGE_dnsmasq=y$' .config; then
  echo "::error::dnsmasq(非 full)又被加回，会与 dnsmasq-full 抢文件；说明有保留包 select 了默认变体"
  fail=1
fi

new=$(grep -vxF "$known" lost.txt || true)
if [ -n "$new" ]; then
  { echo; echo "== 新增未生效（不在已知清单里）=="; echo "$new"; } | tee -a seed-audit.txt
  echo "::error::seed 有 $(echo "$new" | wc -l | tr -d ' ') 行新出现未生效，镜像会少包；名字改了就改 seed，确定不要就从 seed 删并记账"
  fail=1
fi
for k in $known; do
  grep -qxF "$k" lost.txt || echo "已知未生效项 $k 这次开成了，可以从 seed-audit.sh 的已知清单删掉"
done

exit "$fail"
