#!/bin/bash
# 回调备份脚本

echo "🔄 开始备份现有回调..."

# 创建备份目录
BACKUP_DIR="backup/callbacks_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份所有回调文件
echo "📁 备份回调文件..."
cp -r callbacks/ "$BACKUP_DIR/"
cp app.py "$BACKUP_DIR/"

# 备份配置文件
echo "⚙️ 备份配置文件..."
cp -r configs/ "$BACKUP_DIR/" 2>/dev/null || true
cp -r models/ "$BACKUP_DIR/" 2>/dev/null || true
cp -r utils/ "$BACKUP_DIR/" 2>/dev/null || true

# 创建备份信息文件
cat > "$BACKUP_DIR/backup_info.txt" << EOF
备份时间: $(date)
备份原因: 回调迁移前备份
备份内容: 所有回调文件和配置文件
恢复命令: ./scripts/restore_callbacks.sh $BACKUP_DIR
EOF

echo "✅ 备份完成: $BACKUP_DIR"
echo "📋 备份信息:"
cat "$BACKUP_DIR/backup_info.txt"
