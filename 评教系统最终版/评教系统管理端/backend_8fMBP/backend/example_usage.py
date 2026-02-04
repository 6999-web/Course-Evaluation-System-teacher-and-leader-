"""
DeepSeek 自动评分系统使用示例
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.scoring_engine import ScoringEngine
from app.file_parser import FileParser
import json


def example_1_basic_scoring():
    """示例 1: 基础评分"""
    print("\n" + "=" * 60)
    print("示例 1: 基础评分 - 教案评分")
    print("=" * 60)
    
    # 初始化评分引擎
    engine = ScoringEngine(
        api_key="sk-b6ca926900534f1fa31067d49980ec56"
    )
    
    # 教案内容
    lesson_plan = """
    【教学目标】
    1. 学生能够理解二次函数的基本概念和性质
    2. 学生能够绘制二次函数的图像并分析其特征
    3. 学生能够应用二次函数解决实际问题
    
    【教学内容】
    本课程介绍二次函数的定义、标准形式、顶点形式和一般形式。通过具体例子帮助学生理解二次函数的图像特征，包括对称轴、顶点、开口方向等。
    
    【教学重点】
    - 二次函数的三种形式及其相互转化
    - 二次函数图像的性质
    - 二次函数的应用
    
    【教学难点】
    - 二次函数的配方法
    - 二次函数与一元二次方程的关系
    
    【教学方法】
    1. 讲授法：讲解二次函数的基本概念和性质
    2. 演示法：通过图像演示二次函数的性质变化
    3. 练习法：让学生通过练习掌握二次函数的应用
    4. 小组讨论法：让学生在小组中讨论和解决问题
    
    【教学评价】
    1. 课堂提问：检查学生对基本概念的理解
    2. 练习评价：通过练习题评估学生的掌握程度
    3. 作业评价：通过课后作业进一步巩固学生的学习成果
    4. 单元测试：通过单元测试全面评估学生的学习效果
    """
    
    print("\n开始评分教案...")
    result = engine.score_file("教案", lesson_plan)
    
    if result.get("success"):
        print(f"\n✓ 评分成功")
        print(f"基础分: {result.get('base_score')}")
        print(f"加分: {result.get('bonus_score')}")
        print(f"最终分: {result.get('final_score')}")
        print(f"等级: {result.get('grade')}")
        print(f"是否触发否决项: {result.get('veto_triggered')}")
        print(f"\n评分明细:")
        for detail in result.get('score_details', []):
            print(f"  - {detail.get('indicator')}: {detail.get('score')}/{detail.get('max_score')} - {detail.get('reason')}")
        print(f"\n总体评价: {result.get('summary')}")
    else:
        print(f"\n✗ 评分失败: {result.get('error')}")


def example_2_scoring_with_bonus():
    """示例 2: 带加分项的评分"""
    print("\n" + "=" * 60)
    print("示例 2: 带加分项的评分")
    print("=" * 60)
    
    engine = ScoringEngine(
        api_key="sk-b6ca926900534f1fa31067d49980ec56"
    )
    
    # 教学反思内容
    reflection = """
    【教学反思】
    
    本次课程的教学目标是让学生理解二次函数的基本概念。通过课堂观察，我发现大多数学生能够理解基本概念，但在应用方面还需要加强。
    
    【成功之处】
    1. 通过具体例子讲解，学生对二次函数的定义理解较好
    2. 使用图像演示，学生能够直观地看到函数的性质
    3. 小组讨论活动激发了学生的学习兴趣
    
    【不足之处】
    1. 部分学生在配方法上理解不够深入
    2. 应用题的讲解时间不足
    3. 没有充分考虑学生的个体差异
    
    【改进措施】
    1. 下次课程中增加配方法的练习时间
    2. 准备更多的应用题例子
    3. 根据学生的学习进度调整教学速度
    4. 为学困生提供额外的辅导
    
    【理论依据】
    根据建构主义学习理论，学生需要通过主动建构知识来学习。因此，我在课堂中设计了多个小组讨论活动，让学生在讨论中建构对二次函数的理解。
    """
    
    # 加分项
    bonus_items = [
        {"name": "获得市级教学比赛一等奖", "score": 5},
        {"name": "创新教学方法", "score": 3}
    ]
    
    print("\n开始评分教学反思...")
    print(f"加分项: {bonus_items}")
    
    result = engine.score_file("教学反思", reflection, bonus_items)
    
    if result.get("success"):
        print(f"\n✓ 评分成功")
        print(f"基础分: {result.get('base_score')}")
        print(f"加分: {result.get('bonus_score')}")
        print(f"最终分: {result.get('final_score')}")
        print(f"等级: {result.get('grade')}")
        print(f"\n加分明细:")
        for bonus in result.get('bonus_details', []):
            print(f"  - {bonus.get('name')}: +{bonus.get('score')} 分")
    else:
        print(f"\n✗ 评分失败: {result.get('error')}")


def example_3_veto_item():
    """示例 3: 触发否决项"""
    print("\n" + "=" * 60)
    print("示例 3: 触发否决项的情况")
    print("=" * 60)
    
    engine = ScoringEngine(
        api_key="sk-b6ca926900534f1fa31067d49980ec56"
    )
    
    # 包含师德失范内容的文档
    problematic_content = """
    这是一份有问题的教案。
    
    在教学中，我经常对学生进行体罚和言语侮辱，这样可以让学生更加听话。
    我认为这是有效的教学方法。
    """
    
    print("\n开始评分（包含师德失范内容）...")
    result = engine.score_file("教案", problematic_content)
    
    if result.get("success"):
        print(f"\n✓ 评分完成")
        print(f"是否触发否决项: {result.get('veto_triggered')}")
        if result.get('veto_triggered'):
            print(f"否决原因: {result.get('veto_reason')}")
            print(f"最终等级: {result.get('grade')}")
    else:
        print(f"\n✗ 评分失败: {result.get('error')}")


def example_4_file_parsing():
    """示例 4: 文件解析"""
    print("\n" + "=" * 60)
    print("示例 4: 文件解析")
    print("=" * 60)
    
    # 创建测试文件
    test_file_path = "/tmp/test_lesson_plan.txt"
    test_content = """
    【教学目标】
    1. 学生能够理解函数的基本概念
    2. 学生能够绘制函数的图像
    
    【教学内容】
    本课程介绍函数的定义和性质。
    
    【教学方法】
    1. 讲授法
    2. 演示法
    3. 练习法
    """
    
    try:
        # 创建测试文件
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"\n解析文件: {test_file_path}")
        parsed_content = FileParser.parse_file(test_file_path, "txt")
        
        print(f"✓ 文件解析成功")
        print(f"解析内容长度: {len(parsed_content)} 字符")
        print(f"解析内容预览: {parsed_content[:100]}...")
        
        # 对解析后的内容进行评分
        engine = ScoringEngine(
            api_key="sk-b6ca926900534f1fa31067d49980ec56"
        )
        
        print(f"\n对解析后的内容进行评分...")
        result = engine.score_file("教案", parsed_content)
        
        if result.get("success"):
            print(f"✓ 评分成功")
            print(f"最终分: {result.get('final_score')}")
            print(f"等级: {result.get('grade')}")
        else:
            print(f"✗ 评分失败: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ 异常: {str(e)}")
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


def example_5_batch_scoring():
    """示例 5: 批量评分"""
    print("\n" + "=" * 60)
    print("示例 5: 批量评分")
    print("=" * 60)
    
    engine = ScoringEngine(
        api_key="sk-b6ca926900534f1fa31067d49980ec56"
    )
    
    # 多份文档
    documents = [
        {
            "type": "教案",
            "content": "【教学目标】学生能够理解函数的基本概念。【教学内容】本课程介绍函数的定义。【教学方法】讲授法、演示法。【教学评价】课堂提问、练习评价。"
        },
        {
            "type": "教学反思",
            "content": "【教学反思】本次课程的教学目标是让学生理解函数的基本概念。通过课堂观察，我发现大多数学生能够理解基本概念。【成功之处】通过具体例子讲解，学生对函数的定义理解较好。【改进措施】下次课程中增加练习时间。"
        }
    ]
    
    print(f"\n开始批量评分 {len(documents)} 份文档...")
    
    results = []
    for i, doc in enumerate(documents):
        print(f"\n评分文档 {i+1}/{len(documents)}: {doc['type']}")
        result = engine.score_file(doc['type'], doc['content'])
        results.append(result)
        
        if result.get("success"):
            print(f"  ✓ 成功 - 最终分: {result.get('final_score')} - 等级: {result.get('grade')}")
        else:
            print(f"  ✗ 失败 - {result.get('error')}")
    
    # 统计结果
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n批量评分完成: {success_count}/{len(documents)} 成功")


def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DeepSeek 自动评分系统使用示例".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        # 运行示例
        example_1_basic_scoring()
        example_2_scoring_with_bonus()
        example_3_veto_item()
        example_4_file_parsing()
        example_5_batch_scoring()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
