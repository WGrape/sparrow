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


def _load_service_list():
    """Dynamically read ENABLE_SERVICE_LIST from .work/config/.env.* so new services appear automatically."""
    arch = platform.machine()
    if arch in ("arm64", "aarch64"):
        cfg_file = os.path.join(BASE_PATH, ".work/config/.env.arm64")
    else:
        cfg_file = os.path.join(BASE_PATH, ".work/config/.env.amd64")
    if os.path.isfile(cfg_file):
        with open(cfg_file, "r", encoding="utf-8") as f:
            for line in f:
                line = re.sub(r'#.*', '', line).strip()
                if line.startswith("ENABLE_SERVICE_LIST="):
                    val = line.split("=", 1)[1].strip()
                    return re.findall(r'"([^"]+)"', val)
    return [
        "etcd", "etcdkeeper", "go", "jupyter", "kafka", "kafkaui",
        "mysql", "nginx", "phpfpm", "postgres", "python", "redis",
        "zookeeper", "langchain", "nodejs", "mongodb", "ssdb",
        "prometheus", "grafana", "elasticsearch", "kibana",
        "prompthub", "nacos", "difylocal", "django", "azkaban", "milvus", "sqlite",
    ]

SERVICES = _load_service_list()


def parse_config_file():
    """Read CONTAINER_NAMESPACE from root .env (falls back to .work/config/.env.*)"""
    # Try root .env first (it's the runtime-merged file)
    root_env = os.path.join(BASE_PATH, ".env")
    candidates = [root_env]
    arch = platform.machine()
    if arch in ("arm64", "aarch64"):
        candidates.append(os.path.join(BASE_PATH, ".work/config/.env.arm64"))
    else:
        candidates.append(os.path.join(BASE_PATH, ".work/config/.env.amd64"))
    result = {}
    for cfg in candidates:
        if not os.path.isfile(cfg):
            continue
        with open(cfg, "r", encoding="utf-8") as f:
            for line in f:
                line = re.sub(r'#.*', '', line).strip()
                if "=" in line:
                    k, _, v = line.partition("=")
                    result[k.strip()] = v.strip()
        if result.get("CONTAINER_NAMESPACE"):
            break
    return result


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

    services = []
    for svc in SERVICES:
        container_name = f"sparrow_container_{namespace}_{svc}" if namespace else f"sparrow_container_{svc}"
        is_running = container_name in running
        images, config = parse_env_file(svc)
        compose = read_compose_file(svc)
        has_env = bool(images or config)

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
  --bg: #0d1117; --surface: #161b22; --surface2: #21262d;
  --border: #30363d; --border2: #444c56;
  --text: #e6edf3; --text2: #8b949e; --text3: #484f58;
  --green: #3fb950; --green-bg: #0d2119; --green-dim: #1a4229;
  --red: #f85149; --red-bg: #1c0d0d;
  --blue: #58a6ff; --blue-bg: #0d1f36;
  --yellow: #e3b341; --yellow-bg: #2a1d00;
  --purple: #bc8cff;
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
}
.search::placeholder { color: var(--text3); }
.search:focus { border-color: var(--blue); }
.filter-tabs { display: flex; background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; }
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
  overflow: hidden; transition: border-color .15s;
}
.card:hover { border-color: var(--border2); }
.card.is-running { border-top: 2px solid var(--green); }
.card.is-stopped { border-top: 2px solid var(--border2); }
.card.is-noenv   { opacity: .45; }

.card-head {
  padding: 12px 14px; display: flex; align-items: center; gap: 10px;
  cursor: pointer; user-select: none;
}
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 1px; }
.dot.on  { background: var(--green); box-shadow: 0 0 6px var(--green); }
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

/* ── Expandable detail ── */
.card-body { display: none; border-top: 1px solid var(--border); }
.card.open .card-body { display: block; }

/* section inside card */
.detail-section { padding: 10px 14px; }
.detail-section + .detail-section { border-top: 1px solid var(--border); }
.detail-title {
  font-size: 11px; font-weight: 600; color: var(--text2);
  text-transform: uppercase; letter-spacing: .06em; margin-bottom: 8px;
}

