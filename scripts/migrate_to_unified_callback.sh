#!/bin/bash
# 迁移到统一回调脚本

echo "🚀 开始迁移到统一回调..."

# 1. 创建备份
echo "📦 创建备份..."
./scripts/backup_callbacks.sh

# 2. 备份app.py
echo "📄 备份app.py..."
cp app.py app.py.backup

# 3. 注释掉旧回调
echo "🔧 注释掉旧回调..."
sed -i 's/register_chat_input_callbacks(app)/# register_chat_input_callbacks(app)/' app.py
sed -i 's/import callbacks.voice_chat_c/# import callbacks.voice_chat_c/' app.py

# 4. 注册新回调
echo "🆕 注册新回调..."
# 在app.py中添加新回调注册
cat >> app.py << 'EOF'

# 注册完整的统一回调
from callbacks.core_pages_c.complete_unified_callback import register_complete_unified_callback
register_complete_unified_callback(app)
EOF

echo "✅ 迁移完成！"
echo "📋 下一步："
echo "1. 启动前端服务测试功能"
echo "2. 如果出现问题，运行恢复脚本："
echo "   ./scripts/restore_callbacks.sh backup/callbacks_$(date +%Y%m%d_%H%M%S)"
