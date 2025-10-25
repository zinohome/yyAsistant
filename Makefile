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
