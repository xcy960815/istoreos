#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "'data-ui-skin': 'processes'" in t and "#cbi-processes" in t:
    print("SKIP  processes.js: already skinned")
    raise SystemExit(0)

for must in ("callLuciProcessList", "handleSignal", "cbi_update_table", "Hang Up", "Terminate", "Kill"):
    if must not in t:
        raise SystemExit(f"processes.js precheck missing {must}")

old = """\tupdateTable: function(table, processes) {
\t\tvar rows = [];

\t\tprocesses.sort(function(a, b) {
\t\t\treturn (a.PID - b.PID);
\t\t});

\t\tfor (var i = 0; i < processes.length; i++) {
\t\t\tvar proc = processes[i];

\t\t\trows.push([
\t\t\t\tproc.PID,
\t\t\t\tproc.USER,
\t\t\t\tE('span', {'style': 'word-break: break-word'}, proc.COMMAND),
\t\t\t\tproc['%CPU'],
\t\t\t\tproc['%MEM'],
\t\t\t\tE('div', {}, [
\t\t\t\t\tE('button', {
\t\t\t\t\t\t'class': 'btn cbi-button-action',
\t\t\t\t\t\t'click': ui.createHandlerFn(this, 'handleSignal', 1, proc.PID)
\t\t\t\t\t}, _('Hang Up')), ' ',
\t\t\t\t\tE('button', {
\t\t\t\t\t\t'class': 'btn cbi-button-negative',
\t\t\t\t\t\t'click': ui.createHandlerFn(this, 'handleSignal', 15, proc.PID)
\t\t\t\t\t}, _('Terminate')), ' ',
\t\t\t\t\tE('button', {
\t\t\t\t\t\t'class': 'btn cbi-button-negative',
\t\t\t\t\t\t'click': ui.createHandlerFn(this, 'handleSignal', 9, proc.PID)
\t\t\t\t\t}, _('Kill'))
\t\t\t\t])
\t\t\t]);
\t\t}

\t\tcbi_update_table(table, rows, E('em', _('No information available')));
\t},

\trender: function(processes) {
\t\tvar v = E([], [
\t\t\tE('h2', _('Processes')),
\t\t\tE('div', { 'class': 'cbi-map-descr' }, _('This list gives an overview over currently running system processes and their status.')),

\t\t\tE('table', { 'class': 'table' }, [
\t\t\t\tE('tr', { 'class': 'tr table-titles' }, [
\t\t\t\t\tE('th', { 'class': 'th' }, _('PID')),
\t\t\t\t\tE('th', { 'class': 'th' }, _('Owner')),
\t\t\t\t\tE('th', { 'class': 'th' }, _('Command')),
\t\t\t\t\tE('th', { 'class': 'th' }, _('CPU usage (%)')),
\t\t\t\t\tE('th', { 'class': 'th' }, _('Memory usage (%)')),
\t\t\t\t\tE('th', { 'class': 'th center nowrap cbi-section-actions' })
\t\t\t\t])
\t\t\t])
\t\t]);

\t\tthis.updateTable(v.lastElementChild, processes);

\t\treturn v;
\t},"""

if old not in t:
    raise SystemExit("processes.js: updateTable + render anchor not found")