/* image pills */
.image-list { display: flex; flex-direction: column; gap: 5px; }
.image-row { display: flex; align-items: center; gap: 8px; }
.img-kind {
  font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 4px;
  text-transform: uppercase; flex-shrink: 0; width: 52px; text-align: center;
}
.img-kind.basic  { background: var(--blue-bg);   color: var(--blue);   }
.img-kind.app    { background: var(--purple); color: #fff; opacity:.8; }
.img-kind.official { background: var(--yellow-bg); color: var(--yellow); }
.img-repo {
  font-family: var(--mono); font-size: 12px; color: var(--text); flex: 1;
  word-break: break-all; overflow-wrap: anywhere;
}
.img-local { font-size: 11px; padding: 1px 6px; border-radius: 4px; flex-shrink: 0; }
.img-local.yes { background: var(--green-bg); color: var(--green); }
.img-local.no  { background: var(--surface2); color: var(--text3); border: 1px solid var(--border); }

/* config kv table */
.kv-wrap { overflow-x: auto; }
.kv-table { border-collapse: collapse; white-space: nowrap; font-size: 12px; }
.kv-table tr:hover td { background: var(--surface2); }
.kv-table td { padding: 4px 10px 4px 0; vertical-align: middle; border-bottom: 1px solid var(--border); }
.kv-table tr:last-child td { border-bottom: none; }
.kv-key     { font-family: var(--mono); color: var(--blue); padding-right: 16px; }
.kv-value   { font-family: var(--mono); color: var(--text); padding-right: 12px; }
.kv-comment { color: var(--text3); font-size: 11px; }

/* action buttons */
.card-actions { display: flex; gap: 6px; padding: 8px 14px; border-top: 1px solid var(--border); background: var(--surface2); }
.act-btn {
  font-size: 12px; padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border);
  cursor: pointer; font-weight: 500; transition: all .15s; background: var(--surface);
  color: var(--text2);
}
.act-btn:hover { color: var(--text); border-color: var(--border2); }
.act-btn.start  { color: var(--green); border-color: var(--green-dim); }
.act-btn.start:hover  { background: var(--green-dim); }
.act-btn.stop   { color: var(--red);   border-color: #3a1515; }
.act-btn.stop:hover   { background: var(--red-bg); }
.act-btn.restart { color: var(--yellow); border-color: var(--yellow-bg); }
.act-btn.restart:hover { background: var(--yellow-bg); }
.act-btn:disabled { opacity: .4; cursor: not-allowed; }
.act-btn.loading { opacity: .6; }

/* toast */
.toast {
  position: fixed; bottom: 24px; right: 24px; background: var(--surface2);
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 10px 16px; font-size: 13px; z-index: 999;
  display: none; max-width: 340px;
}
.toast.show { display: block; }
.toast.ok   { border-color: var(--green); color: var(--green); }
.toast.err  { border-color: var(--red);   color: var(--red);   }

/* empty state */
.empty-row { color: var(--text3); font-size: 12px; padding: 8px 0; }
.no-results { text-align: center; padding: 60px 20px; color: var(--text3); font-size: 14px; }

/* compose block */
.compose-block {
  background: var(--bg); border-radius: 6px; overflow-x: auto;
  padding: 10px 12px; margin-top: 2px;
}
.compose-block pre {
  font-family: var(--mono); font-size: 11.5px; color: #8b949e;
  white-space: pre; margin: 0; line-height: 1.6;
}
/* syntax highlight classes applied by JS */
.cy-key    { color: #79c0ff; }  /* yaml key */
.cy-str    { color: #a5d6ff; }  /* string value */
.cy-num    { color: #f2cc60; }  /* number */
.cy-bool   { color: #ff7b72; }  /* true/false */
.cy-var    { color: #ffa657; }  /* ${VAR} */
.cy-comment{ color: #484f58; font-style: italic; }
</style>
</head>
<body>
<div class="topbar">
  <div class="logo"><span class="logo-icon">🐦</span> Sparrow Dashboard</div>
  <span class="ns-tag" id="ns-label">namespace: —</span>
  <div class="topbar-right">
    <span class="updated" id="updated"></span>
    <button class="btn-refresh" onclick="loadData()">⟳ 刷新</button>
  </div>
</div>

<div class="main">
  <div class="stats" id="stats"></div>

  <div class="toolbar">
    <input class="search" id="search" placeholder="🔍  搜索服务名 / 变量名 / 值..." oninput="render()">
    <div class="filter-tabs">
      <button class="ftab active" id="ftab-all"     onclick="setFilter('all')">全部</button>
      <button class="ftab"        id="ftab-running" onclick="setFilter('running')">运行中</button>
      <button class="ftab"        id="ftab-stopped" onclick="setFilter('stopped')">未运行</button>
    </div>
    <span class="count-badge" id="count-badge"></span>
    <button class="btn-refresh" id="btn-expand-all" onclick="toggleExpandAll()">展开所有</button>
  </div>

  <div id="grid-container"></div>
</div>
<div class="toast" id="toast"></div>

<script>
let allData = null, filter = 'all';

async function loadData() {
  try {
    const r = await fetch('/api/data');
    allData = await r.json();
    renderStats();
    render();
    document.getElementById('updated').textContent = '更新于 ' + new Date().toLocaleTimeString();
    document.getElementById('ns-label').textContent = 'namespace: ' + (allData.namespace || '(未设置)');
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
    <div class="stat"><div class="stat-label">已安装</div><div class="stat-val blue">${d.installedCount}</div></div>
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
    ? '<span class="badge badge-none">未安装</span>'
    : s.running
      ? '<span class="badge badge-run">● 运行中</span>'
      : '<span class="badge badge-stop">○ 未运行</span>';

  // images section
  let imgHtml = '';
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
    if (rows) imgHtml = `<div class="detail-section">
      <div class="detail-title">镜像</div>
      <div class="image-list">${rows}</div>
    </div>`;
  }

  // config section
  let cfgHtml = '';
  if (s.config.length) {
    const rows = s.config.map(e => `<tr>
      <td class="kv-key">${esc(e.key)}</td>
      <td class="kv-value">${esc(e.value)}</td>
      <td class="kv-comment">${esc(e.comment)}</td>
    </tr>`).join('');
    cfgHtml = `<div class="detail-section">
      <div class="detail-title">配置变量</div>
      <div class="kv-wrap"><table class="kv-table"><tbody>${rows}</tbody></table></div>
    </div>`;
  }

  // compose section
  let composeHtml = '';
  if (s.compose) {
    composeHtml = `<div class="detail-section">
      <div class="detail-title">docker-compose.yml</div>
      <div class="compose-block"><pre>${highlightYaml(esc(s.compose))}</pre></div>
    </div>`;
  }

  // action buttons (only for installed services)
  let actHtml = '';
  if (s.hasEnv) {
    const n = esc(s.name);
    if (s.running) {
      actHtml = `<div class="card-actions">
        <button class="act-btn restart" onclick="doAction('${n}','restart',this)">⟳ 重启</button>
        <button class="act-btn stop"    onclick="doAction('${n}','stopone',this)">■ 停止</button>
      </div>`;
    } else {
      actHtml = `<div class="card-actions">
        <button class="act-btn start" onclick="doAction('${n}','startone',this)">▶ 启动</button>
      </div>`;
    }
  }

  const hasDetail = imgHtml || cfgHtml || composeHtml;
  return `<div class="card ${state}" id="card-${esc(s.name)}">
    <div class="card-head" onclick="toggle('${esc(s.name)}')">
      <div class="dot ${dotCls}"></div>
      <div class="card-name">${esc(s.name)}</div>
      ${badge}
      ${hasDetail ? '<span class="chevron">▼</span>' : ''}
    </div>
    ${actHtml}
    ${hasDetail ? `<div class="card-body">${imgHtml}${cfgHtml}${composeHtml}</div>` : ''}
  </div>`;
}

function toggleExpandAll() {
  const btn = document.getElementById('btn-expand-all');
  const cards = document.querySelectorAll('.card');
  const anyOpen = [...cards].some(c => c.classList.contains('open'));
  cards.forEach(c => { if (anyOpen) c.classList.remove('open'); else c.classList.add('open'); });
  btn.textContent = anyOpen ? '展开所有' : '收起所有';
}

function toggle(name) {
  document.getElementById('card-' + name).classList.toggle('open');
}

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
