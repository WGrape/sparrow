#!/bin/sh

# include sdk of sparrow.
. .work/include/sdk.sh

# -----------------------------------------------------------------------------
# Initialize openclaw home directory if not yet present.
#
# openclaw requires a baseline config at ~/.openclaw/openclaw.json before the
# gateway can start (without it the gateway crash-loops on "Missing config").
# We persist the home directory to the host at ./openclaw/data/openclaw_home/
# so it survives container rebuilds; this hook seeds that directory from the
# committed template the first time the service is started on a host.
#
# Subsequent starts are no-ops: existing config/state/workspace are preserved.
# To force re-initialization, delete ./openclaw/data/openclaw_home/openclaw.json
# (or the whole openclaw_home directory) and restart the service.
# -----------------------------------------------------------------------------

OPENCLAW_HOME_DIR="./openclaw/data/openclaw_home"
OPENCLAW_CONFIG_FILE="${OPENCLAW_HOME_DIR}/openclaw.json"
OPENCLAW_TEMPLATE_FILE="./openclaw/templates/openclaw.json"

if [ -f "${OPENCLAW_CONFIG_FILE}" ]; then
    print_info "openclaw config already exists at ${OPENCLAW_CONFIG_FILE}, skip init"
    return 0
fi

print_info "openclaw config not found, initializing from template..."

if [ ! -f "${OPENCLAW_TEMPLATE_FILE}" ]; then
    print_error "openclaw template missing: ${OPENCLAW_TEMPLATE_FILE}"
    return 1
fi

# Generate a fresh 32-byte hex gateway token for this deployment.
# openssl is available on macOS, most Linux distros, and the busybox images we ship.
token=$(openssl rand -hex 24 2>/dev/null)
if [ -z "${token}" ]; then
    # Fallback: read from /dev/urandom and hex-encode via od when openssl is absent.
    token=$(head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n')
fi
if [ -z "${token}" ]; then
    print_error "failed to generate gateway token (need openssl or /dev/urandom)"
    return 1
fi

mkdir -p "${OPENCLAW_HOME_DIR}"

# Render the template: substitute the token placeholder with the generated value.
sed "s/__OPENCLAW_TOKEN_PLACEHOLDER__/${token}/" "${OPENCLAW_TEMPLATE_FILE}" > "${OPENCLAW_CONFIG_FILE}"

print_info "openclaw config initialized at ${OPENCLAW_CONFIG_FILE}"
print_warn "Gateway token (save it — needed to connect from the dashboard): ${token}"
