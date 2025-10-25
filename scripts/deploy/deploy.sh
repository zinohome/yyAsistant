#!/bin/bash
echo "🚀 部署到生产环境..."
# 备份当前版本
./scripts/backup/backup.sh
# 部署新版本
./scripts/deploy/deploy_new.sh
# 验证部署
./scripts/deploy/verify_deployment.sh
