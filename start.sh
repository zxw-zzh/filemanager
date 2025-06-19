#!/bin/bash
# Linux自启动脚本
cd "$(dirname "$0")"

# 如果有虚拟环境则激活
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

python3 app.py 