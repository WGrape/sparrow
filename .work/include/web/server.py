#!/usr/bin/env python3
"""
Sparrow Web Dashboard
Usage: python3 server.py [port]
"""

import http.server
import json
import os
import platform
import re
import subprocess
import sys
import threading
import webbrowser
from urllib.parse import urlparse

BASE_PATH = os.environ.get("SPARROW_BASE_PATH", os.getcwd())


def _parse_root_env():
    """Read and parse root .env file into a dict."""
    root_env = os.path.join(BASE_PATH, ".env")
    result = {}
    if os.path.isfile(root_env):
        with open(root_env, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    result[k.strip()] = v.strip()
    return result


def _load_enable_service_list():
    """Read ENABLE_SERVICE_LIST from root .env file."""
    env = _parse_root_env()
    if "ENABLE_SERVICE_LIST" in env:
        val = env["ENABLE_SERVICE_LIST"].strip()
        if val.startswith("(") and val.endswith(")"):
            val = val[1:-1]
        return re.findall(r'"([^"]+)"', val)
    return []


def _load_support_service_list():
    """Read SUPPORT_SERVICE_LIST from root .env file."""
    env = _parse_root_env()
    if "SUPPORT_SERVICE_LIST" in env:
        val = env["SUPPORT_SERVICE_LIST"].strip()
        if val.startswith("(") and val.endswith(")"):
            val = val[1:-1]
        return re.findall(r'"([^"]+)"', val)
    return []


def parse_config_file():
    """Read CONTAINER_NAMESPACE from root .env."""
    return _parse_root_env()


def get_running_containers():
    """Return a set of running container names."""
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=5
        )
        return set(r.stdout.strip().splitlines())
    except Exception:
        return set()


def get_local_images():
    """Return a set of 'repo:tag' strings of locally available images."""
    try:
        r = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True, text=True, timeout=5
        )
        return set(r.stdout.strip().splitlines())
    except Exception:
        return set()


