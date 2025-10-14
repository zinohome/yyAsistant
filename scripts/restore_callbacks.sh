#!/bin/bash
# 回调恢复脚本

if [ -z "$1" ]; then
    echo "❌ 请指定备份目录"
    echo "用法: $0 <备份目录>"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ 备份目录不存在: $BACKUP_DIR"
    exit 1
fi

echo "🔄 开始恢复回调..."

# 恢复回调文件
echo "📁 恢复回调文件..."
rm -rf callbacks/
cp -r "$BACKUP_DIR/callbacks/" ./

# 恢复app.py
echo "📄 恢复app.py..."
cp "$BACKUP_DIR/app.py" ./

# 恢复配置文件
echo "⚙️ 恢复配置文件..."
if [ -d "$BACKUP_DIR/configs" ]; then
    rm -rf configs/
    cp -r "$BACKUP_DIR/configs/" ./
fi

if [ -d "$BACKUP_DIR/models" ]; then
    rm -rf models/
    cp -r "$BACKUP_DIR/models/" ./
fi

if [ -d "$BACKUP_DIR/utils" ]; then
    rm -rf utils/
    cp -r "$BACKUP_DIR/utils/" ./
fi

echo "✅ 恢复完成"
echo "📋 恢复信息:"
cat "$BACKUP_DIR/backup_info.txt" 2>/dev/null || echo "备份信息文件不存在"
