#!/bin/bash

# yyAsistant 项目结构优化脚本
# 用于优化项目结构，便于开发和测试

echo "🔧 开始优化 yyAsistant 项目结构..."

# 1. 创建标准目录结构
echo "📁 创建标准目录结构..."
mkdir -p src/core
mkdir -p src/components
mkdir -p src/views
mkdir -p src/assets/js
mkdir -p src/assets/css
mkdir -p src/config
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/e2e
mkdir -p tests/performance
mkdir -p docs/api
mkdir -p docs/user
mkdir -p scripts/deploy
mkdir -p scripts/test
mkdir -p scripts/backup

# 2. 移动核心文件到src目录
echo "📦 移动核心文件..."
if [ -d "core" ]; then
    cp -r core/* src/core/
    echo "  - 移动核心管理器到 src/core/"
fi

if [ -d "components" ]; then
    cp -r components/* src/components/
    echo "  - 移动组件到 src/components/"
fi

if [ -d "views" ]; then
    cp -r views/* src/views/
    echo "  - 移动视图到 src/views/"
fi

if [ -d "assets" ]; then
    cp -r assets/* src/assets/
    echo "  - 移动资源文件到 src/assets/"
fi

if [ -d "config" ]; then
    cp -r config/* src/config/
    echo "  - 移动配置文件到 src/config/"
fi

# 3. 移动测试文件
echo "🧪 移动测试文件..."
if [ -d "tests" ]; then
    cp -r tests/* tests/
    echo "  - 测试文件已整理"
fi

# 4. 创建开发环境配置
echo "⚙️ 创建开发环境配置..."
cat > .env.development << EOF
# 开发环境配置
DEBUG=True
LOG_LEVEL=DEBUG
TEST_MODE=True
UI_OPTIMIZATION=True
PERFORMANCE_MONITORING=True
EOF

cat > .env.production << EOF
# 生产环境配置
DEBUG=False
LOG_LEVEL=INFO
TEST_MODE=False
UI_OPTIMIZATION=True
PERFORMANCE_MONITORING=True
EOF

# 5. 创建开发脚本
echo "🛠️ 创建开发脚本..."
cat > scripts/dev/start_dev.sh << 'EOF'
#!/bin/bash
echo "🚀 启动开发环境..."
source .venv/bin/activate
export FLASK_ENV=development
python app.py
EOF

cat > scripts/dev/run_tests.sh << 'EOF'
#!/bin/bash
echo "🧪 运行测试..."
source .venv/bin/activate
python -m pytest tests/ -v --cov=src
EOF

cat > scripts/dev/check_code.sh << 'EOF'
#!/bin/bash
echo "🔍 检查代码质量..."
source .venv/bin/activate
python -m flake8 src/
python -m black --check src/
python -m isort --check-only src/
EOF

# 6. 创建部署脚本
echo "🚀 创建部署脚本..."
cat > scripts/deploy/deploy.sh << 'EOF'
#!/bin/bash
echo "🚀 部署到生产环境..."
# 备份当前版本
./scripts/backup/backup.sh
# 部署新版本
./scripts/deploy/deploy_new.sh
# 验证部署
./scripts/deploy/verify_deployment.sh
EOF

# 7. 创建备份脚本
echo "💾 创建备份脚本..."
cat > scripts/backup/backup.sh << 'EOF'
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
EOF

# 8. 创建项目配置文件
echo "📋 创建项目配置文件..."
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "yyasistant"
version = "2.0.0"
description = "AI Assistant with Advanced UI Optimization"
authors = [{name = "yyAsistant Team"}]
dependencies = [
    "dash>=2.14.0",
    "flask>=2.3.0",
    "websockets>=11.0.0",
    "psutil>=5.9.0",
]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
EOF

# 9. 创建Makefile
echo "🔨 创建Makefile..."
cat > Makefile << 'EOF'
.PHONY: help install dev test clean deploy backup

help: ## 显示帮助信息
	@echo "yyAsistant 项目管理命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install -r requirements.txt
	pip install -e .

dev: ## 启动开发环境
	./scripts/dev/start_dev.sh

test: ## 运行测试
	python -m pytest tests/ -v

test-coverage: ## 运行测试并生成覆盖率报告
	python -m pytest tests/ --cov=src --cov-report=html

clean: ## 清理项目
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".DS_Store" -delete

backup: ## 创建备份
	./scripts/backup/backup.sh

deploy: ## 部署到生产环境
	./scripts/deploy/deploy.sh

check: ## 检查代码质量
	./scripts/dev/check_code.sh
EOF

echo "✅ 项目结构优化完成！"
echo "📁 新的项目结构已创建"
echo "🛠️ 开发脚本已创建"
echo "📋 配置文件已创建"
echo ""
echo "使用方法:"
echo "  make help     - 显示所有命令"
echo "  make install  - 安装依赖"
echo "  make dev      - 启动开发环境"
echo "  make test     - 运行测试"
echo "  make backup   - 创建备份"