css_lines = [
    "#cbi-processes {",
    "	--proc-accent: #5e72e4; --proc-ok: #2dce89; --proc-warn: #fb6340; --proc-danger: #f5365c;",
    "	--proc-border: #e9ecef; --proc-muted: #8898aa; --proc-text: #32325d; --proc-card: #fff; --proc-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-processes { --proc-border:#3a3a3d; --proc-muted:#9aa2ad; --proc-text:#d7dae0; --proc-card:#232324; --proc-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-processes { --proc-border:#3a3a3d; --proc-muted:#9aa2ad; --proc-text:#d7dae0; --proc-card:#232324; --proc-soft:#2b2b2d; } }',
    "#cbi-processes.cbi-map, #cbi-processes .cbi-map { padding: 0; margin: 0; }",
    "#cbi-processes .proc-head {",
    "	display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px 16px;",
    "	padding: 16px 22px; margin: 0 0 16px; background: var(--proc-card); border: 1px solid var(--proc-border);",
    "	border-radius: 12px; box-shadow: 0 2px 12px rgba(50,50,93,.06);",
    "}",
    "#cbi-processes .proc-head-left h2 { margin: 0 0 4px; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--proc-text); }",
    "#cbi-processes .proc-head-left .cbi-map-descr { margin: 0; font-size: 13px; line-height: 1.6; color: var(--proc-muted); }",
    "#cbi-processes .proc-head-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }",
    "#cbi-processes .proc-badge-count {",
    "	display: inline-block; padding: 4px 10px; border-radius: 999px; background: var(--proc-soft);",
    "	border: 1px solid var(--proc-border); font-size: 12px; font-weight: 600; color: var(--proc-muted); white-space: nowrap;",
    "}",
    "#cbi-processes .proc-filter-input {",
    "	box-sizing: border-box; padding: 6px 12px; border: 1px solid var(--proc-border); border-radius: 8px;",
    "	background: var(--proc-soft); color: var(--proc-text); font-size: 13px; width: 200px;",
    "	transition: border-color .15s ease, box-shadow .15s ease;",
    "}",
    "#cbi-processes .proc-filter-input:focus { border-color: var(--proc-accent); outline: 0; box-shadow: 0 0 0 3px rgba(94, 114, 228, .15); }",
    "#cbi-processes .proc-card {",
    "	background: var(--proc-card); border: 1px solid var(--proc-border); border-radius: 12px;",
    "	box-shadow: 0 2px 12px rgba(50,50,93,.06); overflow: hidden; margin: 0 0 16px;",
    "}",
    "#cbi-processes table.table { width: 100%; border-collapse: collapse; margin: 0; }",
    "#cbi-processes table.table .table-titles th {",
    "	background: var(--proc-soft); color: var(--proc-muted); font-size: 12px; font-weight: 600;",
    "	text-transform: uppercase; letter-spacing: .5px; padding: 12px 16px; border-bottom: 1px solid var(--proc-border); text-align: left;",
    "}",
    "#cbi-processes table.table tr.tr:not(.table-titles) { border-bottom: 1px solid var(--proc-border); transition: background-color .15s ease; }",
    "#cbi-processes table.table tr.tr:not(.table-titles):hover { background-color: var(--proc-soft); }",
    "#cbi-processes table.table tr.tr:not(.table-titles):last-child { border-bottom: 0; }",
    "#cbi-processes table.table td.td { padding: 10px 16px; font-size: 13px; color: var(--proc-text); vertical-align: middle; }",
    "#cbi-processes .proc-badge-pid {",
    "	display: inline-block; padding: 2px 6px; border-radius: 4px; background: var(--proc-soft);",
    "	border: 1px solid var(--proc-border); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;",
    "	font-size: 12px; color: var(--proc-text); font-weight: 600;",
    "}",
    "#cbi-processes .proc-user { font-size: 13px; font-weight: 500; color: var(--proc-muted); }",
    "#cbi-processes .proc-cmd {",
    "	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; color: var(--proc-text);",
    "	word-break: break-all; display: block; max-width: 520px;",
    "}",
    "#cbi-processes .proc-pct { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; font-weight: 600; }",
    "#cbi-processes .proc-pct.proc-high { color: var(--proc-danger) !important; }",
    "#cbi-processes .proc-btn-group { display: flex; align-items: center; justify-content: flex-end; gap: 6px; flex-wrap: nowrap; }",
    "#cbi-processes .proc-btn {",
    "	padding: 4px 10px !important; border-radius: 6px !important; font-size: 12px !important;",
    "	font-weight: 500 !important; min-width: 0 !important; line-height: 1.4 !important; cursor: pointer;",
    "	transition: all .15s ease; border: 1px solid transparent;",
    "}",
    "#cbi-processes .proc-btn-hup { background: var(--proc-soft) !important; border-color: var(--proc-border) !important; color: var(--proc-text) !important; }",
    "#cbi-processes .proc-btn-hup:hover { background: var(--proc-border) !important; }",
    "#cbi-processes .proc-btn-term { background: rgba(251, 99, 64, .1) !important; border-color: rgba(251, 99, 64, .25) !important; color: var(--proc-warn) !important; }",
    "#cbi-processes .proc-btn-term:hover { background: rgba(251, 99, 64, .2) !important; }",
    "#cbi-processes .proc-btn-kill { background: rgba(245, 54, 92, .1) !important; border-color: rgba(245, 54, 92, .25) !important; color: var(--proc-danger) !important; }",
    "#cbi-processes .proc-btn-kill:hover { background: rgba(245, 54, 92, .2) !important; }",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)

