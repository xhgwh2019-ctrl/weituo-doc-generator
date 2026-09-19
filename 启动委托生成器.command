#!/bin/bash
cd "$(dirname "$0")"
# 使用带 Tk 9.0 的新 Python（uv 安装的 3.12），解决系统 Python 自带 Tk 8.5 白屏问题
PY="$HOME/.local/bin/python3.12"
[ -x "$PY" ] || PY="python3"
"$PY" -c "import docx" 2>/dev/null || "$PY" -m pip install --break-system-packages -r requirements.txt
"$PY" app.py
