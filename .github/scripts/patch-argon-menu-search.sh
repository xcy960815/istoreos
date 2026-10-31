#!/usr/bin/env bash
# 把 Argon 侧栏「搜索菜单」修成正常的下拉搜索（§四十三，2026-10-31 用户确认样式）：
#   ① 空输入不再弹「输入为空」大空框（原代码点一下空框就弹，还配 min-height:10em）
#   ② 结果面板去掉 min-height:10em，随内容自适应（一行结果不再撑出大空框）
#   ③ 面板加圆角+阴影，overflow-y: scroll→auto（滚动条槽不再常驻），输入框圆角 1lh→.75rem 统一
#   ④ 「未找到」提示居中（原来被 direction:rtl 推到右侧）
# 必须在 feeds install 之后、make defconfig 之前跑。
# 改的是 feeds 生成的副本，不进 git，不算改源码（第 ⑤ 条构建例外，AGENTS.md 有清单）。
# 任何锚点对不上 = third feed 的主题改了布局，报错人工复核，不许静默跳过。
set -euo pipefail

root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"

d=
for p in package/feeds/third/luci-theme-argon feeds/third/luci-theme-argon; do
  [ -f "$p/htdocs/luci-static/resources/menu-argon.js" ] && d=$p && break
done
[ -n "$d" ] || {
  echo "::error::找不到 luci-theme-argon（feeds install 了吗？third feed 的主题改名/换位置了？）"
  exit 1
}

python3 - "$d" <<'PYEOF'
import sys, pathlib

base = pathlib.Path(sys.argv[1])
FAILURES = []

def patch(rel, old, new, label):
    p = base / rel
    text = p.read_text(encoding="utf-8")
    if new in text:
        print(f"SKIP  {label} (already applied)")
        return
    if old not in text:
        FAILURES.append(label)
        print(f"FAIL  {label}: anchor not found in {p}")
        return
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"OK    {label}")

# 1. menu-argon.js：删掉「先塞 Empty Input 提示再 return」的逻辑，空输入直接关面板
patch("htdocs/luci-static/resources/menu-argon.js",
"""		var do_search = function() {
			var ul = search_result.querySelector("ul");
			var li = document.createElement("li");
			var tips = document.createElement("span");
			tips.innerText = _("Empty Input");
			li.appendChild(tips);
			ul.innerHTML="";
			ul.appendChild(li);
			if (search.value === "")
				return;
""",
"""		var do_search = function() {
			var ul = search_result.querySelector("ul");
			ul.innerHTML = "";
			if (search.value === "") {
				close_result();
				return;
			}
""",
"js: do_search drops Empty Input tip and closes on empty input")

# 2. 「未找到」从 span 包一层改成 li.search-tips（css 里居中弱化）
patch("htdocs/luci-static/resources/menu-argon.js",
"""			if (found.length > 0) {
				ul.innerHTML="";
			} else {
				tips.innerText = _("Not Found");
			}
""",
"""			if (found.length === 0) {
				var li = document.createElement("li");
				li.className = "search-tips";
				li.innerText = _("Not Found");
				ul.appendChild(li);
			}
""",
"js: Not Found tip becomes li.search-tips")

# 3. do_search 末尾展开面板：只有真的搜了才显示，空输入永远不弹
patch("htdocs/luci-static/resources/menu-argon.js",
"""			}, ul);
		};
		var close_result = function() {
""",
"""			}, ul);
			search_result.style.display = "";
		};
		var close_result = function() {
""",
"js: do_search reopens panel only after successful search")

# 4. 事件处理不再无条件强制展开
patch("htdocs/luci-static/resources/menu-argon.js",
"""		search.addEventListener('keyup', function(e){
			if (e.isComposing)
				return;
			do_search();
			if (search_result.style.display === "none") {
				search_result.style.display = "";
			}
		});
		search.addEventListener('click', function(e){
			if (search_result.style.display === "none") {
				do_search();
				search_result.style.display = "";
			} else {
				close_result();
			}
		});
""",
"""		search.addEventListener('keyup', function(e){
			if (e.isComposing)
				return;
			do_search();
		});
		search.addEventListener('click', function(e){
			if (search_result.style.display === "none" && search.value !== "") {
				do_search();
			} else {
				close_result();
			}
		});
""",
"js: handlers no longer force-show the panel")

# 5. header.htm：结果 ul 的内联样式挪进 css，去掉 min-height
patch("luasrc/view/themes/argon/header.htm",
'<ul class="float-list" style="width: 90%;min-height: 10em;max-height: 20em;"></ul>',
'<ul class="float-list"></ul>',
"htm: result ul inline style removed")

# 6. cascade.css（生效的编译产物）
patch("htdocs/luci-static/argon/css/cascade.css",
"#menu_search{margin:0 auto;padding:0 .5rem;width:90%;border-radius:1lh}",
"#menu_search{margin:0 auto;padding:0 .5rem;width:90%;border-radius:.75rem}",
"css: input radius 1lh -> .75rem")