new = """\tupdateTable: function(table, processes) {
\t\tvar rows = [];

\t\tprocesses.sort(function(a, b) {
\t\t\treturn (a.PID - b.PID);
\t\t});

\t\tfor (var i = 0; i < processes.length; i++) {
\t\t\tvar proc = processes[i];

\t\t\trows.push([
\t\t\t\tE('span', { 'class': 'proc-badge-pid' }, String(proc.PID)),
\t\t\t\tE('span', { 'class': 'proc-user' }, String(proc.USER)),
\t\t\t\tE('span', { 'class': 'proc-cmd' }, proc.COMMAND),
\t\t\t\tE('span', { 'class': 'proc-pct' + (+proc['%CPU'] > 10 ? ' proc-high' : '') }, proc['%CPU'] + '%'),
\t\t\t\tE('span', { 'class': 'proc-pct' + (+proc['%MEM'] > 10 ? ' proc-high' : '') }, proc['%MEM'] + '%'),
\t\t\t\tE('div', { 'class': 'proc-btn-group' }, [
\t\t\t\t\tE('button', {
\t\t\t\t\t\t'class': 'btn cbi-button proc-btn proc-btn-hup',
\t\t\t\t\t\t'title': _('Hang Up'),
\t\t\t\t\t\t'click': ui.createHandlerFn(this, 'handleSignal', 1, proc.PID)
\t\t\t\t\t}, _('Hang Up')), ' ',
\t\t\t\t\tE('button', {
\t\t\t\t\t\t'class': 'btn cbi-button proc-btn proc-btn-term',
\t\t\t\t\t\t'title': _('Terminate'),
\t\t\t\t\t\t'click': ui.createHandlerFn(this, 'handleSignal', 15, proc.PID)
\t\t\t\t\t}, _('Terminate')), ' ',
\t\t\t\t\tE('button', {
\t\t\t\t\t\t'class': 'btn cbi-button proc-btn proc-btn-kill',
\t\t\t\t\t\t'title': _('Kill'),
\t\t\t\t\t\t'click': ui.createHandlerFn(this, 'handleSignal', 9, proc.PID)
\t\t\t\t\t}, _('Kill'))
\t\t\t\t])
\t\t\t]);
\t\t}

\t\tcbi_update_table(table, rows, E('em', _('No information available')));

\t\tvar filterInput = document.querySelector('#cbi-processes .proc-filter-input');
\t\tif (filterInput && filterInput.value.trim() !== '') {
\t\t\tvar ev = new Event('input', { bubbles: true });
\t\t\tfilterInput.dispatchEvent(ev);
\t\t} else {
\t\t\tvar cnt = document.querySelector('#proc-count');
\t\t\tif (cnt) cnt.textContent = processes.length + ' ' + _('Processes');
\t\t}
\t},

\trender: function(processes) {
\t\tvar css = '' +
""" + css_js + """;

\t\tvar filterInput = E('input', {
\t\t\t'type': 'text',
\t\t\t'class': 'cbi-input-text proc-filter-input',
\t\t\t'placeholder': _('Filter') + '...',
\t\t\t'input': function(ev) {
\t\t\t\tvar query = ev.target.value.toLowerCase().trim();
\t\t\t\tvar table = document.querySelector('#cbi-processes table.table');
\t\t\t\tif (!table) return;
\t\t\t\tvar trs = table.querySelectorAll('tr.tr:not(.table-titles)');
\t\t\t\tvar matchCount = 0;
\t\t\t\tfor (var j = 0; j < trs.length; j++) {
\t\t\t\t\tvar tr = trs[j];
\t\t\t\t\tvar text = tr.textContent.toLowerCase();
\t\t\t\t\tvar show = !query || text.indexOf(query) !== -1;
\t\t\t\t\ttr.style.display = show ? '' : 'none';
\t\t\t\t\tif (show) matchCount++;
\t\t\t\t}
\t\t\t\tvar cnt = document.querySelector('#proc-count');
\t\t\t\tif (cnt) cnt.textContent = (query ? matchCount + '/' : '') + trs.length + ' ' + _('Processes');
\t\t\t}
\t\t});

\t\tvar head = E('div', { 'class': 'proc-head' }, [
\t\t\tE('div', { 'class': 'proc-head-left' }, [
\t\t\t\tE('h2', {}, _('Processes')),
\t\t\t\tE('div', { 'class': 'cbi-map-descr' }, _('This list gives an overview over currently running system processes and their status.'))
\t\t\t]),
\t\t\tE('div', { 'class': 'proc-head-right' }, [
\t\t\t\tE('span', { 'id': 'proc-count', 'class': 'proc-badge-count' }, [ processes.length + ' ' + _('Processes') ]),
\t\t\t\tfilterInput
\t\t\t])
\t\t]);

\t\tvar table = E('table', { 'class': 'table' }, [
\t\t\tE('tr', { 'class': 'tr table-titles' }, [
\t\t\t\tE('th', { 'class': 'th' }, _('PID')),
\t\t\t\tE('th', { 'class': 'th' }, _('Owner')),
\t\t\t\tE('th', { 'class': 'th' }, _('Command')),
\t\t\t\tE('th', { 'class': 'th' }, _('CPU usage (%)')),
\t\t\t\tE('th', { 'class': 'th' }, _('Memory usage (%)')),
\t\t\t\tE('th', { 'class': 'th right nowrap cbi-section-actions' })
\t\t\t])
\t\t]);

\t\tvar card = E('div', { 'class': 'proc-card' }, [ table ]);

\t\tvar v = E('div', { 'id': 'cbi-processes', 'class': 'cbi-map' }, [
\t\t\tE('style', { 'data-ui-skin': 'processes' }, [ css ]),
\t\t\thead,
\t\t\tcard
\t\t]);

\t\tthis.updateTable(table, processes);

\t\treturn v;
\t},"""

t2 = t.replace(old, new, 1)
if t2 == t:
    raise SystemExit("processes.js replace failed")

for must in ("callLuciProcessList", "handleSignal", "cbi_update_table", "data-ui-skin", "#cbi-processes", "proc-head", "proc-filter-input"):
    if must not in t2:
        raise SystemExit(f"processes.js missing {must}")

p.write_text(t2, encoding="utf-8")
print(f"OK    processes.js skinned ({p})")
