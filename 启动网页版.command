#!/bin/bash
cd "$(dirname "$0")"
# 网页版启动器：启动本地服务后自动打开浏览器填写页
# 不要直接在浏览器输入地址，先双击运行这个文件
PY="$HOME/.local/bin/python3.12"
[ -x "$PY" ] || PY="python3"
"$PY" -c "import docx" 2>/dev/null || "$PY" -m pip install --break-system-packages -r requirements.txt
"$PY" app_web.py
echo ""
echo "服务已退出，按回车关闭窗口"
read
