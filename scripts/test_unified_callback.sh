#!/bin/bash
# 测试统一回调脚本

echo "🧪 开始测试统一回调..."

# 1. 测试应用启动
echo "🔍 测试应用启动..."
python -c "from app import app; print('✅ 应用启动成功')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 应用启动测试通过"
else
    echo "❌ 应用启动测试失败"
    exit 1
fi

# 2. 测试回调注册
echo "🔍 测试回调注册..."
python -c "
from callbacks.core_pages_c.complete_unified_callback import register_complete_unified_callback
print('✅ 统一回调导入成功')
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 回调注册测试通过"
else
    echo "❌ 回调注册测试失败"
    exit 1
fi

# 3. 测试核心功能
echo "🔍 测试核心功能..."
python test/test_unified_callback.py
if [ $? -eq 0 ]; then
    echo "✅ 核心功能测试通过"
else
    echo "❌ 核心功能测试失败"
    exit 1
fi

echo "🎉 所有测试通过！统一回调功能正常"
echo "📋 下一步："
echo "1. 启动前端服务：python server.py"
echo "2. 在浏览器中测试文本发送和语音功能"
echo "3. 如果出现问题，运行恢复脚本"