def parse_env_file(service):
    """Parse per-service variables from the root .env file."""
    root_env = os.path.join(BASE_PATH, ".env")
    service_upper = service.upper()
    images = []
    config = []
    if not os.path.isfile(root_env):
        return images, config

    # We collect variables that belong to this service:
    # 1. Variables prefixed with SERVICE_UPPER_
    # 2. Variables prefixed with IMAGE_*_SERVICE_UPPER_*
    prefix = service_upper + "_"
    with open(root_env, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("###") or stripped.startswith("#"):
                continue
            if "=" not in line:
                continue
            key_part, _, rest = line.partition("=")
            key = key_part.strip()
            if "#" in rest:
                value, _, comment = rest.partition("#")
                value = value.strip()
                comment = comment.strip()
            else:
                value = rest.strip()
                comment = ""

            # Match image keys: IMAGE_(BASIC|APP|OFFICIAL)_{SERVICE}_...
            is_image = bool(re.match(
                r'^IMAGE_(BASIC|APP|OFFICIAL)_' + re.escape(service_upper) + r'(_|$)', key
            ))
            # Match config keys: {SERVICE}_...
            is_config = key.startswith(prefix)

            if not is_image and not is_config:
                continue

            entry = {"key": key, "value": value, "comment": comment}
            if is_image:
                images.append(entry)
            else:
                config.append(entry)
    return images, config


def read_compose_file(service):
    """Extract this service's block from the root docker-compose.yml."""
    root_compose = os.path.join(BASE_PATH, "docker-compose.yml")
    if not os.path.isfile(root_compose):
        return ""

    with open(root_compose, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the line where this service's block starts (2-space indented key under services:)
    # e.g. "  etcd:" or "  mysql:"
    service_pattern = re.compile(r'^  ' + re.escape(service) + r'\s*:')
    # Any other top-level service key (2-space indent + word + colon, but not deeper indent)
    next_service_pattern = re.compile(r'^  [a-zA-Z]')

    in_services = False
    start = None
    end = None

    for i, line in enumerate(lines):
        if line.strip() == "services:":
            in_services = True
            continue
        if not in_services:
            continue
        if start is None:
            if service_pattern.match(line):
                start = i
        else:
            # Stop at the next sibling service key (same 2-space indent, different name)
            if next_service_pattern.match(line) and not service_pattern.match(line):
                end = i
                break

    if start is None:
        return ""
    block = lines[start:end] if end else lines[start:]
    # Strip trailing blank lines
    while block and not block[-1].strip():
        block.pop()
    return "".join(block)


def build_data():
    cfg = parse_config_file()
    namespace = cfg.get("CONTAINER_NAMESPACE", "")
    running = get_running_containers()
    local_images = get_local_images()
    enabled_services = _load_enable_service_list()
    support_services = _load_support_service_list()

    services = []
    for svc in support_services:
        container_name = f"sparrow_container_{namespace}_{svc}" if namespace else f"sparrow_container_{svc}"
        is_running = container_name in running
        images, config = parse_env_file(svc)
        compose = read_compose_file(svc)
        has_env = svc in enabled_services

        # Enrich image entries with local availability
        for img in images:
            key = img["key"]
            val = img["value"]
            # Try to detect if this is a version key and pair with name key
            img["local"] = False
            if key.endswith("_VERSION") and val:
                # e.g. IMAGE_BASIC_MYSQL_VERSION=8.0 → sparrow-basic-mysql:8.0
                m = re.match(r'^IMAGE_(BASIC|APP|OFFICIAL)_(.+)_VERSION$', key)
                if m:
                    kind = m.group(1).lower()
                    svc_name = m.group(2).lower()
                    if kind == "official":
                        # official image name comes from IMAGE_OFFICIAL_{SVC}_NAME
                        name_key = f"IMAGE_OFFICIAL_{m.group(2)}_NAME"
                        name_entry = next((e["value"] for e in images if e["key"] == name_key), svc_name)
                        repo = f"{name_entry}:{val}"
                    else:
                        repo = f"sparrow-{kind}-{svc_name}:{val}"
                    img["repo"] = repo
                    img["local"] = repo in local_images

        services.append({
            "name": svc,
            "container": container_name,
            "running": is_running,
            "hasEnv": has_env,
            "images": images,
            "config": config,
            "compose": compose,
        })

    installed = [s for s in services if s["hasEnv"]]
    running_list = [s for s in services if s["running"]]
    return {
        "namespace": namespace,
        "services": services,
        "runningCount": len(running_list),
        "installedCount": len(installed),
        "totalCount": len(services),
        "stoppedCount": len(installed) - len(running_list),
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sparrow Dashboard</title>
<style>
:root {
  --bg: #ffffff; --surface: #ffffff; --surface2: #f6f8fa;
  --border: #d0d7de; --border2: #8b949e;
  --text: #1f2328; --text2: #656d76; --text3: #9199a1;
  --green: #1a7f37; --green-bg: #dafbe1; --green-dim: #dafbe1;
  --red: #cf222e; --red-bg: #ffebe9;
  --blue: #0969da; --blue-bg: #ddf4ff;
  --yellow: #9a6700; --yellow-bg: #fff8c5;
  --purple: #8250df; --purple-bg: #fbefff;
  --radius: 8px;
  --mono: 'SF Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 14px; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
  background: var(--bg); color: var(--text); min-height: 100vh; line-height: 1.5; }

/* ── Topbar ── */
.topbar {
  background: var(--surface); border-bottom: 1px solid var(--border);
  height: 52px; padding: 0 20px; display: flex; align-items: center; gap: 12px;
  position: sticky; top: 0; z-index: 200;
  height: 90px;
}
.logo { font-size: 16px; font-weight: 600; color: var(--text); display: flex; align-items: center; gap: 8px; }
.logo-icon { font-size: 20px; }
.ns-tag { font-size: 12px; color: var(--text2); background: var(--surface2);
  border: 1px solid var(--border); padding: 2px 10px; border-radius: 20px; }
.topbar-right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
.updated { font-size: 12px; color: var(--text3); }
.btn-refresh { background: var(--surface2); border: 1px solid var(--border); color: var(--text2);
  padding: 5px 12px; border-radius: var(--radius); cursor: pointer; font-size: 13px; transition: all .15s; }
.btn-refresh:hover { border-color: var(--border2); color: var(--text); }

/* ── Layout ── */
.main { padding: 20px; max-width: 1440px; margin: 0 auto; }

/* ── Stats row ── */
.stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 16px 20px; }
.stat-label { font-size: 12px; color: var(--text2); margin-bottom: 4px; }
.stat-val { font-size: 26px; font-weight: 700; line-height: 1; }
.stat-val.green { color: var(--green); }
.stat-val.red   { color: var(--red);   }
.stat-val.blue  { color: var(--blue);  }
.stat-val.muted { color: var(--text2); }

/* ── Toolbar ── */
.toolbar { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
.search {
  background: var(--surface); border: 1px solid var(--border); color: var(--text);
  padding: 6px 12px; border-radius: var(--radius); font-size: 13px; outline: none;
  width: 260px; transition: border-color .15s;
  height: 40px;
}
.search::placeholder { color: var(--text3); }
.search:focus { border-color: var(--blue); }
.filter-tabs { display: flex; background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; height: 40px;}
.ftab { background: none; border: none; color: var(--text2); padding: 6px 14px;
  cursor: pointer; font-size: 13px; transition: all .15s; white-space: nowrap; }
.ftab.active { background: var(--surface); color: var(--text); box-shadow: inset 0 0 0 1px var(--border); border-radius: 6px; }
.ftab:hover:not(.active) { color: var(--text); }
.count-badge { font-size: 11px; color: var(--text3); margin-left: auto; }

/* ── Grid ── */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }

/* ── Service Card ── */
.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  overflow: hidden; transition: border-color .15s, box-shadow .15s;
}
.card:hover { border-color: var(--border2); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.card.is-running { border-top: 2px solid var(--green); }
.card.is-stopped { border-top: 2px solid var(--border2); }
.card.is-noenv   { opacity: .45; }

.card-head {
  padding: 12px 14px; display: flex; align-items: center; gap: 10px;
  cursor: pointer; user-select: none;
}
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 1px; }
.dot.on  { background: var(--green); box-shadow: 0 0 6px rgba(26,127,55,0.4); }
.dot.off { background: var(--border2); }
.card-name { font-size: 14px; font-weight: 600; flex: 1; color: var(--text); }
.badge {
  font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 500;
  white-space: nowrap; flex-shrink: 0;
}
.badge-run  { background: var(--green-dim); color: var(--green); }
.badge-stop { background: var(--surface2); color: var(--text2); border: 1px solid var(--border); }
.badge-none { background: var(--surface2); color: var(--text3); border: 1px solid var(--border); }
.chevron { color: var(--text3); font-size: 11px; transition: transform .2s; flex-shrink: 0; }
.card.open .chevron { transform: rotate(180deg); }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000;
  display: none; align-items: center; justify-content: center; padding: 20px;
}
.modal-overlay.show { display: flex; }
.modal {
  background: #fff; border-radius: 12px; width: 100%; max-width: 1100px;
  max-height: 85vh; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  display: flex; flex-direction: column;
}
.modal-header {
  padding: 16px 20px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px; background: var(--surface2);
}
.modal-title { font-size: 18px; font-weight: 600; flex: 1; }
.modal-close {
  background: none; border: none; color: var(--text2); font-size: 24px;
  cursor: pointer; line-height: 1; padding: 0 4px;
}
.modal-close:hover { color: var(--text); }
.modal-body {
  padding: 20px; overflow-y: auto; flex: 1;
}

