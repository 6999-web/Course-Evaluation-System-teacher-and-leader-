"""
DeepSeek API 集成测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.deepseek_client import DeepseekAPIClient
from app.scoring_engine import ScoringEngine
from app.file_parser import FileParser
import json


def test_deepseek_api():
    """测试 DeepSeek API 连接"""
    print("=" * 60)
    print("测试 DeepSeek API 连接")
    print("=" * 60)
    
    api_key = "sk-b6ca926900534f1fa31067d49980ec56"
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    client = DeepseekAPIClient(api_key, api_url)
    
    # 测试简单提示
    test_prompt = "请用一句话介绍你自己"
    
    try:
        print(f"\n发送测试提示: {test_prompt}")
        response = client.call_api(test_prompt)
        
        if response.get("success"):
            print(f"✓ API 连接成功")
            print(f"响应内容: {response.get('content')[:100]}...")
            return True
        else:
            print(f"✗ API 调用失败: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ API 调用异常: {str(e)}")
        return False


def test_scoring_engine():
    """测试评分引擎"""
    print("\n" + "=" * 60)
    print("测试评分引擎")
    print("=" * 60)
    
    api_key = "sk-b6ca926900534f1fa31067d49980ec56"
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    engine = ScoringEngine(api_key, api_url)
    
    # 测试教案评分
    test_content = """
    教学目标：
    1. 学生能够理解二次函数的基本概念
    2. 学生能够绘制二次函数的图像
    3. 学生能够应用二次函数解决实际问题
    
    教学内容：
    本课程介绍二次函数的定义、性质和应用。通过具体例子帮助学生理解二次函数的图像特征。
    
    教学方法：
    1. 讲授法：讲解二次函数的基本概念
    2. 演示法：通过图像演示二次函数的性质
    3. 练习法：让学生通过练习掌握二次函数的应用
    
    教学评价：
    1. 课堂提问：检查学生对基本概念的理解
    2. 练习评价：通过练习题评估学生的掌握程度
    3. 作业评价：通过课后作业进一步巩固学生的学习成果
    """
    
    try:
        print(f"\n开始评分教案...")
        result = engine.score_file("教案", test_content)
        
        if result.get("success"):
            print(f"✓ 评分成功")
            print(f"基础分: {result.get('base_score')}")
            print(f"最终分: {result.get('final_score')}")
            print(f"等级: {result.get('grade')}")
            print(f"是否触发否决项: {result.get('veto_triggered')}")
            if result.get('veto_triggered'):
                print(f"否决原因: {result.get('veto_reason')}")
            print(f"总体评价: {result.get('summary')[:100]}...")
            return True
        else:
            print(f"✗ 评分失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ 评分异常: {str(e)}")
        return False


def test_file_parser():
    """测试文件解析器"""
    print("\n" + "=" * 60)
    print("测试文件解析器")
    print("=" * 60)
    
    # 创建测试文件
    test_file_path = "/tmp/test_document.txt"
    test_content = "这是一份测试文档。\n包含多行内容。\n用于测试文件解析功能。"
    
    try:
        # 创建测试文件
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"\n解析测试文件: {test_file_path}")
        parsed_content = FileParser.parse_file(test_file_path, "txt")
        
        if parsed_content == test_content:
            print(f"✓ 文件解析成功")
            print(f"解析内容: {parsed_content}")
            return True
        else:
            print(f"✗ 解析内容不匹配")
            return False
            
    except Exception as e:
        print(f"✗ 文件解析异常: {str(e)}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DeepSeek 自动评分系统集成测试".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = []
    
    # 测试 API 连接
    results.append(("API 连接测试", test_deepseek_api()))
    
    # 测试文件解析
    results.append(("文件解析测试", test_file_parser()))
    
    # 测试评分引擎
    results.append(("评分引擎测试", test_scoring_engine()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    # 计算总体结果
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print(f"\n总计: {passed_tests}/{total_tests} 个测试通过")
    
    if passed_tests == total_tests:
        print("\n✓ 所有测试通过！系统已准备就绪。")
        return 0
    else:
        print(f"\n✗ 有 {total_tests - passed_tests} 个测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
