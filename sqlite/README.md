# SQLite Service

<sub>[English](./README.md) / [中文](./README.zh-CN.md)</sub>

A containerized SQLite environment with a web-based management UI powered by [sqlite-web](https://github.com/coleifer/sqlite-web), plus the standard `sqlite3` command line.

## Quick Start

```bash
./sparrow startone sqlite
```

Then open your browser at: **http://localhost:4700**

## Configuration

Key variables in `sqlite/.env`:

| Variable | Default | Description |
|---|---|---|
| `SQLITE_HOST_PORT` | `4700` | Host port for the web UI |
| `SQLITE_CONTAINER_PORT` | `8080` | Container port for sqlite-web |
| `SQLITE_DATA_DIR` | `/var/data/sqlite` | Path inside container for DB files |
| `SQLITE_DB_FILE` | `sparrow.db` | Default database file name |

## Data Persistence

Database files are stored in `./sqlite/data/` on the host, mounted to `/var/data/sqlite/` in the container.

## Web UI Features

- Browse tables and rows
- Execute SQL queries
- Import / export data
- Create / drop tables

## Why is the official image `python` and not `sqlite`?

This is the most confusing thing about this service. These two lines in `sqlite/.env`—

```env
IMAGE_OFFICIAL_SQLITE_NAME=python
IMAGE_OFFICIAL_SQLITE_VERSION=3.11-slim
```

—are not a misconfiguration; they are an intentional design forced by the nature of SQLite. The rest of this section walks through the chain of reasoning.

### (1) SQLite has no "server process", so it cannot be a daemon container on its own

Most databases (MySQL, Redis, Postgres, …) follow a **client/server architecture**: a long-running server process listens on a port, and clients connect over the network. That maps naturally onto containers — put the server process in the container, expose its port, done.

**SQLite is not that kind of thing.** SQLite is an **embedded C library** (`libsqlite3`). It has no server process, listens on no port, and accepts no network connections. There are exactly two ways to use SQLite:

- An application links `libsqlite3` (statically or dynamically) and reads/writes the database file directly as a local file;
- The `sqlite3` command-line tool opens a `.db` file for interactive use.

So **packaging "sqlite" itself as a long-running container is meaningless** — there is no process to keep running in the foreground, the container would exit immediately on start.

### (2) Then what does this container actually run?

It runs **`sqlite_web`** — a SQLite **web admin UI** written in Python (think phpMyAdmin, but for SQLite). The last line of `make_app_image/Dockerfile` makes this obvious:

```dockerfile
CMD sh -c "sqlite_web --host 0.0.0.0 --port ${SQLITE_CONTAINER_PORT} --no-browser ${SQLITE_DATA_DIR}/${SQLITE_DB_FILE}"
```

The long-lived process inside the container is the `sqlite_web` Python web server. Internally it uses `libsqlite3` to read/write `sparrow.db` and serves the contents over HTTP for your browser. **That** is what justifies having a container at all.

### (3) Why `python:3.11-slim` as the official image?

Because `sqlite_web` is installed via **`pip install sqlite-web`**, the base image needs a Python runtime. Rather than building a Python environment from scratch, we reuse Docker Hub's official `python:3.11-slim` — the cleanest, smallest option.

The `-slim` tag means a stripped-down build (~50MB) that ships only the Python runtime and pip, no build toolchain — enough for `sqlite_web`.

### (4) Then where does the `sqlite3` command come from?

`python:3.11-slim` does **not** ship the `sqlite3` command-line tool (it only ships the standard library's `sqlite3` Python module). So we install it ourselves in `make_basic_image/Dockerfile`:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir sqlite-web
```

Two steps:

1. `apt install sqlite3` — installs the SQLite CLI, so after `./sparrow enter sqlite` you can run `sqlite3 sparrow.db` to get an interactive shell.
2. `pip install sqlite-web` — installs the web admin UI.

After that, the basic image carries: Python runtime + `sqlite3` CLI + the `sqlite_web` package. The app image then layers on `EXPOSE`, `CMD`, and directory init.

### (5) The full build chain

```
docker.io/python:3.11-slim          ← official image (Python runtime)
        │
        │  apt install sqlite3 + pip install sqlite-web
        ▼
sparrow-basic-sqlite:3.11           ← basic image
        │
        │  EXPOSE + CMD sqlite_web ...
        ▼
sparrow-app-sqlite:latest           ← app image
        │
        │  docker compose up
        ▼
sparrow_container_test_sqlite       ← running container
   ├── background process: sqlite_web   ← browser reaches it via localhost:4700
   └── CLI tool: sqlite3                ← available after ./sparrow enter sqlite
```

## Using the SQLite CLI

The `sqlite3` command is preinstalled in the container. Three ways to use it:

### Option 1: enter the container (most common)

```bash
./sparrow enter sqlite
sqlite3 /var/data/sqlite/sparrow.db
sqlite> .tables
sqlite> CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
sqlite> SELECT * FROM users;
sqlite> .quit
```

### Option 2: one-liner from the host

```bash
# Single SQL
docker exec sparrow_container_test_sqlite \
    sqlite3 /var/data/sqlite/sparrow.db "SELECT name FROM sqlite_master WHERE type='table';"

# Interactive
docker exec -it sparrow_container_test_sqlite \
    sqlite3 /var/data/sqlite/sparrow.db
```

### Option 3: open the db file directly on the host (macOS ships sqlite3)

Because `./sqlite/data/` is mounted to the container's `/var/data/sqlite/`, the db file lives on the host:

```bash
sqlite3 ./sqlite/data/sparrow.db
```

⚠️ **Note**: don't use Option 3 while writing through `sqlite_web` in the container at the same time. SQLite uses file-level locking; concurrent writers will conflict. Read-only access is fine.