patch("htdocs/luci-static/argon/css/cascade.css",
"#search_result .float-list{overflow-x:hidden;overflow-y:scroll;padding-left:0;padding-right:0}",
"#search_result .float-list{width:90%;max-height:16em;overflow-x:hidden;overflow-y:auto;border-radius:.75rem;box-shadow:0 .5rem 1rem rgba(0,0,0,.15);padding-left:0;padding-right:0}",
"css: panel sized by content, radius+shadow, auto scrollbar")

patch("htdocs/luci-static/argon/css/cascade.css",
"#search_result .float-list a,#search_result .float-list span{display:block;width:100%;padding-left:1em;padding-right:1em;user-select:none;color:#5f6368;color:var(--menu-color);overflow-x:hidden;text-overflow:ellipsis;white-space:nowrap;direction:rtl}",
"#search_result .float-list a,#search_result .float-list span{display:block;width:100%;padding-left:1em;padding-right:1em;user-select:none;color:#5f6368;color:var(--menu-color);overflow-x:hidden;text-overflow:ellipsis;white-space:nowrap;direction:rtl}\n"
"#search_result .float-list .search-tips{padding:.5em 1em;text-align:center;direction:ltr;opacity:.6;cursor:default}",
"css: .search-tips centered hint")

# 7. dark.css：提示色跟随暗色覆盖
patch("htdocs/luci-static/argon/css/dark.css",
"#search_result .float-list a,#search_result .float-list span{color:#cccccc !important}",
"#search_result .float-list a,#search_result .float-list span{color:#cccccc !important}\n"
"#search_result .float-list .search-tips{color:#cccccc !important}",
"dark.css: .search-tips follows dark color")

# 8. cascade.less（源码与产物同步，构建期不编译，纯维护一致性）
patch("htdocs/luci-static/argon/less/cascade.less",
"""#menu_search {
    margin: 0 auto;
    padding: 0 0.5rem;
    width: 90%;
    border-radius: 1lh;
}""",
"""#menu_search {
    margin: 0 auto;
    padding: 0 0.5rem;
    width: 90%;
    border-radius: 0.75rem;
}""",
"less: input radius 1lh -> .75rem")

patch("htdocs/luci-static/argon/less/cascade.less",
"""    .float-list {
        overflow-x: hidden;
        overflow-y: scroll;
        padding-left: 0;
        padding-right: 0;
        a, span {""",
"""    .float-list {
        width: 90%;
        max-height: 16em;
        overflow-x: hidden;
        overflow-y: auto;
        border-radius: 0.75rem;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        padding-left: 0;
        padding-right: 0;
        a, span {""",
"less: panel sized by content, radius+shadow, auto scrollbar")

patch("htdocs/luci-static/argon/less/cascade.less",
"""            direction: rtl;
        }
    }
}


/* IE hacks */""",
"""            direction: rtl;
        }
        .search-tips {
            padding: 0.5em 1em;
            text-align: center;
            direction: ltr;
            user-select: none;
            opacity: 0.6;
            cursor: default;
        }
    }
}


/* IE hacks */""",
"less: .search-tips rule")

if FAILURES:
    print(f"::error::{len(FAILURES)} 处锚点没对上（{', '.join(FAILURES)}），third feed 的主题可能改了写法，人工复核", file=sys.stderr)
    sys.exit(1)
print("all menu-search patches applied")
PYEOF

js="$d/htdocs/luci-static/resources/menu-argon.js"
if command -v node >/dev/null 2>&1; then
  node --check "$js"
  echo "node --check: menu-argon.js 语法通过"
else
  echo "::warning::没有 node，跳过 menu-argon.js 语法检查（CI 上必须跑到）"
fi

# 终检：关键改动必须能 grep 到，旧的丑态必须消失
grep -q 'search-tips' "$js" || { echo "::error::$js 里没有 search-tips"; exit 1; }
if grep -q 'Empty Input' "$js"; then echo "::error::$js 还引用 Empty Input（空态应完全不弹）"; exit 1; fi
if grep -q 'min-height: 10em' "$d/luasrc/view/themes/argon/header.htm"; then echo "::error::header.htm 还有 min-height: 10em"; exit 1; fi
grep -q 'search-tips' "$d/htdocs/luci-static/argon/css/cascade.css" || { echo "::error::cascade.css 里没有 .search-tips"; exit 1; }
if grep -q '#menu_search{margin:0 auto;padding:0 .5rem;width:90%;border-radius:1lh}' "$d/htdocs/luci-static/argon/css/cascade.css"; then echo "::error::cascade.css 输入框还是 1lh 圆角"; exit 1; fi
if grep -qF '#search_result .float-list{overflow-x:hidden;overflow-y:scroll;padding-left:0;padding-right:0}' "$d/htdocs/luci-static/argon/css/cascade.css"; then echo "::error::cascade.css 弹层还是常驻滚动条"; exit 1; fi
grep -q 'search-tips' "$d/htdocs/luci-static/argon/css/dark.css" || { echo "::error::dark.css 里没有 .search-tips"; exit 1; }
grep -q 'search-tips' "$d/htdocs/luci-static/argon/less/cascade.less" || { echo "::error::cascade.less 里没有 .search-tips"; exit 1; }

echo "argon menu-search 样式补丁 OK ($d)"
