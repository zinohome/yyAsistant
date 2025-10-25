#!/bin/bash

# yyAsistant 部署脚本
# 版本: 3.0.0
# 日期: 2024-10-24

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python_version() {
    log_info "检查Python版本..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_info "Python版本: $PYTHON_VERSION"
        
        # 检查版本是否在3.8-3.13之间
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) and sys.version_info < (3, 14) else 1)"; then
            log_success "Python版本符合要求 (3.8-3.13)"
        else
            log_error "Python版本不符合要求，需要3.8-3.13"
            exit 1
        fi
    else
        log_error "未找到Python3，请先安装Python 3.8-3.13"
        exit 1
    fi
}

# 检查虚拟环境
check_venv() {
    log_info "检查虚拟环境..."
    
    if [ -d ".venv" ]; then
        log_success "虚拟环境已存在"
    else
        log_info "创建虚拟环境..."
        python3 -m venv .venv
        log_success "虚拟环境创建完成"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    source .venv/bin/activate
    log_success "虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖包..."
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    log_success "依赖安装完成"
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."
    
    # 单元测试
    log_info "运行单元测试..."
    if python -m pytest tests/unit/ -v; then
        log_success "单元测试通过"
    else
        log_error "单元测试失败"
        exit 1
    fi
    
    # 集成测试
    log_info "运行集成测试..."
    if python -m pytest tests/integration/ -v; then
        log_success "集成测试通过"
    else
        log_error "集成测试失败"
        exit 1
    fi
    
    # 端到端测试
    log_info "运行端到端测试..."
    if python tests/e2e/test_chat_scenarios.py; then
        log_success "端到端测试通过"
    else
        log_error "端到端测试失败"
        exit 1
    fi
    
    # 完整系统测试
    log_info "运行完整系统测试..."
    if python tests/integration/test_complete_system.py; then
        log_success "完整系统测试通过"
    else
        log_error "完整系统测试失败"
        exit 1
    fi
    
    log_success "所有测试通过"
}

# 检查配置
check_config() {
    log_info "检查配置文件..."
    
    if [ -f "config/config.py" ]; then
        log_success "Python配置文件存在"
    else
        log_error "Python配置文件不存在"
        exit 1
    fi
    
    if [ -f "assets/js/config.js" ]; then
        log_success "JavaScript配置文件存在"
    else
        log_error "JavaScript配置文件不存在"
        exit 1
    fi
}

# 检查核心模块
check_core_modules() {
    log_info "检查核心模块..."
    
    local modules=(
        "core/state_manager/state_manager.py"
        "core/event_manager/event_manager.py"
        "core/websocket_manager/websocket_manager.py"
        "core/timeout_manager/timeout_manager.py"
        "core/error_handler/error_handler.py"
        "core/performance_monitor/performance_monitor.py"
        "core/resource_manager/resource_manager.py"
        "core/health_checker/health_checker.py"
    )
    
    for module in "${modules[@]}"; do
        if [ -f "$module" ]; then
            log_success "模块存在: $module"
        else
            log_error "模块不存在: $module"
            exit 1
        fi
    done
}

# 创建启动脚本
create_startup_script() {
    log_info "创建启动脚本..."
    
    cat > start_app.sh << 'EOF'
#!/bin/bash

# yyAsistant 启动脚本
# 版本: 3.0.0

set -e

# 激活虚拟环境
source .venv/bin/activate

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 启动应用
echo "🚀 启动yyAsistant v3.0.0..."
echo "   - 状态管理: 8个清晰状态"
echo "   - 事件驱动: 11种事件类型"
echo "   - 智能超时: 动态超时计算"
echo "   - 错误处理: 6种错误类型，自动恢复"
echo "   - 性能监控: 全面监控，指标收集"
echo "   - 资源管理: 连接池，缓存管理"
echo "   - 健康检查: 系统健康，自动检查"
echo ""

python app.py
EOF
    
    chmod +x start_app.sh
    log_success "启动脚本创建完成: start_app.sh"
}

# 创建停止脚本
create_stop_script() {
    log_info "创建停止脚本..."
    
    cat > stop_app.sh << 'EOF'
#!/bin/bash

# yyAsistant 停止脚本
# 版本: 3.0.0

echo "🛑 停止yyAsistant..."

# 查找并停止Python进程
pkill -f "python app.py" || true

echo "✅ yyAsistant已停止"
EOF
    
    chmod +x stop_app.sh
    log_success "停止脚本创建完成: stop_app.sh"
}

