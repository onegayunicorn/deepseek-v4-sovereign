#!/data/data/com.termux/files/usr/bin/bash
# One-line installer — Android (Termux, no root)
set -euo pipefail

pkg update -y && pkg upgrade -y
pkg install -y python git rust binutils libopenblas libzmq
pip install --upgrade pip
pip install numpy scipy pyyaml fastapi uvicorn websockets rich

cd ~
[ -d sovereign ] || git clone https://github.com/onegayunicorn/deepseek-v4-sovereign.git sovereign
cd sovereign
pip install --no-build-isolation -e .

cat > ~/../usr/bin/sovereign <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/sovereign && exec python -m sovereign.main "$@"
EOF
chmod +x ~/../usr/bin/sovereign

echo "✅ Sovereign Termux install done. Run: sovereign dashboard"
