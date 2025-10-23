# yyAsistant 配置系统使用指南

## 🎯 配置系统概述

yyAsistant现在使用统一的配置系统，支持环境变量覆盖，解决了所有硬编码配置问题。

## 📁 配置文件结构

```
configs/
├── app_config.py          # 统一配置类（新增）
├── base_config.py         # 基础配置（已更新）
├── database_config.py     # 数据库配置（已更新）
├── voice_config.py        # 语音配置（已更新）
└── ...                    # 其他配置文件
```

## 🔧 配置加载机制

### 1. 环境变量优先级
1. **系统环境变量** - 最高优先级
2. **.env文件** - 项目根目录下的.env文件
3. **默认值** - 代码中定义的默认值

### 2. .env文件支持
- 自动检测项目根目录下的.env文件
- 支持python-dotenv库（可选安装）
- 如果未安装python-dotenv，会显示警告但不影响功能

## 🚀 使用方法

### 1. 基本使用
```python
from configs.app_config import app_config

# 获取配置
print(app_config.APP_TITLE)
print(app_config.DATABASE_TYPE)
print(app_config.WS_URL)
```

### 2. 环境变量覆盖
```bash
# 通过环境变量覆盖配置
export APP_TITLE="我的应用"
export YYCHAT_HOST="localhost"
export DATABASE_TYPE="sqlite"

# 运行应用
python app.py
```

### 3. .env文件配置
```bash
# 复制示例文件
cp env.example .env

# 编辑.env文件
vim .env
```

## 📋 主要配置项

### 应用基础配置
- `APP_TITLE` - 应用标题
- `APP_VERSION` - 应用版本
- `APP_SECRET_KEY` - 应用密钥

### 服务器配置
- `APP_HOST` - 服务器监听地址
- `APP_PORT` - 服务器端口
- `APP_DEBUG` - 调试模式

### 数据库配置
- `DATABASE_TYPE` - 数据库类型 (sqlite/postgresql/mysql)
- `POSTGRESQL_HOST` - PostgreSQL主机
- `POSTGRESQL_PORT` - PostgreSQL端口
- `POSTGRESQL_USER` - PostgreSQL用户名
- `POSTGRESQL_PASSWORD` - PostgreSQL密码
- `POSTGRESQL_DATABASE` - PostgreSQL数据库名

### 后端服务配置
- `YYCHAT_HOST` - yychat后端主机
- `YYCHAT_PORT` - yychat后端端口
- `YYCHAT_API_KEY` - yychat API密钥

### WebSocket配置
- `WS_URL` - WebSocket连接URL
- `WS_RECONNECT_INTERVAL` - 重连间隔
- `WS_MAX_RECONNECT_ATTEMPTS` - 最大重连次数

### 测试配置
- `TEST_BASE_URL` - 测试前端URL
- `TEST_BACKEND_URL` - 测试后端URL
- `TEST_LOCALHOST_URL` - 测试本地URL

## 🔄 配置更新流程

### 1. 添加新配置项
1. 在`configs/app_config.py`中添加新配置项
2. 在`env.example`中添加示例值
3. 更新相关文档

### 2. 修改现有配置
1. 直接修改`configs/app_config.py`中的默认值
2. 更新`env.example`文件
3. 测试配置是否正常工作

## 🐳 Docker部署配置

### 1. 环境变量方式
```yaml
# docker-compose.yml
services:
  yyasistant:
    environment:
      - APP_TITLE=研翌助手
      - DATABASE_TYPE=postgresql
      - POSTGRESQL_HOST=postgres
      - YYCHAT_HOST=yychat
```

### 2. .env文件方式
```bash
# 创建.env文件
cp env.example .env

# 编辑配置
vim .env

# 启动服务
docker-compose up
```

## 🧪 测试配置

### 1. 配置加载测试
```python
from configs.app_config import app_config
print("配置加载成功")
print("应用标题:", app_config.APP_TITLE)
print("数据库类型:", app_config.DATABASE_TYPE)
```

### 2. 环境变量覆盖测试
```bash
APP_TITLE="测试应用" python3 -c "
from configs.app_config import app_config
print('应用标题:', app_config.APP_TITLE)
"
```

## 📝 注意事项

1. **向后兼容** - 现有代码无需修改，自动使用新配置
2. **类型安全** - 支持类型转换和验证
3. **环境隔离** - 开发、测试、生产环境可以有不同的配置
4. **安全性** - 敏感配置（如密码、密钥）建议使用环境变量

## 🔍 故障排除

### 1. 配置不生效
- 检查环境变量是否正确设置
- 检查.env文件是否存在且格式正确
- 检查配置项名称是否正确

### 2. 类型转换错误
- 检查数值类型配置是否正确
- 检查布尔类型配置是否为"true"/"false"

### 3. 导入错误
- 确保在项目根目录下运行
- 检查Python路径是否正确

## 🎉 优势总结

- ✅ **零硬编码** - 所有配置都支持环境变量覆盖
- ✅ **易部署** - 支持Docker等容器化部署
- ✅ **易维护** - 配置集中管理，易于修改
- ✅ **易测试** - 支持不同环境的配置隔离
- ✅ **向后兼容** - 现有功能完全不受影响
