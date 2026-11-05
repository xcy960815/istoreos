#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "ddnsgo-log" in t and "#cbi-ddns-go-log" in t:
    print("SKIP  ddns-go log.js: already skinned")
    raise SystemExit(0)

old_css = """		var css = `
			/* 日志框文本区域 */
			#log_textarea pre {
				padding: 10px; /* 内边距 */
				border-bottom: 1px solid #ddd; /* 边框颜色 */
				font-size: small;
				line-height: 1.3; /* 行高 */
				white-space: pre-wrap;
				word-wrap: break-word;
				overflow-y: auto;
			}
			/* 5s 自动刷新文字 */
			.cbi-section small {
				margin-left: 1rem;
				font-size: small; 
				color: #666; /* 深灰色文字 */
			}
		`;"""

new_css = """		var css = `
			#cbi-ddns-go-log {
				--dgl-accent: #5e72e4; --dgl-warn: #fb6340; --dgl-border: #e9ecef;
				--dgl-muted: #8898aa; --dgl-text: #32325d; --dgl-card: #fff; --dgl-soft: #f7f9fc;
			}
			#cbi-ddns-go-log.cbi-section, #cbi-ddns-go-log .cbi-section {
				padding: 0; border: 0; background: none; box-shadow: none; margin: 0;
			}
			body[theme="dark"] #cbi-ddns-go-log {
				--dgl-border: #3a3a3d; --dgl-muted: #9aa2ad; --dgl-text: #d7dae0; --dgl-card: #232324; --dgl-soft: #2b2b2d;
			}
			@media (prefers-color-scheme: dark) {
				body[theme="normal"] #cbi-ddns-go-log {
					--dgl-border: #3a3a3d; --dgl-muted: #9aa2ad; --dgl-text: #d7dae0; --dgl-card: #232324; --dgl-soft: #2b2b2d;
				}
			}
			#cbi-ddns-go-log .ddnsgo-log-card {
				background: var(--dgl-card); border: 1px solid var(--dgl-border); border-radius: 12px;
				box-shadow: 0 2px 12px rgba(50,50,93,.06); padding: 20px 22px; margin: 0 0 16px;
			}
			#cbi-ddns-go-log .ddnsgo-log-bar {
				display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
				margin: 0 0 12px;
			}
			#cbi-ddns-go-log .cbi-button {
				min-width: 132px; padding: 8px 18px; border-radius: 8px; font-size: 14px;
			}
			#cbi-ddns-go-log #log_textarea {
				font-size: 13px; color: var(--dgl-muted);
			}
			#cbi-ddns-go-log #log_textarea pre {
				margin: 0; padding: 14px 16px; background: var(--dgl-soft); color: var(--dgl-text);
				border: 1px solid var(--dgl-border); border-radius: 10px;
				font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
				font-size: 12px; line-height: 1.6; max-height: 62vh;
				white-space: pre-wrap; word-wrap: break-word; overflow-y: auto;
			}
			#cbi-ddns-go-log small {
				margin: 0; font-size: 12px; color: var(--dgl-muted);
			}
			#cbi-ddns-go-log .ddnsgo-note {
				font-size: 12px; color: var(--dgl-muted);
			}
			#cbi-ddns-go-log .ddnsgo-note a {
				color: var(--dgl-muted);
			}
		`;"""

if old_css not in t:
    raise SystemExit("ddns-go log.js: css anchor not found")
t = t.replace(old_css, new_css, 1)

old_ret = """		return E('div', { 'class': 'cbi-map' }, [
			E('style', [css]),
			E('div', { 'class': 'cbi-section' }, [
				clear_log_button,
				log_textarea,
				E('small', {}, _('Refresh every 5 seconds.').format(L.env.pollinterval)),
				E('div', { 'class': 'cbi-section-actions cbi-section-actions-right' })
			]),
		E('div', { 'style': 'text-align: right;  font-style: italic;' }, [
                E('span', {}, [
                    _('© github '),
                    E('a', { 
                        'href': 'https://github.com/sirpdboy', 
                        'target': '_blank',
                        'style': 'text-decoration: none;'
                    }, 'by sirpdboy')
                ])
            ])


		]);"""

new_ret = """		return E('div', { 'id': 'cbi-ddns-go-log', 'class': 'cbi-map' }, [
			E('style', { 'data-ui-skin': 'ddnsgo-log' }, [css]),
			E('div', { 'class': 'cbi-section' }, [
				E('div', { 'class': 'ddnsgo-log-card' }, [
					E('div', { 'class': 'ddnsgo-log-bar' }, [
						clear_log_button,
						E('small', {}, _('Refresh every 5 seconds.').format(L.env.pollinterval))
					]),
					log_textarea,
					E('div', { 'class': 'cbi-section-actions cbi-section-actions-right' })
				])
			]),
			E('div', { 'class': 'ddnsgo-note', 'style': 'text-align: right;  font-style: italic;' }, [
				E('span', {}, [
					_('© github '),
					E('a', { 
						'href': 'https://github.com/sirpdboy', 
						'target': '_blank',
						'style': 'text-decoration: none;'
					}, 'by sirpdboy')
				])
			])
		]);"""

if old_ret not in t:
    raise SystemExit("ddns-go log.js: return E('div', ...) anchor not found")
t = t.replace(old_ret, new_ret, 1)

for must in (
    "#cbi-ddns-go-log",
    "ddnsgo-log",
    "log_textarea",
    "/var/log/ddns-go.log",
    "/usr/libexec/ddns-go-call",
    "clear_log",
    "by sirpdboy",
):
    if must not in t:
        raise SystemExit(f"ddns-go log.js missing {must}")
p.write_text(t, encoding="utf-8")
print(f"OK    ddns-go log.js skinned ({p})")
