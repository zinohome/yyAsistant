#!/bin/bash

# yyAsistant 文件状态检查脚本
# 用于检查项目文件状态，便于测试和调整

echo "🔍 检查 yyAsistant 项目文件状态..."

# 1. 创建检查报告
REPORT_FILE="docs/refactoring/19-file-status-check.md"
mkdir -p docs/refactoring

cat > $REPORT_FILE << 'EOF'
# 项目文件状态检查报告

## 检查时间
EOF

echo "$(date)" >> $REPORT_FILE

cat >> $REPORT_FILE << 'EOF'

## 文件状态统计

### 核心文件检查
EOF

# 2. 检查核心文件
echo "📋 检查核心文件..."
echo "### 核心应用文件" >> $REPORT_FILE
echo "| 文件 | 状态 | 大小 | 最后修改 |" >> $REPORT_FILE
echo "|------|------|------|----------|" >> $REPORT_FILE

if [ -f "app.py" ]; then
    SIZE=$(du -h app.py | cut -f1)
    DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" app.py)
    echo "| app.py | ✅ 存在 | $SIZE | $DATE |" >> $REPORT_FILE
else
    echo "| app.py | ❌ 缺失 | - | - |" >> $REPORT_FILE
fi

if [ -f "server.py" ]; then
    SIZE=$(du -h server.py | cut -f1)
    DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" server.py)
    echo "| server.py | ✅ 存在 | $SIZE | $DATE |" >> $REPORT_FILE
else
    echo "| server.py | ❌ 缺失 | - | - |" >> $REPORT_FILE
fi

# 3. 检查核心管理器
echo "🔧 检查核心管理器..."
echo "" >> $REPORT_FILE
echo "### 核心管理器文件" >> $REPORT_FILE
echo "| 文件 | 状态 | 大小 | 最后修改 |" >> $REPORT_FILE
echo "|------|------|------|----------|" >> $REPORT_FILE

CORE_FILES=(
    "core/state_manager/state_manager.py"
    "core/event_manager/event_manager.py"
    "core/websocket_manager/websocket_manager.py"
    "core/timeout_manager/timeout_manager.py"
    "core/error_handler/error_handler.py"
    "core/performance_monitor/performance_monitor.py"
    "core/resource_manager/resource_manager.py"
    "core/health_checker/health_checker.py"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")
        echo "| $file | ✅ 存在 | $SIZE | $DATE |" >> $REPORT_FILE
    else
        echo "| $file | ❌ 缺失 | - | - |" >> $REPORT_FILE
    fi
done

# 4. 检查UI优化文件
echo "🎨 检查UI优化文件..."
echo "" >> $REPORT_FILE
echo "### UI优化文件" >> $REPORT_FILE
echo "| 文件 | 状态 | 大小 | 最后修改 |" >> $REPORT_FILE
echo "|------|------|------|----------|" >> $REPORT_FILE

UI_FILES=(
    "assets/js/enhanced_audio_visualizer.js"
    "assets/js/enhanced_playback_status.js"
    "assets/js/smart_error_handler.js"
    "assets/js/state_sync_manager.js"
    "assets/js/smart_state_predictor.js"
    "assets/js/adaptive_ui.js"
    "components/smart_message_actions.py"
)

for file in "${UI_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")
        echo "| $file | ✅ 存在 | $SIZE | $DATE |" >> $REPORT_FILE
    else
        echo "| $file | ❌ 缺失 | - | - |" >> $REPORT_FILE
    fi
done

# 5. 检查测试文件
echo "🧪 检查测试文件..."
echo "" >> $REPORT_FILE
echo "### 测试文件" >> $REPORT_FILE
echo "| 文件 | 状态 | 大小 | 最后修改 |" >> $REPORT_FILE
echo "|------|------|------|----------|" >> $REPORT_FILE

TEST_FILES=(
    "tests/unit/test_ui_optimization.py"
    "tests/unit/test_error_handler.py"
    "tests/unit/test_state_sync.py"
    "tests/unit/test_state_predictor.py"
    "tests/unit/test_adaptive_ui.py"
    "tests/integration/test_ui_integration.py"
    "tests/integration/test_error_recovery.py"
    "tests/e2e/test_chat_scenarios.py"
)

for file in "${TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")
        echo "| $file | ✅ 存在 | $SIZE | $DATE |" >> $REPORT_FILE
    else
        echo "| $file | ❌ 缺失 | - | - |" >> $REPORT_FILE
    fi
done

