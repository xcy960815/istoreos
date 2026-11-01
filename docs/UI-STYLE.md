# LuCI 界面改造风格指南（Argon / 无 Bootstrap）

> 面向后续 AI：本 fork 的 LuCI 页面如果要「变好看」，**按这份指南改**，不要各写一套。
> 首个落地样例是 OTA 页（`package/diy/luci-app-ota/luasrc/view/admin_system/ota.htm`，
> 变更记录见 `docs/CUSTOM-TRIMMING.md` §四十五）。改任何页面前先读本文件和该页的原始模板。

## 0. 前提与边界

| 约束 | 说明 |
|---|---|
| 主题 | 只装 Argon（Bootstrap 已在构建期移除，见 CUSTOM-TRIMMING §二十四）。不要写依赖 Bootstrap 的类名 |
| 依赖 | **不新增任何前端依赖**（Bootstrap / jQuery / Tailwind / 图标库都不要）。CSS 写在模板内的 `<style>` 里，JS 用原生 + LuCI 自带 `XHR` |
| 改哪里 | 页面模板（`luasrc/view/...`）、自己的 diy 包、或 `.github/scripts/patch-*.sh`（改 feeds 里的主题副本）。**不要为了 UI 动 `config-custom.seed`** |
| 不动什么 | 后端行为、元素 id、状态机、请求路径。UI 改造是**换皮**，不是重写业务 |
| 作用域 | 所有选择器都挂在页面根容器 `#cbi-<功能>` 下，禁止写裸标签选择器或全局类名改（会把别的页面弄花） |

## 1. 设计令牌（design tokens）

用 CSS 变量定义在页面根容器上，深色模式只覆盖变量，不重复写规则。

```css
#cbi-ota {
	--ota-accent: #5e72e4;   /* 主色：Argon 默认 primary，动作按钮 */
	--ota-accent-2: #825ee4; /* 主色渐变第二段：进度条 */
	--ota-ok: #2dce89;       /* 成功：完成态、apply 按钮 */
	--ota-warn: #fb6340;     /* 警示/新版本/取消 */
	--ota-border: #e9ecef;
	--ota-muted: #8898aa;    /* 次要文字 */
	--ota-text: #32325d;     /* 正文标题 */
	--ota-card: #fff;
	--ota-soft: #f7f9fc;     /* 行底、代码块底 */
}
```

| 元素 | 规格 |
|---|---|
| 卡片 | 圆角 `12px`、`1px solid var(--ota-border)`、`box-shadow: 0 2px 12px rgba(50,50,93,.06)`、内边距 `20px 22px`、卡片间距 `16px` |
| 标题 | `18px / 600`，行高 1.3，颜色 `--ota-text` |
| 说明文字 | `13px`，行高 1.6，颜色 `--ota-muted` |
| 次要注释/步骤 | `12px`，`--ota-muted` |
| 按钮 | 内边距 `8px 18px`、圆角 `8px`、`14px`，最小宽 `132px`（避免按钮宽度随文字跳动） |
| 状态点 | `10px` 圆点 + `0 0 0 4px` 同色 12% 透明光环 |
| 进度条 | 高 `10px`、`999px` 圆角、`linear-gradient(90deg, accent, accent-2)` |
| 间距节奏 | 8 / 10 / 12 / 16 / 18 / 20 px，不要出现 13、17 这种随手值 |

颜色只从上面的变量取，不要在组件里写死 `#fff` / `#333`——否则深色模式必翻车。

## 2. 页面骨架

```html
<%+header%>
<%
	local fs = require "nixio.fs"
	-- 需要展示系统信息就在模板里读，别让前端再发一次请求
-%>
<div class="cbi-map" id="cbi-xxx">
	<style>
	#cbi-xxx { /* 令牌 */ }
	/* Argon 的 .cbi-section 自带白卡片，套在里面会“卡中卡”，先压平 */
	#cbi-xxx.cbi-section, #cbi-xxx .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }
	/* 深色模式只覆盖变量 */
	body[theme="dark"] #cbi-xxx { /* ... */ }
	@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-xxx { /* 同上 */ } }
	</style>

	<div class="cbi-section state-ctl state-ctl-unchecked">
		<div class="ota-card">
			<h3 class="ota-title"><%:English msgid%></h3>
			<p class="ota-sub"><%:One line explaining what this page does%></p>
			... 各状态 ...
		</div>
	</div>
</div>
<script>/* 原生 JS，逻辑原样保留 */</script>
<%+footer%>
```

## 3. 组件清单（以 OTA 页为例，可直接复制改名）

