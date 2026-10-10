# CI 排障复盘（从 CUSTOM-TRIMMING.md 拆出，2026-10-10）

> 这里是历次构建失败的原始复盘：run 编号、耗时、日志原文、实测过程，**按原文保留，不再修改**。
> 节号与 [`CUSTOM-TRIMMING.md`](CUSTOM-TRIMMING.md) 一一对应，那边只留当前有效的结论。
> 文中引用的 §X 若本文件没有，指 CUSTOM-TRIMMING.md 的同号节。文中「已被推翻」「待定」等说法以写作当时为准，现状看 CUSTOM-TRIMMING.md。


## 七、CI 首次构建失败复盘（2026-10-05，run 37324148570）

失败点不在编译而在 **rootfs 装配**：`make[2]: *** [package/Makefile:99: package/install] Error 255`，
opkg 报 `Collected errors`。该 run 用的是**首轮 seed**（HEAD=eea07ec0f3，早于二次裁剪）；同日 15:28Z 另有一次
基于二次裁剪 seed（706d20bfe1）的 run，步骤顺序未修，会挂在同一处。两条互相独立的原因：

| # | 日志现象 | 根因 | 修法 |
|---|---|---|---|
| 1 | `cannot find dependency attr for base-files`、`curl for opkg`、`libgcrypt for ntfsprogs`、`luci-theme-argon for istoreos-files` | workflow 把 `make defconfig` 排在 `feeds update/install` **之前**。此刻 feed 符号尚不存在，kconfig `--defconfig` 把这些行**静默丢弃**（`CONFIG_LUCI_LANG_zh_Hans` 等信息类行同样被丢）。attr/curl/libgcrypt/luci-theme-argon 四个依赖全是 feed 包，核心树里没有；`base-files`(Makefile:45)、`opkg`(:41)、`package/diy/ntfsprogs`(:51)、`package/istoreos-files`(:20) 对它们的 `+xxx` 依赖在符号不可见时 select 落空 → 既没 `=y` 也没构建候选 | workflow 改为先装 feeds 再 `cp seed .config && make defconfig`；seed 头部"用法"行补上 feeds 步骤（原来漏写，正是它带偏了 CI） |
| 2 | `check_data_file_clashes: dnsmasq-full wants to install .../usr/sbin/dnsmasq`（等 10 个文件）`already provided by dnsmasq` | seed 只要 `dnsmasq-full`；`dnsmasq`(非 full) 是 **profile 默认包**——`include/target.mk:13` `DEVICE_TYPE?=router` → `DEFAULT_PACKAGES.router` 含 dnsmasq → 生成的 kconfig `default y if DEFAULT_dnsmasq` 把它加回 `=y`，两个变体装同一批文件 | seed 在 `dnsmasq-full` 前钉 `# CONFIG_PACKAGE_dnsmasq is not set` |

**kconfig 语义实测**（用本仓库 `scripts/config/conf` 复现生成规则，不是推断）：

- `# CONFIG_X is not set` 扛得住 `default y if DEFAULT_X`（defconfig 尊重显式关闭）→ 原因 2 的修法成立
- 扛不住其他包的 `select PACKAGE_X`（会被强制回 `=y`）→ 若某个保留包硬依赖非 full 变体，冲突会复发
- 符号不存在时 `CONFIG_...=y` 行被无警告删除 → 原因 1 只能靠步骤顺序防。CI 现已在 defconfig 后做审计：按 `tmp/.config-package.in` 把未生效的 seed 行分成「符号不存在」与「符号存在但没开成」两类，报告连同展开的 `.config` 一起作 artifact 上传；**审计本身不阻断构建**（要让它同时回答"能不能出镜像"），只有 `CONFIG_PACKAGE_dnsmasq=y` 复现时才硬失败（已被 §十四 收紧：已知清单外的未生效行也硬失败）

**功能视角**：本次**没有增删任何功能**，只修构建正确性。设备能做的事仍与 §六「仍然完好、一个没动的功能」清单一致；`dnsmasq` 非 full 变体从来不在路由器实装清单里，钉死它不改变行为（dnsmasq-full 以 `PROVIDES:=dnsmasq` 满足依赖）。

**查构建状态的坑**：本目录配了 `upstream=istoreos/istoreos`，`gh run list` 不带 `--repo` 会解析到**上游仓库并返回空数组**，看着像"从没跑过"。必须 `gh run list --repo xcy960815/istoreos --workflow "Build iStoreOS trimmed"`。