# 6. 检查配置文件
echo "⚙️ 检查配置文件..."
echo "" >> $REPORT_FILE
echo "### 配置文件" >> $REPORT_FILE
echo "| 文件 | 状态 | 大小 | 最后修改 |" >> $REPORT_FILE
echo "|------|------|------|----------|" >> $REPORT_FILE

CONFIG_FILES=(
    "config/config.py"
    "assets/js/config.js"
    "requirements.txt"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")
        echo "| $file | ✅ 存在 | $SIZE | $DATE |" >> $REPORT_FILE
    else
        echo "| $file | ❌ 缺失 | - | - |" >> $REPORT_FILE
    fi
done

# 7. 检查文档文件
echo "📚 检查文档文件..."
echo "" >> $REPORT_FILE
echo "### 文档文件" >> $REPORT_FILE
echo "| 文件 | 状态 | 大小 | 最后修改 |" >> $REPORT_FILE
echo "|------|------|------|----------|" >> $REPORT_FILE

DOC_FILES=(
    "docs/refactoring/01-project-analysis.md"
    "docs/refactoring/03-refactoring-overview.md"
    "docs/refactoring/08-implementation-plan.md"
    "docs/refactoring/09-code-migration-strategy.md"
    "docs/refactoring/11-coding-standards.md"
    "docs/refactoring/12-ui-optimization-plan.md"
    "docs/refactoring/13-ui-optimization-implementation.md"
    "docs/refactoring/14-ui-optimization-testing.md"
    "docs/refactoring/15-ui-optimization-deployment.md"
    "docs/refactoring/16-project-file-analysis.md"
    "docs/refactoring/17-file-dependency-analysis.md"
    "docs/refactoring/18-refactoring-summary.md"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")
        echo "| $file | ✅ 存在 | $SIZE | $DATE |" >> $REPORT_FILE
    else
        echo "| $file | ❌ 缺失 | - | - |" >> $REPORT_FILE
    fi
done

# 8. 检查重复和冲突文件
echo "⚠️ 检查重复和冲突文件..."
echo "" >> $REPORT_FILE
echo "### 重复和冲突文件" >> $REPORT_FILE
echo "| 文件 | 状态 | 说明 |" >> $REPORT_FILE
echo "|------|------|------|" >> $REPORT_FILE

# 检查重复文件
if [ -f "assets/js/state_manager.js" ] && [ -f "assets/js/state_manager_v2.js" ]; then
    echo "| state_manager.js + state_manager_v2.js | ⚠️ 重复 | 建议保留一个 |" >> $REPORT_FILE
fi

if [ -f "assets/js/websocket_manager_v2.js" ] && [ -f "assets/js/voice_websocket_manager.js" ]; then
    echo "| websocket_manager_v2.js + voice_websocket_manager.js | ⚠️ 重复 | 建议保留一个 |" >> $REPORT_FILE
fi

# 检查备份文件
if [ -f "app.py.backup" ]; then
    echo "| app.py.backup | 📦 备份 | 原始版本备份 |" >> $REPORT_FILE
fi

if [ -f "assets/js/audio_visualizer.js.backup" ]; then
    echo "| audio_visualizer.js.backup | 📦 备份 | 原始版本备份 |" >> $REPORT_FILE
fi

# 9. 生成统计信息
echo "📊 生成统计信息..."
echo "" >> $REPORT_FILE
echo "## 统计信息" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 统计文件数量
TOTAL_FILES=$(find . -type f -name "*.py" -o -name "*.js" -o -name "*.md" | wc -l)
echo "总文件数: $TOTAL_FILES" >> $REPORT_FILE

# 统计Python文件
PYTHON_FILES=$(find . -name "*.py" | wc -l)
echo "Python文件数: $PYTHON_FILES" >> $REPORT_FILE

# 统计JavaScript文件
JS_FILES=$(find . -name "*.js" | wc -l)
echo "JavaScript文件数: $JS_FILES" >> $REPORT_FILE

# 统计文档文件
DOC_FILES=$(find . -name "*.md" | wc -l)
echo "文档文件数: $DOC_FILES" >> $REPORT_FILE

# 统计测试文件
TEST_FILES=$(find . -name "test_*.py" | wc -l)
echo "测试文件数: $TEST_FILES" >> $REPORT_FILE

echo "✅ 文件状态检查完成！"
echo "📊 检查报告: $REPORT_FILE"
echo ""
echo "建议操作:"
echo "1. 查看检查报告了解文件状态"
echo "2. 运行清理脚本整理项目文件"
echo "3. 运行结构优化脚本优化项目结构"
echo "4. 使用Git管理版本控制"