| 类名 | 用途 |
|---|---|
| `.ota-card` | 白/深色卡片容器，所有内容都放在卡片里 |
| `.ota-title` / `.ota-sub` / `.ota-cur` | 页标题 / 一句话说明 / 当前状态行（`当前系统: iStoreOS 24.10.8 r46`） |
| `.ota-state` | 状态块的上间距 |
| `.ota-empty` + `.ota-empty-mark` | 空态：居中、圆形淡底图标、主按钮、步骤说明 |
| `.ota-feedback` | 动态反馈文字；`:empty` 时自动隐藏（避免占位空白） |
| `.ota-btn` | 统一按钮尺寸（配合 LuCI 的 `cbi-button-action` / `cbi-button-apply`） |
| `.ota-step` | 「步骤 N/3：…」小字，放在按钮下方或旁边 |
| `.ota-row` + `.ota-row-main` | 横向信息行：左侧状态点+文字，右侧动作按钮 |
| `.ota-dot` + `.ota-dot-new` / `.ota-dot-ok` | 状态点：橙=有新版，绿=完成 |
| `.ota-spinner` | 纯 CSS 转圈（`@keyframes ota-spin`），不要引图标库 |
| `.ota-linkbtn` | 次要动作（取消下载）：无边框文字按钮，hover 才给淡底 |
| `.ota-progress` + `progress` | 进度条；未知进度时 `removeAttribute('value')` 显示不确定态 |
| `.ota-ok` | 成功提示块：淡绿底 + 绿边框 + 圆点 |
| `.ota-check` | 复选框行（`accent-color: var(--ota-accent)`，点击整行可切换） |
| `.ota-actions` | 主按钮 + 步骤说明的横向排列，窄屏自动折行 |
| `.ota-meta` / `.ota-meta-row` / `.ota-meta-k` / `.ota-meta-v` | key/value 表：替代 `<pre>`，key 定宽 92px，value 可换行，`code` 用等宽字体淡底 |
| `.ota-note` | 卡片底部灰色小字/链接 |

原则：**信息用行/表格，不用 `<pre>` 拼字符串**；**一个状态一张卡的内容区，不要把四步堆成一片文字**。

## 4. 状态机：只换显示，不改骨架

原模板的约定保持不变：

```html
<div class="cbi-section state-ctl state-ctl-unchecked"> ... </div>
<div class="state state-unchecked">...</div>
```

```js
var state_switch = function(from, to) {
	state_ctl.classList.remove("state-ctl-" + from);
	state_ctl.classList.add("state-ctl-" + to);
};
```

CSS 里**唯一允许 `!important` 的地方**就是这套显隐：

```css
#cbi-ota .state-ctl .state { display:none !important; }
#cbi-ota .state-ctl.state-ctl-checked .state.state-checked { display:block !important; }
```

- 所有 `id`（`check_result`、`download_bar`…）与 `name`（`check`、`download`、`cancel`）**逐字保留**，否则 JS 直接 null。
- JS 一行都别顺手动；要改行为先单独提交、单独说明。
- 需要「同一页多个区块分属不同状态」时，给外层块同时挂多个 `state state-checked state-downloading`，靠显隐规则天然切换（OTA 的详情卡就是这么做的）。

## 5. 深色模式

Argon 的 `header.htm` 会在 `<body theme="light|dark|normal">` 上输出模式，且 dark 只在 `dark` 或 `normal + prefers-color-scheme: dark` 时加载 `dark.css`。

所以页面只需两段变量覆盖（写法见 §2），并且：

- 组件里**不要**出现 `background:#fff` / `color:#333` 这类硬编码；
- 半透明底色用 `rgba(色, .08)` 这种，深浅底都成立；
- 改完用 §7 的方法生成 `-dark.html` 预览对照，别只测浅色。

本机（J4125）Argon 当前 `argon.@global[0].mode='light'`，深色模式属于**顺便支持**，不能成为回归理由。

## 6. 安全与多语言

| 规则 | 做法 |
|---|---|
| LuCI 模板输出 | `<%=expr%>` 会自动转义 HTML，**用它**；`<%:English%>` 是 i18n，`<%+header%>` 是包含 |
| 后端生成的 HTML | 拼进页面前必须转义外部字符串（GitHub API 的资产名/链接等）。`/bin/ota` 里的 `hesc()` 是最小实现：`& < > "` |
| 文案 | 模板里写英文 msgid，中文进 `po/zh-cn/ota.po`；**不要**在模板里直接写中文（除注释） |
| 新增 msgid | 同一次提交里补 `po/zh-cn/*.po`，并核对模板里每个 `<%:...%>` 都能在 po 中找到（见 §8 第 6 条） |
| 后端脚本输出给页面 | 允许中文（如 `.ota-meta` 的「当前版本」），但值必须过 `hesc()` |