### 修复后复查（run 37345712561，17:04Z）

顺序修好 + dnsmasq 钉死后，构建停在新增的审计步骤（几分钟，不再烧 2 小时）。已验证生效的部分：`attr`/`curl`/`libgcrypt`/`luci-theme-argon` 不再出现在丢失列表，`CONFIG_PACKAGE_dnsmasq` 也没被加回。

审计同时打出 **105 行 `CONFIG_PACKAGE_*=y` 未生效**，workflow 现在按 `tmp/.config-package.in` 把它们自动分成两类并上传 `.config`+报告为 artifact：

- **符号本就不存在**：绝大多数是 `libcurl4` `libgcc1` `libubus20250102` 这类**带 ABI 后缀的 opkg 二进制包名**。kconfig 符号是无后缀的 `libcurl`/`libgcc`/`libubus`，后缀只出现在打包出的包名上。这些行自写进 seed 起就是死行（历次构建都丢），不影响功能——库会作为依赖自动进镜像，但"清单"是假的，待清
- **符号存在却没开成**（依赖不满足/被隐藏）：已在 r4 定档，见下方「r4 审计定档」

**顺序错误的真实代价比原判断严重**（对 14:22Z 那次日志的实测计数，非推断）：全文 `openclash|tailscale` 出现 **0** 次、`Installing luci*` **0** 条、`Configuring luci-base` **0** 次——也就是说那次构建的产物根本没有 LuCI 和任何商店应用，是台裸路由；先前只看到 4 条 `cannot find dependency` 是因为核心包（base-files/opkg/istoreos-files/ntfsprogs）硬依赖 feed 包，是这批缺失里**最早撞墙**的一部分，不是全部。

## 八、第三次失败：上游源码 404（run 37347586447 = r4，17:19Z→21:08Z）

前两层已确认修好：`Collected errors` **0** 条、dnsmasq 没被加回、一路跑到编译并在 3.8 小时后挂掉。唯一失败点是 `package/feeds/third/vlmcsd`：

- feed 的 Makefile 用 `PKG_SOURCE_URL_FILE:=$(PKG_VERSION).tar.gz` 去抓 `…/archive/refs/tags/1113.tar.gz`，可上游 tag 实际叫 **`svn1113`**（`gh api repos/Wind4/vlmcsd/tags`）。GitHub + sources.cdn + sources.openwrt + mirror2 四路全 404 → `No more mirrors to try - giving up.`
- **内容没变，只是远端文件名错**：实测 `https://github.com/Wind4/vlmcsd/archive/refs/tags/svn1113.tar.gz` 的 sha256 = feed 里的 `PKG_HASH`（`62f55c48…42cc`）。

修法（**不改 feed 源码**，vlmcsd 是 §三 在用项也不从 seed 删）：CI 在 `make download` 前把它按 dl 目标名预放进 `dl/vlmcsd-1113.tar.gz`，哈希取自 feed 的 Makefile 现场校验。成立依据是 `include/download.mk:350` 的 `$(DL_DIR)/$(FILE)` 规则无前提——文件已在就视为最新；`include/package.mk:214` 的 `check_download_integrity` 只在**哈希不符**时才补 FORCE（:77）。离线三步验证过：首次落位、再跑跳过、内容错则 rc=1 且不留正式文件。

顺带堵第二道延迟：`make download` 对失败包只打 `ERROR: package/… failed to build`、**退出码仍是 0**（r4 步 9 绿，而日志 4448 行已经有这条 ERROR），所以 Download sources 现在自己扫日志并失败退出——死源码在几分钟内暴露，不再等 3.8 小时。

**功能视角**：没有增删任何功能，vlmcsd 仍在固件里。

> ⚠️ 本节只治了下载 404，**漏了同一个 Makefile 的第二处笔误**（`PKG_BUILD_DIR` 目录名），所以 r6/r7 依旧挂在 vlmcsd。真因与最终修法见 §十二；本节的 `dl` 预置 shim 已被 §十二 的做法取代删除。

## 十一、第四次失败：缓存死锁——每次都被自家 timeout 杀在半路（run 37422215944，2026-10-06）

