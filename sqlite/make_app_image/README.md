# make_app_image

Builds `sparrow-app-sqlite` on top of `sparrow-basic-sqlite`.

- Creates the data directory at `SQLITE_DATA_DIR`.
- Starts `sqlite-web` listening on `0.0.0.0:SQLITE_CONTAINER_PORT`, serving `SQLITE_DB_FILE`.
- Web UI is accessible at `http://localhost:SQLITE_HOST_PORT` on the host machine.
