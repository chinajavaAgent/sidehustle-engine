#!/bin/bash

echo "🚀 启动副业有道内容引擎..."

# 检查是否安装了依赖
if [ ! -d "backend/venv" ]; then
    echo "📦 创建Python虚拟环境..."
    cd backend && python3 -m venv venv && cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend && npm install && cd ..
fi

echo "🔧 启动后端服务..."
cd backend
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python main.py &
BACKEND_PID=$!
cd ..

echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 服务启动完成！"
echo "📱 前端地址: http://localhost:3000"
echo "🔌 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获中断信号，停止所有服务
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT

# 等待
wait