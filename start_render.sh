#!/bin/sh
set -eu

if [ -n "${TAILSCALE_AUTHKEY:-}" ]; then
  echo "Starting tailscaled userspace networking..."
  tailscaled \
    --tun=userspace-networking \
    --socks5-server=127.0.0.1:1055 \
    --outbound-http-proxy-listen=127.0.0.1:1055 \
    --state=/tmp/tailscaled.state >/tmp/tailscaled.log 2>&1 &
  sleep 2
  tailscale up --authkey="${TAILSCALE_AUTHKEY}" --hostname="render-model3-backend" --accept-routes=false || (cat /tmp/tailscaled.log && exit 1)
  export HTTP_PROXY="http://127.0.0.1:1055"
  export HTTPS_PROXY="http://127.0.0.1:1055"
  export ALL_PROXY="http://127.0.0.1:1055"
  export NO_PROXY="127.0.0.1,localhost,.onrender.com"
  echo "Tailscale ready."
else
  echo "TAILSCALE_AUTHKEY not set; starting without tailnet."
fi

exec python -m uvicorn app.web_app:app --host 0.0.0.0 --port "${PORT:-10000}"