`conclusion: cancelled` 不是人取消的，是 workflow 自己的 `timeout-minutes: 350` 到点被 GitHub 杀掉：job 06:09:37Z 起跑、12:00:21Z 终止，正好 5h50m44s。前 10 步全绿，Compile（06:40:26 开始 `make world`）被杀时正在编 **ruby**。里程碑实测：tools/compile 1h25m → toolchain/compile 23m → target/compile 15m → package/compile 3h17m 才到 ruby 中段——当时据此判断"**4 核托管 runner 上全量冷编译约需 7h+，350 分钟根本装不下**"。

> ⚠️ 这条 7h+ 的推断**已被 §十二 用 r6 之后那次 run（37470180070 = r7）的实测推翻**：r6 被杀时还卡在无用的 `make -j1 V=s` 兜底里，从没测到终点；r7 冷缓存跑到自然失败，全程 5h27m 且**只剩 vlmcsd 一个包没编**，全量冷编真值约 4h15m–4h45m，350 分钟预算够用。本节下面"死循环"的诊断与缓存修法仍然有效。

真正的病是**死循环**：`actions/cache@v4` 的缓存保存在 post 步骤里，`post-if: success()`——job 不成功就不存。而这个仓库 6 次 run 无一成功（`gh cache list` 实测 0 条），于是每次都全量冷编 → 每次都超时取消 → 永远存不上缓存 → 下次还是冷编。此前 §八 修的 vlmcsd 预置在本次 run 是生效的（step 9 绿），不是本症。

**GitHub Actions 取消语义实测**（本次 run 的步骤清单为证，非推断）：job 被 timeout 取消后，`if: always()` 的步骤**照常执行**（Report disk usage 在 12:00:17Z 留下了 df 输出），post 步骤里 `post-if: success()` 的被跳过（Post Cache conclusion=skipped）。所以出路是把"保存"从 post 挪到普通步骤并挂 `always()`。

**修法**（借鉴 draco-china/istoreos-actions 所用 `klever1988/cachewrtbuild` 的机制，不引入第三方 action，用官方 `actions/cache` 的 restore/save 拆分实现）：

- 缓存拆两对独立 restore+save，key 按用途分前缀（`istoreos-dl-<run_id>` / `istoreos-tc-<run_id>`，restore-keys 前缀滚动复用）：
  - `dl`：Save downloads cache 紧跟 Download sources，挂 `always()`——此刻 job 还健康，上传从容，编译超时也保住这 28 分钟的下载
  - `staging_dir`：Save toolchain cache 在 Compile 后，挂 `always()`——**被超时取消也会存**。当时假设"下次 run 恢复后 tools/toolchain 靠 stamp 跳过、从 package/compile 续编（约 4.5–5h，350 分钟内可完成，死循环即破）"，**该假设已被 2026-10-07 复核推翻，见下**；这份缓存已在 §十四 删除
- 缓存路径去掉顶层 `toolchain/`（源码目录，无缓存价值，编译产物在 `staging_dir/`）；`staging_dir` 整目录保留
- 恢复时不做 cachewrtbuild 那招 sed 改顶层 Makefile——不改源码树的文件，符合本仓库纪律

### 复核更正（2026-10-07）：staging_dir 缓存不能续编

读 `rules.mk:186`、`include/package.mk:114-119`、`include/host-build.mk:27-28` 得到的 stamp 落点：

