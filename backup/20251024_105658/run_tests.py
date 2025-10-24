#!/usr/bin/env python3
"""
测试执行脚本
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


def run_command(command, description=""):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"执行时间: {end_time - start_time:.2f}秒")
    print(f"返回码: {result.returncode}")
    
    if result.stdout:
        print("标准输出:")
        print(result.stdout)
    
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    return result.returncode == 0


def check_environment():
    """检查测试环境"""
    print("检查测试环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"错误: Python版本过低 ({python_version.major}.{python_version.minor})，需要3.8+")
        return False
    
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查pytest
    try:
        import pytest
        print(f"pytest版本: {pytest.__version__}")
    except ImportError:
        print("错误: 未安装pytest")
        return False
    
    # 检查测试目录
    test_dir = Path("tests")
    if not test_dir.exists():
        print("错误: tests目录不存在")
        return False
    
    print("测试环境检查通过")
    return True


def install_test_dependencies():
    """安装测试依赖"""
    print("安装测试依赖...")
    
    test_requirements = Path("tests/requirements-test.txt")
    if test_requirements.exists():
        return run_command(
            f"pip install -r {test_requirements}",
            "安装测试依赖"
        )
    else:
        print("警告: tests/requirements-test.txt不存在，跳过依赖安装")
        return True


def run_unit_tests():
    """运行单元测试"""
    return run_command(
        "pytest tests/unit/ -v --tb=short",
        "运行单元测试"
    )


def run_integration_tests():
    """运行集成测试"""
    return run_command(
        "pytest tests/integration/ -v --tb=short",
        "运行集成测试"
    )


def run_e2e_tests():
    """运行端到端测试"""
    return run_command(
        "pytest tests/e2e/ -v --tb=short",
        "运行端到端测试"
    )


def run_performance_tests():
    """运行性能测试"""
    return run_command(
        "pytest tests/performance/ -v --tb=short",
        "运行性能测试"
    )


def run_all_tests():
    """运行所有测试"""
    return run_command(
        "pytest tests/ -v --tb=short",
        "运行所有测试"
    )


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    return run_command(
        "pytest tests/ --cov=. --cov-report=html --cov-report=term-missing",
        "运行测试并生成覆盖率报告"
    )


def run_specific_test(test_path):
    """运行特定测试"""
    return run_command(
        f"pytest {test_path} -v --tb=short",
        f"运行特定测试: {test_path}"
    )


def run_tests_by_marker(marker):
    """按标记运行测试"""
    return run_command(
        f"pytest -m {marker} -v --tb=short",
        f"运行标记为 {marker} 的测试"
    )


def generate_test_report():
    """生成测试报告"""
    return run_command(
        "pytest tests/ --html=test_report.html --self-contained-html",
        "生成HTML测试报告"
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="YYAssistant测试执行脚本")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "e2e", "performance", "all"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--report", 
        action="store_true",
        help="生成HTML测试报告"
    )
    parser.add_argument(
        "--test", 
        type=str,
        help="运行特定测试文件或函数"
    )
    parser.add_argument(
        "--marker", 
        type=str,
        help="按标记运行测试"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="安装测试依赖"
    )
    parser.add_argument(
        "--check-env", 
        action="store_true",
        help="检查测试环境"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="并行运行测试"
    )
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ["TESTING"] = "true"
    os.environ["FLASK_ENV"] = "testing"
    
    print("YYAssistant 测试执行脚本")
    print("=" * 60)
    
    # 检查环境
    if args.check_env or args.install_deps:
        if not check_environment():
            sys.exit(1)
    
    # 安装依赖
    if args.install_deps:
        if not install_test_dependencies():
            sys.exit(1)
    
    # 构建pytest命令
    pytest_cmd = "pytest"
    if args.parallel:
        pytest_cmd += " -n auto"
    
    success = True
    
    # 运行测试
    if args.test:
        success = run_specific_test(args.test)
    elif args.marker:
        success = run_tests_by_marker(args.marker)
    elif args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "e2e":
        success = run_e2e_tests()
    elif args.type == "performance":
        success = run_performance_tests()
    elif args.type == "all":
        if args.coverage:
            success = run_tests_with_coverage()
        else:
            success = run_all_tests()
    
    # 生成报告
    if args.report and success:
        generate_test_report()
    
    # 输出结果
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试执行成功")
        if args.coverage:
            print("📊 覆盖率报告已生成: htmlcov/index.html")
        if args.report:
            print("📋 测试报告已生成: test_report.html")
    else:
        print("❌ 测试执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
