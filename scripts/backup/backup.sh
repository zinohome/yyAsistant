#!/bin/bash
echo "💾 创建项目备份..."
BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r src/ $BACKUP_DIR/
cp -r tests/ $BACKUP_DIR/
cp -r docs/ $BACKUP_DIR/
cp app.py $BACKUP_DIR/
cp server.py $BACKUP_DIR/
cp requirements.txt $BACKUP_DIR/
echo "备份完成: $BACKUP_DIR"
