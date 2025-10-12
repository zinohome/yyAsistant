#!/usr/bin/env python3
"""
测试运行脚本
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def setup_test_environment():
    """设置测试环境"""
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 设置环境变量
    os.environ['TESTING'] = 'true'
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'


def run_unit_tests(verbose=False, coverage=False):
    """运行单元测试"""
    cmd = ["python", "-m", "pytest", "tests/unit/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_integration_tests(verbose=False, coverage=False):
    """运行集成测试"""
    cmd = ["python", "-m", "pytest", "tests/integration/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_e2e_tests(verbose=False, headless=True):
    """运行端到端测试"""
    cmd = ["python", "-m", "pytest", "tests/e2e/"]
    
    if verbose:
        cmd.append("-v")
    
    if not headless:
        cmd.append("--headless=false")
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_performance_tests(verbose=False):
    """运行性能测试"""
    cmd = ["python", "-m", "pytest", "tests/performance/"]
    
    if verbose:
        cmd.append("-v")
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_all_tests(verbose=False, coverage=False, headless=True):
    """运行所有测试"""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    if not headless:
        cmd.append("--headless=false")
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def install_test_dependencies():
    """安装测试依赖"""
    requirements_file = Path(__file__).parent / "requirements-test.txt"
    
    if requirements_file.exists():
        cmd = ["pip", "install", "-r", str(requirements_file)]
        return subprocess.run(cmd)
    else:
        print("测试依赖文件不存在: requirements-test.txt")
        return subprocess.CompletedProcess([], 1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行YYAssistant测试套件")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "performance", "all"], 
                       default="all", help="测试类型")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--coverage", "-c", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--headless", action="store_true", default=True, 
                       help="端到端测试使用无头浏览器")
    parser.add_argument("--install-deps", action="store_true", help="安装测试依赖")
    
    args = parser.parse_args()
    
    # 设置测试环境
    setup_test_environment()
    
    # 安装依赖
    if args.install_deps:
        print("安装测试依赖...")
        result = install_test_dependencies()
        if result.returncode != 0:
            print("依赖安装失败")
            return result.returncode
    
    # 运行测试
    if args.type == "unit":
        result = run_unit_tests(args.verbose, args.coverage)
    elif args.type == "integration":
        result = run_integration_tests(args.verbose, args.coverage)
    elif args.type == "e2e":
        result = run_e2e_tests(args.verbose, args.headless)
    elif args.type == "performance":
        result = run_performance_tests(args.verbose)
    elif args.type == "all":
        result = run_all_tests(args.verbose, args.coverage, args.headless)
    else:
        print(f"未知的测试类型: {args.type}")
        return 1
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
