#!/bin/bash

# yyAsistant 项目文件清理脚本
# 用于清理项目文件，便于测试和调整

echo "🧹 开始清理 yyAsistant 项目文件..."

# 1. 创建清理目录
echo "📁 创建清理目录..."
mkdir -p cleanup/backup_files
mkdir -p cleanup/unused_files
mkdir -p cleanup/duplicate_files
mkdir -p cleanup/test_files

# 2. 备份重要文件
echo "💾 备份重要文件..."
cp app.py cleanup/backup_files/
cp server.py cleanup/backup_files/
cp -r core/ cleanup/backup_files/
cp -r components/ cleanup/backup_files/
cp -r views/ cleanup/backup_files/
cp -r assets/ cleanup/backup_files/
cp -r tests/ cleanup/backup_files/
cp -r docs/ cleanup/backup_files/

# 3. 移动暂时禁用的文件
echo "📦 移动暂时禁用的文件..."
if [ -f "assets/js/state_manager_v2.js" ]; then
    mv assets/js/state_manager_v2.js cleanup/unused_files/
    echo "  - 移动 state_manager_v2.js"
fi

if [ -f "assets/js/websocket_manager_v2.js" ]; then
    mv assets/js/websocket_manager_v2.js cleanup/unused_files/
    echo "  - 移动 websocket_manager_v2.js"
fi

if [ -f "callbacks/core_pages_c/chat_input_area_v2_c.py" ]; then
    mv callbacks/core_pages_c/chat_input_area_v2_c.py cleanup/unused_files/
    echo "  - 移动 chat_input_area_v2_c.py"
fi

if [ -f "callbacks/core_pages_c/chat_input_area_v3_c.py" ]; then
    mv callbacks/core_pages_c/chat_input_area_v3_c.py cleanup/unused_files/
    echo "  - 移动 chat_input_area_v3_c.py"
fi

# 4. 移动已废弃的文件
echo "🗑️ 移动已废弃的文件..."
if [ -f "assets/js/unified_button_state_manager.js" ]; then
    mv assets/js/unified_button_state_manager.js cleanup/unused_files/
    echo "  - 移动 unified_button_state_manager.js"
fi

if [ -f "assets/js/audio_visualizer.js.backup" ]; then
    mv assets/js/audio_visualizer.js.backup cleanup/unused_files/
    echo "  - 移动 audio_visualizer.js.backup"
fi

# 5. 移动测试相关文件到测试目录
echo "🧪 整理测试文件..."
if [ -f "test_ui_optimization.html" ]; then
    mv test_ui_optimization.html cleanup/test_files/
    echo "  - 移动 test_ui_optimization.html"
fi

if [ -f "test_audio_visualizer.html" ]; then
    mv test_audio_visualizer.html cleanup/test_files/
    echo "  - 移动 test_audio_visualizer.html"
fi

if [ -f "verify_ui_optimization.py" ]; then
    mv verify_ui_optimization.py cleanup/test_files/
    echo "  - 移动 verify_ui_optimization.py"
fi

# 6. 移动文档文件到docs目录
echo "📚 整理文档文件..."
if [ -f "UI_OPTIMIZATION_COMPLETE.md" ]; then
    mv UI_OPTIMIZATION_COMPLETE.md docs/
    echo "  - 移动 UI_OPTIMIZATION_COMPLETE.md"
fi

# 7. 清理临时文件
echo "🧽 清理临时文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".DS_Store" -delete
find . -name "*.log" -delete

# 8. 创建清理报告
echo "📊 生成清理报告..."
cat > cleanup/cleanup_report.md << EOF
# 项目清理报告

## 清理时间
$(date)

## 清理内容

### 移动的文件
- 暂时禁用的文件: 4个
- 已废弃的文件: 2个
- 测试文件: 3个
- 文档文件: 1个

### 清理的临时文件
- Python缓存文件
- 系统临时文件
- 日志文件

## 清理后的项目结构
- 核心文件: 保持原位置
- 测试文件: 移动到 cleanup/test_files/
- 废弃文件: 移动到 cleanup/unused_files/
- 备份文件: 移动到 cleanup/backup_files/

## 建议
1. 定期运行此脚本保持项目整洁
2. 在删除任何文件前先备份
3. 使用Git管理版本控制
EOF

echo "✅ 项目清理完成！"
echo "📁 清理文件位置: cleanup/"
echo "📊 清理报告: cleanup/cleanup_report.md"