/* section inside modal */
.detail-section { padding: 14px 16px; border-radius: 10px; margin-bottom: 14px; }
.detail-section:last-child { margin-bottom: 0; }
.detail-title {
  font-size: 12px; font-weight: 700; color: var(--text2);
  text-transform: uppercase; letter-spacing: .08em; margin-bottom: 10px;
}
/* colored sections */
.detail-section.images { background: var(--blue-bg); border: 1px solid rgba(9,105,218,0.2); }
.detail-section.config { background: var(--purple-bg); border: 1px solid rgba(130,80,223,0.2); }
.detail-section.compose { background: var(--surface2); border: 1px solid var(--border); }

/* image pills */
.image-list { display: flex; flex-direction: column; gap: 8px; }
.image-row { display: flex; align-items: center; gap: 10px; }
.img-kind {
  font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px;
  text-transform: uppercase; flex-shrink: 0; width: 56px; text-align: center;
}
.img-kind.basic  { background: var(--blue); color: #fff; width: 80px;}
.img-kind.app    { background: var(--purple); color: #fff; width: 80px;}
.img-kind.official { background: #9a6700; color: #fff; width: 80px;}
.img-repo {
  font-family: var(--mono); font-size: 13px; color: var(--text); flex: 1;
  word-break: break-all; overflow-wrap: anywhere;
}
.img-local { font-size: 11px; padding: 2px 8px; border-radius: 4px; flex-shrink: 0; font-weight: 600; }
.img-local.yes { background: var(--green-bg); color: var(--green); border: 1px solid rgba(26,127,55,0.3); }
.img-local.no  { background: #fff; color: var(--text3); border: 1px solid var(--border); }

/* config kv table */
.kv-wrap { overflow-x: auto; }
.kv-table { border-collapse: collapse; white-space: nowrap; font-size: 12px; width: 100%; }
.kv-table tr { background: #fff; }
.kv-table tr:hover td { background: rgba(130,80,223,0.05); }
.kv-table td { padding: 8px 12px; vertical-align: middle; border-bottom: 1px solid rgba(130,80,223,0.15); }
.kv-table tr:last-child td { border-bottom: none; }
.kv-key     { font-family: var(--mono); color: var(--purple); padding-right: 20px; font-weight: 600; }
.kv-value   { font-family: var(--mono); color: var(--text); padding-right: 16px; }
.kv-comment { color: var(--text3); font-size: 11px; }

/* action buttons */
.card-actions { display: flex; gap: 6px; padding: 8px 14px; border-top: 1px solid var(--border); background: var(--surface2); }
.act-btn {
  font-size: 12px; padding: 6px 14px; border-radius: 6px; border: 1px solid var(--border);
  cursor: pointer; font-weight: 600; transition: all .15s; background: #fff;
  color: var(--text2);
}
.act-btn:hover { color: var(--text); border-color: var(--border2); background: var(--surface2); }
.act-btn.start  { color: var(--green); border-color: rgba(26,127,55,0.4); background: var(--green-bg); }
.act-btn.start:hover  { background: rgba(26,127,55,0.2); }
.act-btn.stop   { color: var(--red); border-color: rgba(207,34,46,0.4); background: var(--red-bg); }
.act-btn.stop:hover   { background: rgba(207,34,46,0.1); }
.act-btn.restart { color: var(--yellow); border-color: rgba(154,103,0,0.4); background: var(--yellow-bg); }
.act-btn.restart:hover { background: rgba(154,103,0,0.1); }
.act-btn:disabled { opacity: .4; cursor: not-allowed; }
.act-btn.loading { opacity: .6; }

/* modal actions */
.modal-actions {
  padding: 16px 20px; border-top: 1px solid var(--border);
  display: flex; gap: 8px; background: var(--surface2);
}

/* toast */
.toast {
  position: fixed; bottom: 24px; right: 24px; background: #fff;
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 10px 16px; font-size: 13px; z-index: 999;
  display: none; max-width: 340px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.toast.show { display: block; }
.toast.ok   { border-color: var(--green); color: var(--green); }
.toast.err  { border-color: var(--red);   color: var(--red);   }

/* empty state */
.empty-row { color: var(--text3); font-size: 12px; padding: 8px 0; }
.no-results { text-align: center; padding: 60px 20px; color: var(--text3); font-size: 14px; }

/* compose block */
.compose-block {
  background: #fff; border-radius: 8px; overflow-x: auto;
  padding: 14px 16px; margin-top: 4px; border: 1px solid var(--border);
}
.compose-block pre {
  font-family: var(--mono); font-size: 12.5px; color: var(--text2);
  white-space: pre; margin: 0; line-height: 1.7;
}
/* syntax highlight classes applied by JS (light theme) */
.cy-key    { color: #0550ae; font-weight: 600; }  /* yaml key */
.cy-str    { color: #0a3069; }  /* string value */
.cy-num    { color: #9a6700; }  /* number */
.cy-bool   { color: #cf222e; }  /* true/false */
.cy-var    { color: #8250df; font-weight: 600; }  /* ${VAR} */
.cy-comment{ color: #8b949e; font-style: italic; }
</style>
</head>
<body>
<div class="topbar">
  <div class="logo"><img src="https://github.com/WGrape/sparrow/assets/35942268/ab3ef3f3-8625-41df-99ed-50edde47a68e" alt="Sparrow Dashboard" style="width: 200px;">Dashboard</div>
  <span class="ns-tag" id="ns-label">namespace: —</span>
  <div class="topbar-right">
    <span class="updated" id="updated"></span>
    <button class="btn-refresh" onclick="loadData()">⟳ 刷新</button>
  </div>
</div>

<div class="main">
  <div class="stats" id="stats"></div>

  <div class="toolbar">
    <input class="search" id="search" placeholder="搜索服务名 / 变量名 / 值..." oninput="render()">
    <div class="filter-tabs">
      <button class="ftab active" id="ftab-all"     onclick="setFilter('all')">全部</button>
      <button class="ftab"        id="ftab-running" onclick="setFilter('running')">运行中</button>
      <button class="ftab"        id="ftab-stopped" onclick="setFilter('stopped')">未运行</button>
    </div>
    <span class="count-badge" id="count-badge"></span>
    <!-- <button class="btn-refresh" id="btn-expand-all" onclick="toggleExpandAll()">展开所有</button> -->
  </div>

  <div id="grid-container"></div>
</div>

<!-- Modal overlay -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModal(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <div class="modal-header">
      <span class="dot" id="modal-dot"></span>
      <div class="modal-title" id="modal-title"></div>
      <span class="badge" id="modal-badge"></span>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
    <div class="modal-actions" id="modal-actions"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let allData = null, filter = 'all', currentModalService = null;

async function loadData() {
  try {
    const r = await fetch('/api/data');
    allData = await r.json();
    renderStats();
    render();
    document.getElementById('updated').textContent = '更新于 ' + new Date().toLocaleTimeString();
    document.getElementById('ns-label').textContent = 'namespace: ' + (allData.namespace || '(未设置)');
    // If modal is open, refresh its content
    if (currentModalService) {
      const s = allData.services.find(x => x.name === currentModalService);
      if (s) openModal(s.name);
    }
  } catch(e) {
    document.getElementById('grid-container').innerHTML =
      '<div class="no-results">⚠️ 加载失败，请确认 Docker 正在运行</div>';
  }
}

function renderStats() {
  const d = allData;
  document.getElementById('stats').innerHTML = `
    <div class="stat"><div class="stat-label">运行中</div><div class="stat-val green">${d.runningCount}</div></div>
    <div class="stat"><div class="stat-label">未运行</div><div class="stat-val red">${d.stoppedCount}</div></div>
    <div class="stat"><div class="stat-label">已启用</div><div class="stat-val blue">${d.installedCount}</div></div>
    <div class="stat"><div class="stat-label">全部服务</div><div class="stat-val muted">${d.totalCount}</div></div>
  `;
}

function setFilter(f) {
  filter = f;
  ['all','running','stopped'].forEach(id =>
    document.getElementById('ftab-' + id).classList.toggle('active', id === f));
  render();
}

function render() {
  if (!allData) return;
  const q = document.getElementById('search').value.trim().toLowerCase();
  let list = allData.services;

  if (filter === 'running') list = list.filter(s => s.running);
  else if (filter === 'stopped') list = list.filter(s => s.hasEnv && !s.running);

  if (q) {
    list = list.filter(s => {
      if (s.name.includes(q)) return true;
      const inImg = s.images.some(e => e.key.toLowerCase().includes(q) || e.value.toLowerCase().includes(q) || (e.repo||'').toLowerCase().includes(q));
      const inCfg = s.config.some(e => e.key.toLowerCase().includes(q) || e.value.toLowerCase().includes(q));
      return inImg || inCfg;
    });
  }

  document.getElementById('count-badge').textContent = list.length + ' 个服务';

  if (!list.length) {
    document.getElementById('grid-container').innerHTML = '<div class="no-results">没有匹配的服务</div>';
    return;
  }
  document.getElementById('grid-container').innerHTML =
    '<div class="grid">' + list.map(cardHTML).join('') + '</div>';
}

function cardHTML(s) {
  const state = !s.hasEnv ? 'is-noenv' : s.running ? 'is-running' : 'is-stopped';
  const dotCls = s.running ? 'on' : 'off';
  const badge = !s.hasEnv
    ? '<span class="badge badge-none">未启用</span>'
    : s.running
      ? '<span class="badge badge-run">● 运行中</span>'
      : '<span class="badge badge-stop">○ 未运行</span>';

  // action buttons (only for installed services)
  let actHtml = '';
  if (s.hasEnv) {
    const n = esc(s.name);
    if (s.running) {
      actHtml = `<div class="card-actions">
        <button class="act-btn restart" onclick="event.stopPropagation(); doAction('${n}','restart',this)">⟳ 重启</button>
        <button class="act-btn stop"    onclick="event.stopPropagation(); doAction('${n}','stopone',this)">■ 停止</button>
      </div>`;
    } else {
      actHtml = `<div class="card-actions">
        <button class="act-btn start" onclick="event.stopPropagation(); doAction('${n}','startone',this)">▶ 启动</button>
      </div>`;
    }
  }

  const hasDetail = s.images.length || s.config.length || s.compose;
  return `<div class="card ${state}" id="card-${esc(s.name)}">
    <div class="card-head" onclick="openModal('${esc(s.name)}')">
      <div class="dot ${dotCls}"></div>
      <div class="card-name">${esc(s.name)}</div>
      ${badge}
      ${hasDetail ? '<span class="chevron">›</span>' : ''}
    </div>
    ${actHtml}
  </div>`;
}

function toggleExpandAll() {
  // no-op for modal design, keep button for potential future use
}

function openModal(name) {
  const s = allData.services.find(x => x.name === name);
  if (!s) return;
  currentModalService = name;

  const dotCls = s.running ? 'on' : 'off';
  const badge = !s.hasEnv
    ? '<span class="badge badge-none">未启用</span>'
    : s.running
      ? '<span class="badge badge-run">● 运行中</span>'
      : '<span class="badge badge-stop">○ 未运行</span>';

  document.getElementById('modal-dot').className = 'dot ' + dotCls;
  document.getElementById('modal-title').textContent = s.name;
  // Replace the badge content while keeping the element with id
  const badgeEl = document.getElementById('modal-badge');
  badgeEl.outerHTML = badge.replace('<span ', '<span id="modal-badge" ');

  // Build modal body content
  let bodyHtml = '';

  // Container name section
  bodyHtml += `<div class="detail-section compose">
    <div class="detail-title">容器名</div>
    <div class="compose-block"><pre><span class="cy-key">${esc(s.container)}</span></pre></div>
  </div>`;

  // images section
  if (s.images.length) {
    const rows = s.images.filter(e => e.key.endsWith('_VERSION') && e.repo).map(e => {
      const m = e.key.match(/^IMAGE_(BASIC|APP|OFFICIAL)_/);
      const kind = m ? m[1].toLowerCase() : 'other';
      const localCls = e.local ? 'yes' : 'no';
      const localTxt = e.local ? '本地已有' : '未拉取';
      return `<div class="image-row">
        <span class="img-kind ${kind}">${kind}</span>
        <span class="img-repo" title="${esc(e.repo)}">${esc(e.repo)}</span>
        <span class="img-local ${localCls}">${localTxt}</span>
      </div>`;
    }).join('');
    if (rows) bodyHtml += `<div class="detail-section images">
      <div class="detail-title">镜像</div>
      <div class="image-list">${rows}</div>
    </div>`;
  }

  // config section
  if (s.config.length) {
    const rows = s.config.map(e => `<tr>
      <td class="kv-key" style="border-right: 1px solid #ddd;">${esc(e.key)}</td>
      <td class="kv-value" style="border-right: 1px solid #ddd;">${esc(e.value)}</td>
      <td class="kv-comment">${esc(e.comment)}</td>
    </tr>`).join('');
    bodyHtml += `<div class="detail-section config">
      <div class="detail-title">配置变量</div>
      <div class="kv-wrap"><table class="kv-table">
        <thead>
          <tr style="border-bottom: 1px solid #ddd;">
            <th style="text-align:center;width:30%;border-right: 1px solid #ddd;font-family:var(--mono);font-size:11px;color:var(--text2);padding:8px 0 8px 0;">变量名</th>
            <th style="text-align:center;width:30%;border-right: 1px solid #ddd;font-family:var(--mono);font-size:11px;color:var(--text2);padding:8px 0 8px 0;">变量值</th>
            <th style="text-align:center;font-family:var(--mono);font-size:11px;color:var(--text2);padding:8px 0 8px 0;">注释</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;
  }

  // compose section
  if (s.compose) {
    bodyHtml += `<div class="detail-section compose">
      <div class="detail-title">docker-compose.yml</div>
      <div class="compose-block"><pre>${highlightYaml(esc(s.compose))}</pre></div>
    </div>`;
  }

  if (!bodyHtml) {
    bodyHtml = '<div class="no-results">暂无详细信息</div>';
  }
  document.getElementById('modal-body').innerHTML = bodyHtml;

  // Modal actions
  let actHtml = '';
  if (s.hasEnv) {
    const n = esc(s.name);
    if (s.running) {
      actHtml = `
        <button class="act-btn restart" onclick="doAction('${n}','restart',this)">⟳ 重启</button>
        <button class="act-btn stop"    onclick="doAction('${n}','stopone',this)">■ 停止</button>
      `;
    } else {
      actHtml = `
        <button class="act-btn start" onclick="doAction('${n}','startone',this)">▶ 启动</button>
      `;
    }
    actHtml += `<button class="act-btn" onclick="doDisable('${esc(s.name)}',this)" style="border-color:#e74c3c;color:#e74c3c;">✕ 禁用</button>`;
  } else {
    actHtml += `<button class="act-btn" onclick="doEnable('${esc(s.name)}',this)" style="border-color:#27ae60;color:#27ae60;">✚ 启用</button>`;
  }
  actHtml += `<button class="act-btn" onclick="closeModal()">关闭</button>`;
  document.getElementById('modal-actions').innerHTML = actHtml;

  document.getElementById('modal-overlay').classList.add('show');
}

function closeModal(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById('modal-overlay').classList.remove('show');
  currentModalService = null;
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

let toastTimer = null;
function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + type;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 4000);
}

async function doAction(service, action, btn) {
  btn.disabled = true;
  btn.classList.add('loading');
  const origText = btn.textContent;
  btn.textContent = '执行中...';
  try {
    const r = await fetch('/api/action', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({service, action})
    });
    const d = await r.json();
    if (d.ok) {
      showToast('✓ ' + service + ' ' + action + ' 已执行', 'ok');
      setTimeout(loadData, 2000);
    } else {
      showToast('✗ ' + (d.error || '执行失败'), 'err');
    }
  } catch(e) {
    showToast('✗ 请求失败: ' + e.message, 'err');
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.textContent = origText;
  }
}

async function doDisable(service, btn) {
  if (!confirm('确定要禁用 ' + service + ' 吗？这将从 ENABLE_SERVICE_LIST 中移除该服务。')) {
    return;
  }
  btn.disabled = true;
  btn.classList.add('loading');
  const origText = btn.textContent;
  btn.textContent = '禁用中...';
  try {
    const r = await fetch('/api/disable', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({service})
    });
    const d = await r.json();
    if (d.ok) {
      showToast('✓ ' + service + ' 已禁用', 'ok');
      closeModal();
      setTimeout(loadData, 500);
    } else {
      showToast('✗ ' + (d.error || '禁用失败'), 'err');
    }
  } catch(e) {
    showToast('✗ 请求失败: ' + e.message, 'err');
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.textContent = origText;
  }
}

async function doEnable(service, btn) {
  btn.disabled = true;
  btn.classList.add('loading');
  const origText = btn.textContent;
  btn.textContent = '启用中...';
  try {
    const r = await fetch('/api/enable', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({service})
    });
    const d = await r.json();
    if (d.ok) {
      showToast('✓ ' + service + ' 已启用', 'ok');
      closeModal();
      setTimeout(loadData, 500);
    } else {
      showToast('✗ ' + (d.error || '启用失败'), 'err');
    }
  } catch(e) {
    showToast('✗ 请求失败: ' + e.message, 'err');
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.textContent = origText;
  }
}

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function highlightYaml(s) {
  return s.split('\n').map(line => {
    // comment lines
    if (/^\s*#/.test(line)) return `<span class="cy-comment">${line}</span>`;
    // key: value lines
    return line.replace(/^(\s*)([\w\-\.]+)(\s*:\s*)(.*)$/, (_, indent, key, sep, val) => {
      let valHtml = val;
      // inline comment
      let comment = '';
      const ci = val.indexOf(' #');
      if (ci !== -1) { comment = val.slice(ci); valHtml = val.slice(0, ci); }
      // ${VAR} substitution highlight
      valHtml = valHtml.replace(/(\$\{[^}]+\})/g, '<span class="cy-var">$1</span>');
      // string/num/bool color if no var spans already
      if (!valHtml.includes('cy-var')) {
        if (/^(true|false|null|~)$/.test(valHtml.trim())) valHtml = `<span class="cy-bool">${valHtml}</span>`;
        else if (/^\d/.test(valHtml.trim())) valHtml = `<span class="cy-num">${valHtml}</span>`;
        else if (valHtml.trim()) valHtml = `<span class="cy-str">${valHtml}</span>`;
      }
      const commentHtml = comment ? `<span class="cy-comment">${comment}</span>` : '';
      return `${indent}<span class="cy-key">${key}</span>${sep}${valHtml}${commentHtml}`;
    });
  }).join('\n');
}

loadData();
setInterval(loadData, 15000);
</script>
</body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access logs

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/data":
            data = json.dumps(build_data(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        elif path == "/":
            body = HTML_TEMPLATE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/action":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                req = json.loads(body)
                service = req.get("service", "").strip()
                action = req.get("action", "").strip()
                allowed_actions = {"startone", "stopone", "restart"}
                if not service or action not in allowed_actions or not re.match(r'^[a-zA-Z0-9_-]+$', service):
                    raise ValueError("invalid service or action")
                sparrow = os.path.join(BASE_PATH, "sparrow")
                label = f"[web] ./sparrow {action} {service}"
                print(f"\n{'─'*60}")
                print(f"▶  {label}")
                print(f"{'─'*60}", flush=True)
                proc = subprocess.Popen(
                    [sparrow, action, service],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, cwd=BASE_PATH
                )
                output_lines = []
                for line in proc.stdout:
                    line_stripped = line.rstrip("\n")
                    print(line_stripped, flush=True)
                    output_lines.append(line_stripped)
                proc.wait()
                ok = proc.returncode == 0
                print(f"{'─'*60}")
                print(f"{'✓' if ok else '✗'}  {label}  (exit {proc.returncode})")
                print(f"{'─'*60}\n", flush=True)
                output_text = "\n".join(output_lines[-100:])
                resp = json.dumps({
                    "ok": ok,
                    "stdout": output_text,
                    "error": "" if ok else output_lines[-1] if output_lines else "exit code " + str(proc.returncode),
                }, ensure_ascii=False).encode("utf-8")
            except Exception as e:
                resp = json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", len(resp))
            self.end_headers()
            self.wfile.write(resp)
        elif path == "/api/disable":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                req = json.loads(body)
                service = req.get("service", "").strip()
                if not service or not re.match(r'^[a-zA-Z0-9_-]+$', service):
                    raise ValueError("invalid service")

                # Update only root .env file
                root_env = os.path.join(BASE_PATH, ".env")
                if os.path.isfile(root_env):
                    with open(root_env, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    new_lines = []
                    for line in lines:
                        if line.strip().startswith("ENABLE_SERVICE_LIST="):
                            # Extract the list content
                            list_str = line.split("=", 1)[1].strip()
                            if list_str.startswith("(") and list_str.endswith(")"):
                                list_content = list_str[1:-1]
                                # Parse quoted strings
                                items = re.findall(r'"([^"]+)"', list_content)
                                # Remove the service
                                new_items = [item for item in items if item != service]
                                # Rebuild the list
                                new_list_str = "(" + " ".join(f'"{item}"' for item in new_items) + ")"
                                new_line = re.sub(r'ENABLE_SERVICE_LIST\s*=\s*\([^)]*\)', f"ENABLE_SERVICE_LIST={new_list_str}", line)
                                new_lines.append(new_line)
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)

                    with open(root_env, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)

                label = f"[web] disabled service {service}"
                print(f"\n{'─'*60}")
                print(f"✓  {label}")
                print(f"{'─'*60}\n", flush=True)
                resp = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
            except Exception as e:
                resp = json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", len(resp))
            self.end_headers()
            self.wfile.write(resp)
        elif path == "/api/enable":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                req = json.loads(body)
                service = req.get("service", "").strip()
                if not service or not re.match(r'^[a-zA-Z0-9_-]+$', service):
                    raise ValueError("invalid service")

                # Update only root .env file
                root_env = os.path.join(BASE_PATH, ".env")
                if os.path.isfile(root_env):
                    with open(root_env, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    new_lines = []
                    for line in lines:
                        if line.strip().startswith("ENABLE_SERVICE_LIST="):
                            # Extract the list content
                            list_str = line.split("=", 1)[1].strip()
                            if list_str.startswith("(") and list_str.endswith(")"):
                                list_content = list_str[1:-1]
                                # Parse quoted strings
                                items = re.findall(r'"([^"]+)"', list_content)
                                # Add the service if not already present
                                if service not in items:
                                    items.append(service)
                                # Rebuild the list
                                new_list_str = "(" + " ".join(f'"{item}"' for item in items) + ")"
                                new_line = re.sub(r'ENABLE_SERVICE_LIST\s*=\s*\([^)]*\)', f"ENABLE_SERVICE_LIST={new_list_str}", line)
                                new_lines.append(new_line)
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)

                    with open(root_env, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)

                label = f"[web] enabled service {service}"
                print(f"\n{'─'*60}")
                print(f"✓  {label}")
                print(f"{'─'*60}\n", flush=True)
                resp = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
            except Exception as e:
                resp = json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", len(resp))
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_response(404)
            self.end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7979
    url = f"http://localhost:{port}"

    server = http.server.HTTPServer(("", port), Handler)
    print(f"\n🐦  Sparrow Dashboard")
    print(f"   Local:  {url}")
    print(f"\n   Press Ctrl+C to stop\n")

    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