# 创建健康检查脚本
create_health_check_script() {
    log_info "创建健康检查脚本..."
    
    cat > health_check.sh << 'EOF'
#!/bin/bash

# yyAsistant 健康检查脚本
# 版本: 3.0.0

echo "🔍 检查yyAsistant健康状态..."

# 检查进程
if pgrep -f "python app.py" > /dev/null; then
    echo "✅ 应用进程运行中"
else
    echo "❌ 应用进程未运行"
    exit 1
fi

# 检查端口
if netstat -tuln | grep -q ":8050"; then
    echo "✅ 端口8050监听中"
else
    echo "❌ 端口8050未监听"
    exit 1
fi

# 检查日志
if [ -f "logs/app.log" ]; then
    echo "✅ 日志文件存在"
    echo "📊 最近日志:"
    tail -5 logs/app.log
else
    echo "⚠️  日志文件不存在"
fi

echo "🎉 健康检查完成"
EOF
    
    chmod +x health_check.sh
    log_success "健康检查脚本创建完成: health_check.sh"
}

# 创建监控脚本
create_monitor_script() {
    log_info "创建监控脚本..."
    
    cat > monitor.sh << 'EOF'
#!/bin/bash

# yyAsistant 监控脚本
# 版本: 3.0.0

echo "📊 yyAsistant监控信息"
echo "========================"

# 系统信息
echo "🖥️  系统信息:"
echo "   CPU使用率: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')"
echo "   内存使用率: $(top -l 1 | grep "PhysMem" | awk '{print $2}' | sed 's/M//')"
echo "   磁盘使用率: $(df -h . | tail -1 | awk '{print $5}')"
echo ""

# 应用信息
echo "🚀 应用信息:"
if pgrep -f "python app.py" > /dev/null; then
    echo "   状态: 运行中"
    echo "   进程ID: $(pgrep -f "python app.py")"
    echo "   运行时间: $(ps -o etime= -p $(pgrep -f "python app.py"))"
else
    echo "   状态: 未运行"
fi
echo ""

# 端口信息
echo "🌐 端口信息:"
if netstat -tuln | grep -q ":8050"; then
    echo "   端口8050: 监听中"
else
    echo "   端口8050: 未监听"
fi
echo ""

# 日志信息
echo "📝 日志信息:"
if [ -f "logs/app.log" ]; then
    echo "   日志文件: 存在"
    echo "   文件大小: $(ls -lh logs/app.log | awk '{print $5}')"
    echo "   最近错误:"
    grep -i error logs/app.log | tail -3 || echo "   无错误日志"
else
    echo "   日志文件: 不存在"
fi
echo ""

echo "🎉 监控信息获取完成"
EOF
    
    chmod +x monitor.sh
    log_success "监控脚本创建完成: monitor.sh"
}

# 主函数
main() {
    echo "🚀 yyAsistant v3.0.0 部署脚本"
    echo "================================"
    echo ""
    
    # 检查环境
    check_python_version
    check_venv
    activate_venv
    
    # 安装依赖
    install_dependencies
    
    # 检查配置和模块
    check_config
    check_core_modules
    
    # 运行测试
    run_tests
    
    # 创建脚本
    create_startup_script
    create_stop_script
    create_health_check_script
    create_monitor_script
    
    echo ""
    echo "🎉 部署完成！"
    echo "============="
    echo ""
    echo "📋 可用命令:"
    echo "   ./start_app.sh      - 启动应用"
    echo "   ./stop_app.sh       - 停止应用"
    echo "   ./health_check.sh   - 健康检查"
    echo "   ./monitor.sh        - 监控信息"
    echo ""
    echo "📚 文档:"
    echo "   docs/MIGRATION_GUIDE.md  - 迁移指南"
    echo "   docs/refactoring/        - 重构文档"
    echo ""
    echo "🧪 测试:"
    echo "   python tests/integration/test_complete_system.py  - 完整系统测试"
    echo "   python tests/e2e/test_chat_scenarios.py          - 端到端测试"
    echo ""
    echo "🚀 启动应用:"
    echo "   ./start_app.sh"
    echo ""
}

# 运行主函数
main "$@"
