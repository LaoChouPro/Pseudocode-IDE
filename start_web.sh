#!/bin/bash
# 启动Web服务器

echo "======================================"
echo "A-level CS 伪代码解释器 Web版"
echo "======================================"
echo

# 检查依赖
echo "检查依赖..."
pip3 show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "安装依赖..."
    pip3 install -r requirements.txt
fi

echo
echo "启动Web服务器..."
echo

# 启动服务器
python3 web_server.py