## 7. 本地预览（不改真机也能看样式）

思路：**从 `.htm` 里抽出真实的 `<style>`，配上样例 DOM**，生成自包含 HTML，用 in-app 浏览器截图比对。这样预览用的 CSS 和上线用的完全同源，不会出现「预览好看、真机崩」。

步骤：

1. 用正则取出 `ota.htm` 中 `<style>...</style>` 的内容；
2. 手写样例 DOM（未检查/有新版/下载中/已下载 + 详情卡 + 历史卡），把 LuCI 指令（`<%:...%>`）替换成中文；
3. 加一条预览专用规则把所有状态展开：`#cbi-ota.preview-open .state { display:block !important; }`；
4. 再生成一份深色版：`html.replace('<body>', '<body theme="dark">')`；
5. `python3 -m http.server` 起本地服务（`file://` 在浏览器工具里会被拒），打开截图；
6. 用 `browser.preview` 把文件展示给用户确认。

预览脚本可以照抄这个骨架（放到临时目录即可，不用进仓库）：

```python
import re
src = open("package/diy/luci-app-ota/luasrc/view/admin_system/ota.htm").read()
css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
html = f"""<!doctype html><meta charset="utf-8"><title>预览</title>
<style>body{{background:#f4f6fb}} .cbi-map{{max-width:980px;margin:0 auto;padding:24px}}
{css}
#cbi-ota.preview-open .state{{display:block !important}}</style>
<div class="cbi-map preview-open" id="cbi-ota"> ...样例 DOM... </div>"""
```

**预览不等于真机验证**：字体、Argon 的 `.cbi-section` 内边距、浏览器缩放、深色模式都要在真机页面再看一眼。

## 8. 提交前自检清单

1. `sh -n`（若改了 `/bin/*` 脚本）、`python3 -c 'import yaml,sys;yaml.safe_load(open(".github/workflows/xxx.yml"))'`（若改了 workflow）。
2. 模板 `<%` 与 `%>` 数量相等。
3. 所有元素 `id` / `name` 与旧模板逐一对照，**没有丢失**。
4. JS 逻辑 diff 为空（只允许改与样式相关的 class）。
5. 深色模式：`body[theme="dark"]` 与 `prefers-color-scheme` 两段都在。
6. i18n：`<%:...%>` 的 msgid 全部存在于 `po/zh-cn/*.po`（脚本见下）。
7. 没有新增前端依赖、没有全局选择器、没有写死颜色。
8. 真机或预览二选一都过一遍；有条件就真机截图。
9. 同一次提交更新 `docs/CUSTOM-TRIMMING.md`（功能视角 + 包名明细），seed 行数不变要写明「无变化」。

msgid 自查：

```python
import re
s = open("package/diy/luci-app-ota/luasrc/view/admin_system/ota.htm").read()
ids = set(re.findall(r"<%:([^%]*)%>", s))
po = open("package/diy/luci-app-ota/po/zh-cn/ota.po").read()
print([i for i in sorted(ids) if f'msgid "{i}"' not in po])
```

## 9. 反例（踩过的坑）

| 坑 | 后果 | 正确做法 |
|---|---|---|
| 卡片套卡片（`.cbi-section` 里再放白卡） | 双层白底、阴影打架 | 先压平外层 `.cbi-section`（§2 那三行） |
| 用 `!important` 覆盖 Argon 内部（`.cbi-button` 等） | 主题升级后样式错位 | 只在自有类上加样式，用变量控制配色 |
| 硬编码颜色 | 深色模式白底白字 | 只用令牌变量 |
| 顺手「简化」状态机 / 改 id | JS 取不到元素，功能整块失效 | id、name、函数名原样保留 |
| 把 `<pre>` 里的文本改结构却忘了转义 | HTML 注入 / 排版崩 | 后端 `hesc()`，模板 `<%=%>` |
| 为了 UI 改 seed 加包 | 固件体积与信任边界被动 | UI 全部在模板/CSS 内实现 |
| 只测浅色 | 深色模式不可读 | 生成 `-dark.html` 对照 |

## 10. 命名与记账

- 根容器 `#cbi-<功能>`（`#cbi-ota`、`#cbi-quickstart`…），类名统一 `<功能>-xxx`（`.ota-card`），避免和 Argon/LuCI 撞名。
- 局部变量前缀同上（`--ota-accent`）。
- 提交信息写清「哪个页面 + 什么变化 + §章节」，例：`fix(ota): 当前版本未知——解析 DISTRIB_DESCRIPTION 行尾 rNN；页面重排为卡片式（§四十五）`。
- 文档两层记录：功能视角（用户看到什么变化、不能做什么）+ 包名/文件明细。**不留记录的界面改造视同未完成。**
