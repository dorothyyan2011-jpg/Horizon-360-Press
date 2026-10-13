#!/usr/bin/env bash
# Run by GitHub Actions: records the Horizon voice for new articles and prepares the website.
set -euo pipefail
pip install -q kokoro-onnx soundfile pillow pillow-heif
mkdir -p /tmp/kokoro
B=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -f /tmp/kokoro/voices-v1.0.bin ] || curl -fsSL -o /tmp/kokoro/voices-v1.0.bin "$B/voices-v1.0.bin"
[ -f /tmp/kokoro/kokoro-v1.0.int8.onnx ] || curl -fsSL -o /tmp/kokoro/kokoro-v1.0.int8.onnx "$B/kokoro-v1.0.int8.onnx"
python scripts/build.py
git config user.name "horizon-bot"
git config user.email "horizon-bot@users.noreply.github.com"
git add -A
git diff --cached --quiet || { git commit -q -m "Update site and Horizon voice recordings" && git push -q; }
rm -rf _site && mkdir _site
cp -r index.html data.json CNAME assets audio editions _site/
mkdir -p _site/photos && cp -r photos/web _site/photos/ 2>/dev/null || true
rm -f _site/editions/README.txt
