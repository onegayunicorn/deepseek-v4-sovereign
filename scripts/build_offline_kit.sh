#!/usr/bin/env bash
# Build the Sovereign Offline Kit — bootable Debian live + full stack
# Usage: ./scripts/build_offline_kit.sh [SIZE_MB]   (default 32768 = 32 GB)
set -euo pipefail

OUT="dist/sovereign-offline-$(date +%Y%m%d).img"
SIZE_MB="${1:-32768}"
mkdir -p dist

echo "Building offline kit: $OUT (${SIZE_MB} MB)"
dd if=/dev/zero of="$OUT" bs=1M count="$SIZE_MB" status=progress
mkfs.ext4 -F "$OUT"

MNT=$(mktemp -d)
sudo mount -o loop "$OUT" "$MNT"
sudo debootstrap --arch=amd64 stable "$MNT" https://deb.debian.org/debian
sudo cp -r . "$MNT/opt/sovereign"
sudo chroot "$MNT" /bin/bash -c '
set -e
cd /opt/sovereign
apt-get update && apt-get install -y python3-pip python3-venv git
python3 -m venv /opt/sovereign/.venv
/opt/sovereign/.venv/bin/pip install --upgrade pip
/opt/sovereign/.venv/bin/pip install -r requirements.txt
/opt/sovereign/.venv/bin/pip install -e .
/opt/sovereign/.venv/bin/pip install huggingface_hub
/opt/sovereign/.venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download('mradermacher/gemma-3-12b-it-jailbreak-EN-GGUF',
allow_patterns=['*Q4_K_M.gguf'], cache_dir='/opt/sovereign/models')
" 2>&1 | tail -5
'
sudo umount "$MNT"

echo "✅ Offline kit built: $OUT"
echo "   Burn: sudo dd if=$OUT of=/dev/sdX bs=4M status=progress conv=fsync"
