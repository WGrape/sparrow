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
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))


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


def _load_html_template():
    """Load HTML template from index.html file."""
    index_path = os.path.join(SERVER_DIR, "index.html")
    if os.path.isfile(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

HTML_TEMPLATE = _load_html_template()


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
            body = _load_html_template().encode("utf-8")
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