| stamp | 落在哪 | 本 workflow 缓存了吗 |
|---|---|---|
| `STAMP_PREPARED` / `STAMP_CONFIGURED` / `STAMP_BUILT`（含 host 版） | `$(PKG_BUILD_DIR)` = **build_dir/**（`STAMP_DIR:=$(BUILD_DIR)/stamp`，rules.mk:186-187） | ❌ 没缓存 |
| `STAMP_INSTALLED` / `HOST_STAMP_INSTALLED` | **staging_dir/stamp**（package.mk:119 `$(STAGING_DIR)/stamp/.$(PKG_DIR_NAME)..._installed`；host-build.mk:28 `$(HOST_BUILD_PREFIX)/stamp`） | ✅ 缓存了 |

`make` 判定是否重编看的是 `.built`，而它在没进缓存的 `build_dir/` 里；只把 `_installed` 存进缓存，恢复后 `.prepared/.configured/.built` 全缺，tools 与 toolchain 依旧从头编。所以 §十一 的"下次就能续编"不成立，缓存里唯一确定省时间的是 `dl`（省掉那次 28 分钟的 Download sources）。

**判据（下次 run 一眼定性，非推断）**：恢复缓存后 `tools/compile` 若仍约 1h15m（r7 冷缓存实测 1h14m43s，此前这里写的 1h25m 是 r6 被杀时的估读），即证明这份 staging_dir 缓存只是占配额；若接近 0，我这条更正作废。（§十四 已按上面的 stamp 落点表直接删掉这份缓存，本判据不再适用）

**`build_dir` 能不能一起缓存，唯一判据是它的体积，而这个数本机给不出**（M1 Max 跑不了 x86 构建树）——所以主构建 workflow 的 `Report disk usage` 现在顺手量 `dl`/`staging_dir`/`build_dir` 三者体积，并数 `.built`（build_dir 内）与 `*_installed`（staging_dir 内）作为上方落点表的现场版。r7 已实测 dl 1.240GB、staging_dir 1.117GB，`build_dir` 待下一次 run 出数；那次 run 若中途失败，读数只是全量体积的下限。**待用户定的三条路**：①9400F 挂自建 runner，`build_dir` 常驻增量，彻底绕开托管 runner 的 350 分钟与配额（BUILD-CUSTOM 本来就以在 9400F 上编译为主线）；②接受"每次全量冷编"，把 dl 缓存留着、staging_dir 缓存删掉换配额；③先跑一次拿到 tools/compile 实测时长再决定——r7 之后紧接着的那次 run 就是它，判据见 §十三「判据」。——② 的「删 staging_dir」已在 §十四 落地，① 仍待定；`Report disk usage` 现在只量 `dl`/`build_dir`、不再数 stamp。

**参考项目的现状警示**：draco-china/istoreos-actions 最近 20 次 run 全 failure（多为 3 分钟早夭，另有一次 360.3 分钟撞 6h 平台上限），只能借鉴机制不能照抄现状；它的 cachewrtbuild 同样 `post-if: success()`，首次成功前的 bootstrap 问题在我们这里用 `always()` save 解决。

**功能视角**：没有增删任何功能、没有动 seed。构建基础设施修复。当时预期"下一次 run 仍可能超时一次（存下 staging_dir），再下一次即可续编成功"——该预期已被上方「复核更正」推翻，改成：靠缓存续编不成立，下一次 run 仍是全量冷编，超时与否只取决于上面三条路选哪条。

## 十二、CI 整理：审计抽成脚本、去掉重复与失效步骤（2026-10-07）

**功能视角**：没有增删任何功能、没有动 seed 的任何一行 `=y`（只改 seed 头部注释里的过期表述）。设备能做的事与 §六「仍然完好、一个没动的功能」重列后的清单一致；固件产物也不变——本轮全是 CI 侧与文档侧整理。

| # | 改动 | 为什么 |
|---|---|---|
| 1 | 审计逻辑从 workflow 的 28 行内联 shell 抽到 `.github/scripts/seed-audit.sh` | 那是全仓唯一的真逻辑，写在 YAML 里就无法本地执行。抽出后本轮用合成 fixture 验了三条路径：分类正确（死行/真缺各归各位）、`CONFIG_PACKAGE_dnsmasq=y` 复现时 rc=1、缺 `.config`/`tmp/.config-package.in` 时 rc=1 并指名前置没跑 |
| 2 | 审计报告新增第二段「seed 没写却开启的包」 | 取代 §六 安全网 1 原先靠猜的候选清单，直接给 defconfig 自行加回的集合；这份输出也是日后 seed 瘦身的基线数据 |
| 3 | artifact 改收 `config-expanded.txt`、`seed-audit.txt`、`lost_dead.txt`、`lost_hidden.txt`，不再收 11910 行的 `ksyms.txt` 和可推导的 `lost.txt` | 上传结论而不是原料 |
| 4 | 依赖清单收敛为 `.github/apt-packages.txt` 一份，CI 与 BUILD-CUSTOM 都读它 | 原两份已漂移：CI 装 `wget` 却不装 `curl`，而 `scripts/download.pl:113-119` 首选 curl（wget 只是 fallback），CI 当时的 `seed_dl` 也直接调 curl（该 shim 已被 §十三 删除，但 curl 仍是 download.pl 的首选，清单照留）；BUILD-CUSTOM 反之缺 `swig`/`python3-dev` |
| 5 | 去掉 `make -j$(nproc) || make -j1 V=s`，改为单次并行 + `compile.log` 作 `always()` artifact | 串行重跑只是把快速失败拖长、并挤掉存缓存的时间（本地没有时长预算，仍可用 `V=s` 重试，BUILD-CUSTOM 步骤 5 已注明这个差异）。本行"冷编 7h+ 必然跑不完"的前提与"完全不重跑"的做法都被 §十三 修正：改成只重跑出错的包 |
| 6 | 删重复的 `df -hT`（Compile 里那次已被 `always()` 的 Report disk usage 覆盖）、3 处 `shell: bash`（ubuntu runner 默认即 bash）、无人消费的 `echo "kconfig 包符号总数"`（计数已进报告首行）；`Download sources` 里列 URL 的 grep 补 `|| true`，与它自己的注释保持一致 | 左手到右手；以及注释承诺与代码不一致 |
| 7 | 缓存注释按 §十一「复核更正」改写 | 原注释断言"下次 run 从 package/compile 续编"，`rules.mk:186`/`package.mk:114-119` 不支持它 |
| 8 | 文档去重与对账：「商店应用不在构建期」原在 6 处各列一遍包名，现收敛为 §九（证据）＋§十（清单），§三 ⚠️、§六、BUILD-CUSTOM 改为引用；§六「仍然完好」按 r4 口径拆成"固件里确实有"与"要从商店装回"两栏；seed 头部 D 档与 §六 D 档去掉 `linkmount`（§十 已清） | 同一事实写 6 遍，改一处忘五处——§六 那条当时就已经和 §九/§十 直接矛盾 |

**没做的那件（要跑构建才能定）**：seed 现 593 行里估计约一半是传递闭包抄写（`lib*` 46、`kmod-crypto-*` 43、`kmod-usb-*` 43、`shadow*` 36、`kmod-nf-*` 27、`perlbase-*` 26、`kmod-fs-*` 20），硬依赖由 defconfig 自动加回，理论上能收到 ~150 行"意图清单"。但 §六 安全网 3 说得很清楚：软依赖（脚本里 shell 调用而非包依赖）不会被拉回，所以不能靠推理删，必须逐组剥离 → 跑 `make defconfig` → 与基线包集合比差集，差集为 0 的组才算纯冗余。本机是 M1 Max，跑不了 x86 构建树，这一步留到有 Linux 构建环境时做。

**本轮验证方式**：`bash -n` 过；workflow 用 YAML 解析过（16 步，`shell:` 已清空）；`seed-audit.sh` 三条路径以 fixture 实跑过。CI 侧的真实验证要等下一次 run。

## 十三、第六次 run（37470180070 = r7，10-06 13:21→18:49）：唯一失败点仍是 vlmcsd，这次拍到了真因

r7 用的是 §十二 之前的 HEAD（`e06934e5a5`，缓存拆分那次），所以它的价值是**第一条完整的冷缓存基线**：job 自然失败（`failure` 不是 `cancelled`），前 12 步全绿，全程 5h27m38s。

| 阶段 | 起 | 止 | 耗时 | 备注 |
|---|---|---|---|---|
| checkout→apt→restore 缓存 | 13:21:46 | 13:23:55 | 2m09s | 两条 restore 都是 `Cache not found`，即全量冷编 |
| feeds update+install / defconfig+审计 | 13:23:55 | 13:25:25 | 1m30s | |
| Download sources | 13:25:25 | 13:53:26 | **28m01s** | 这就是 `dl` 缓存要省掉的那 28 分钟 |
| tools/compile | 13:53:43 | 15:08:26 | **1h14m43s** | |
| toolchain/compile | 15:08:26 | 15:29:21 | 20m55s | |
| target/compile | 15:29:21 | 15:42:18 | 12m57s | |
| package/compile（-j4） | 15:42:18 | 17:40:06 | 1h57m48s | vlmcsd **15:56:07** 就挂了，`-j4` 把在飞的活儿跑完才退出 |
| 兜底 `make -j1 V=s` | 17:40:12 | 18:48:53 | **1h08m41s** | 又走到同一个错，才第一次打印真因 |
| Save toolchain cache | 18:48:53 | 18:49:21 | 28s | 1.117 GB，`always()` 生效；`dl` 1.240 GB 早在 13:53 存好 |

全程只有 **一个** 包失败：`ERROR: package/feeds/third/vlmcsd failed to build`（出现 2 次 = 并行+串行各一次）。其余包全编过了。

### 真因：feed 的两处笔误，§八 只治了第一处

r7 串行那轮打出的原文（`127744` 行附近）：

```
make[4]: Entering directory '.../build_dir/target-x86_64_musl/vlmcsd-1113'
make[4]: *** No targets specified and no makefile found.  Stop.
time: package/feeds/third/vlmcsd/compile#0.07#0.07#0.13
```

目录**存在但是空的**。`include/unpack.mk:6,65` 只把包 `tar -C $(PKG_BUILD_DIR)/..` 解到父目录、不改名，`package-defaults.mk:64-68` 的 `Build/Prepare/Default` 也不重命名——**构建目录名必须与归档里的目录名逐字相同**。而 `jjm2473/openwrt-third` 的 vlmcsd Makefile 里 tag 叫 `1113`、上游实际叫 **`svn1113`**，归档内目录是 `vlmcsd-svn1113`：

| 行 | 原值 | 改成 |
|---|---|---|
| `PKG_SOURCE_URL_FILE` | `$(PKG_VERSION).tar.gz` | `svn$(PKG_VERSION).tar.gz` |
| `PKG_BUILD_DIR` | `$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)` | `$(BUILD_DIR)/$(PKG_NAME)-svn$(PKG_VERSION)` |

§八 那套"往 `dl/` 预置文件"只补了下载，把第二处原样留着，所以 r6、r7 照挂。现在改成**直接补 feed 副本的这两行**：`dl` 名、URL、构建目录全由 `PKG_SOURCE_URL_FILE` 一处推导，下载与 sha256 校验交回 OpenWrt 自己的机制，curl 预置 shim 删除。

改法成立与否是实测而非推断：把改后的 4 行 `PKG_*` 用 make 展开 → URL `…/archive/refs/tags/svn1113.tar.gz`、`dl` 名 `vlmcsd-svn1113.tar.gz`、构建目录 `…/vlmcsd-svn1113`；实测 `tar tzf` 归档首条正是 `vlmcsd-svn1113/`，实测该 tar 包 sha256 = feed 里的 `PKG_HASH`（`62f55c48…42cc`）。三者对齐。

feed 副本是 `scripts/feeds install` 生成的、不在本仓库版本里，所以改它不违反 §一"不改源码"；**本地构建同样会踩**，命令见 BUILD-CUSTOM.md 步骤 5。

### 顺带两处 CI 修正

1. **去掉 `-j1 V=s` 全局兜底**（§十二 表格第 5 行的做法再收紧）：r7 里它 17:40 起跑、18:48 才又撞上同一个错，白烧 **1h08m**。现在只把 `ERROR: package/…` 点名的包用 `make <pkg>/{download,prepare,compile} -j1 V=s` 重跑，几十秒出真因。
2. **补上 `set -eo pipefail`**：workflow 里没写 `shell:` 的步骤，runner 实际用 `/usr/bin/bash -e {0}`（r7 日志原文），**不带 pipefail**——`make | tee compile.log` 的退出码取自 tee 的 0，编译失败时步骤会**静默变绿**、job 报成功却没有镜像。桩 `make` 实测过四条路径：失败→rc=1 且只重跑被点名的包、成功→rc=0、失败但日志里没有 `ERROR: package` 行→rc=1 并提示去看 compile.log、旧写法（无 pipefail）→**rc=0**（即这个 bug）。

### 更正 §十一 的"冷编 7h+"

r7 的量级是 tools 1h15m + toolchain 21m + target 13m + package/compile（到终点约 2h 出头），**全量冷编约 4h15m–4h45m 而不是 7h+**；那次 7h+ 的推断来自 r6——它被 350 分钟杀掉时还处在无用的 `-j1` 兜底里，从没测到终点。叠加 `dl` 缓存省掉那 28 分钟，350 分钟预算第一次够用，`timeout-minutes` 不动。**§十一「待用户定的三条路」里 ③（先跑一次拿实测时长）已由 r7 回答，①②的取舍等 r8 出结果再定**。

### 判据（下一次 run 一眼定性）

- `dl` 缓存生效 = Download sources 从 28 分钟掉到几分钟
- `staging_dir` 缓存有没有用，仍按 §十一「复核更正」的判据：恢复后 `tools/compile` 若还是约 1h15m 就是白占配额；接近 0 才算我那条评论作废——已作废，staging_dir 缓存在 §十四 删除
- `build_dir` 到底装不装得下：同一次 run 的 `Report disk usage` 会打 `dl`/`build_dir` 体积（§十四 起不再量 staging_dir、不再数 stamp）。`build_dir` 若逼近 10GB 配额，"把它一起缓存"这条出局，只剩 §十一 的 ①（9400F 自建 runner）或 ②（§十四 已删掉 `staging_dir`、只留 `dl`，即接受每次冷编）
- 出镜像的话 `bin/targets/x86/64/manifest` 的包数才是 §六 基准要的最终数，回填 BUILD-CUSTOM 备注

**功能视角**：固件功能零增删，vlmcsd（§三 在用项）照旧在镜像里；改的是 CI 步骤与 feed 副本的两行笔误。刷机后需从商店装回的清单不变，见 §十。

## 十四、同步流程与审计闭环修正（2026-10-08，code-review 8 条）

**功能视角**：固件功能零增删，seed 一行没动；改的是 CI、审计脚本与两份文档。设备能做的事与 §六「仍然完好」一致，刷机后需从商店装回的清单不变（§十）。

| # | 改动 | 为什么 |
|---|---|---|
| 1 | AGENTS.md 同步步骤补 `git checkout istoreos-24.10`，末尾推送用 `git push --force-with-lease origin custom-24.10` | 原写法的 `merge --ff-only` 落在 custom-24.10 上必失败，本地 istoreos-24.10 不前进，随后的 rebase 是空操作，上游修复一个都进不来 |
| 2 | BUILD-CUSTOM.md 同步命令：rebase 后改用 `--force-with-lease` 推送；ff 合并后补 `git push origin istoreos-24.10` | rebase 改写了已推送历史，普通 push 必被拒；`--force-with-lease` 在远端被别处改过时拒绝覆盖，免得顺手 `--force` |
| 3 | 更正"符号改名构建时会提示" | `make defconfig` 对不存在的符号是无警告删除（§七），本地零提示；改由 CI 审计拦截 |
| 4 | `seed-audit.sh`：已知未生效清单（`kmod-thermal`、`kmod-xdp-sockets-diag`，即 §十 的保留项）之外的丢失行硬失败；dnsmasq 与新增丢失两项都检查完再统一退出；已知项若开成了，提示可从清单删 | 原来只发 `::warning::`，上游/feed 改名或依赖变化时 CI 照样绿、镜像悄悄少包，要到刷进主路由才发现。§七 的"审计本身不阻断构建"自此只对已知项成立；往已知清单加项须同时在本文档记账 |
| 5 | 审计报告首行"seed 符号数"改为"feed 包符号总数" | 那是 `tmp/.config-package.in` 的全部包符号（r4 为 11910），不是 seed 行数 |
| 6 | vlmcsd 补丁（CI 与 BUILD-CUSTOM 步骤 3b）只匹配原笔误整行；CI 里 `PKG_VERSION` 已以 svn 开头则跳过，补完后精确校验两行，不符即失败 | third feed 跟踪 `main` 没锁版本，作者自己修好后原来的 `:.*` 盲改会拼出 `svnsvn1113`，要到 Download 阶段才 404 |
| 7 | 删 staging_dir 缓存（Restore/Save toolchain cache 两步） | §十一「复核更正」已证明续不了编（`.built` 在 build_dir）；每次白存约 1.1GB，几次 run 就挤占 10GB 配额，可能把有用的 dl 缓存淘汰掉。即 §十一 三条路里的 ②；①（9400F 自建 runner）仍待定 |
| 8 | Report disk usage 删 `.built`/`*_installed` 计数，只量 `dl`、`build_dir` | staging_dir 缓存删了，这组对比失去意义；`build_dir` 体积仍要实测，用来判 ① |

**本轮验证方式**：`bash -n` 过；workflow YAML 解析过（14 步）。`seed-audit.sh` 用合成 fixture 跑了五条路径：只丢两个已知项 rc=0、多丢一项 rc=1 并列出该项、dnsmasq 被加回 rc=1、已知项开成了 rc=0 并提示、两种错误同时出现 rc=1 且两条 error 都打印（旧脚本"多丢一项"是 rc=0，即这个漏洞）。vlmcsd 补丁用三种 Makefile 实跑：原笔误版补齐 rc=0、`PKG_VERSION:=svn1113` 跳过且无 svnsvn rc=0、改成其他写法 rc=1。CI 侧的真实验证等下一次 run；前提是清完死行后真的只剩那 2 个已知项，若冒出别的项，审计步骤几分钟内就会失败，看 artifact 里的 `seed-audit.txt`。

## 十五、DDNS-Go r8 失败（run 37875891581）


seed 审计、vlmcsd、download 全绿，编了 4h21m，唯一挂掉的包是 `package/feeds/ddnsgo/ddns-go`。V=s 原文：

```
go: ../../go.mod requires go >= 1.25.0 (running go 1.23.12; GOTOOLCHAIN=local)
```

`feeds.conf.default` 当时跟 `main`，sirpdboy 把内核升到 **6.17.1**，其 `go.mod` 要 Go 1.25；`istoreos-24.10` 的 `feeds/packages/lang/golang` 是 **1.23.12**，且 `GOTOOLCHAIN=local` 不许自动下新 toolchain。其余包都编过了。

修法：feed 钉死 tag **`v6.12.2`**（`c0730e9`）。该 tag 的 `PKG_VERSION:=6.12.2`，上游 `go.mod` 写的就是 `go 1.23.12`，和商店当时的 `app-meta-ddnsgo_6.12.2` 同版本。不升级官方 golang（动 packages feed 太大）。功能仍是开箱有 DDNS-Go，只是内核停在 6.12.2，不要再改回 `main` 除非 golang 先升到 ≥1.25。

后续 AI：**不要**再根据 §二 旧表述把 DDNS-Go 删掉；**不要**把这条 feed 扩成整个商店源；**不要**把 `ddnsgo` 改回跟踪 `main`。

## 十七、r9 打盘失败（run 37897946779，2026-10-09）

DDNS-Go 钉 `v6.12.2` 之后包全部编过（含 `feeds/ddnsgo/luci-app-ddns-go`），`package/install` 也过了。挂在：

```
make[3] -C target/linux install
   ERROR: target/linux failed to build.
```

quiet 日志里没有 `ERROR: package` 行，CI 旧逻辑当成「tools/kernel」直接退出，**没有 V=s**。磁盘仍剩 54G，不是空间不够。

### 原因

seed 只写了 `CONFIG_TARGET_ROOTFS_SQUASHFS=y` 和 `PARTSIZE=224`。x86 `FEATURES` 含 `ext4`，`TARGET_ROOTFS_EXT4FS` 默认 y，defconfig 把 **ext4 根镜像**加回来。`make_ext4fs -l 224MB` 按**未压缩** rootfs 算；ruby/git/perl、i915 固件（`DEVICE_PACKAGES` 里的 `kmod-drm-i915` 又拉回来了）、tailscale、ddns-go 叠在一起远超 224MB，这一步必炸。squashfs 能压、刷机也只用 `*-squashfs-combined-efi.img.gz`，ext4 根镜像根本不需要。kernel 分区当时走默认 16MB，vmlinuz+grub 也偏紧。

### 修法（仍只改 seed + CI，不改源码）

| 动作 | 内容 |
|---|---|
| seed 钉关 | `# CONFIG_TARGET_ROOTFS_EXT4FS is not set` |
| seed 加大 | `CONFIG_TARGET_KERNEL_PARTSIZE=32`、`CONFIG_TARGET_ROOTFS_PARTSIZE=512` |
| CI | 看到 `ERROR: target/linux` 时 `make target/linux/install -j1 V=s`；artifact 带上 `logs/target` |

刷完机少的只是「另打一份 ext4 根盘镜像」——LuCI/overlay/扩容不受影响。i915 仍被 profile 加回，属 §六 A 档没钉死 `is not set`，**这次不动**（D 档同样不动），出镜像后再收。

后续 AI：**不要**再把 `TARGET_ROOTFS_EXT4FS` 打开，也**不要**把 PARTSIZE 改回 224。

## 十八、r10 成功后清掉 CI 黄条（2026-10-10）

r10（run 38017418688）出镜像了。页面上两条 warning、一条 notice，都不影响固件：

| 注解 | 原因 | 修法 |
|---|---|---|
| Node.js 20 deprecated | `checkout`/`cache`/`upload-artifact` 还钉 v4 | 改为 `checkout@v5`、`cache@v5`、`upload-artifact@v6`（Node 24） |
| seed 有 2 行未生效 | `kmod-thermal`、`kmod-xdp-sockets-diag` 是 §十 已知项；审计对已知项也 `::warning::` | 已知项只写 artifact；未知丢失仍 `::error::`。**不要**为消黄条从 seed 删这两行，也**不要**把 warning 加回 |
| ubuntu-latest → 26 | GitHub 2026-10-19 起切 Ubuntu 26 | `runs-on: ubuntu-24.04` |

固件功能零增删。不必为这三条重跑 5 小时构建。
