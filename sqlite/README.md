# SQLite Service

A containerized SQLite environment with a web-based management UI powered by [sqlite-web](https://github.com/coleifer/sqlite-web).

## Quick Start

```bash
./sparrow startone sqlite
```

Then open your browser at: **http://localhost:4600**

## Configuration

Key variables in `sqlite/.env`:

| Variable | Default | Description |
|---|---|---|
| `SQLITE_HOST_PORT` | `4600` | Host port for the web UI |
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
