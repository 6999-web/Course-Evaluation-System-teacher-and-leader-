"""
测试结构化评分反馈格式
验证AI评分返回的summary字段是否按照结构化格式输出
"""

import sys
import os

# 添加backend路径到sys.path
backend_path = os.path.join(os.path.dirname(__file__), '评教系统最终版', '评教系统管理端', 'backend_8fMBP', 'backend')
sys.path.insert(0, backend_path)

from app.scoring_engine import ScoringEngine

# DeepSeek API配置
API_KEY = "sk-b6ca926900534f1fa31067d49980ec56"

def test_structured_feedback():
    """测试结构化反馈格式"""
    
    print("=" * 80)
    print("测试结构化评分反馈格式")
    print("=" * 80)
    
    # 初始化评分引擎
    engine = ScoringEngine(api_key=API_KEY)
    
    # 测试内容 - 使用一个简短的教学反思
    test_content = """
    教学反思
    
    本节课是关于Python基础语法的教学。通过本节课的教学，我发现学生对于变量和数据类型的理解还不够深入。
    
    在教学过程中，我采用了案例教学法，通过实际的代码示例来讲解概念。学生的反应比较积极，但在实践环节中，
    部分学生还是出现了一些错误。
    
    今后需要加强实践环节的指导，多给学生提供练习的机会。同时，需要更多地关注学生的个体差异，
    对于基础较弱的学生要给予更多的帮助。
    """
    
    print("\n📝 测试内容:")
    print("-" * 80)
    print(test_content.strip())
    print("-" * 80)
    
    # 执行评分
    print("\n🤖 正在调用DeepSeek API进行评分...")
    print("⏳ 请稍候，这可能需要几秒钟...")
    
    result = engine.score_file(
        file_type="教学反思",
        content=test_content,
        total_score=100
    )
    
    # 显示结果
    print("\n" + "=" * 80)
    print("📊 评分结果")
    print("=" * 80)
    
    if result.get("success"):
        print(f"\n✅ 评分成功!")
        print(f"📈 最终得分: {result['final_score']}分")
        print(f"🏆 评定等级: {result['grade']}")
        print(f"⚠️  触发否决: {'是' if result.get('veto_triggered') else '否'}")
        
        if result.get('veto_triggered'):
            print(f"🚫 否决原因: {result.get('veto_reason')}")
        
        # 显示详细评分
        if result.get('score_details'):
            print("\n📋 详细评分:")
            print("-" * 80)
            for detail in result['score_details']:
                print(f"• {detail['indicator']}: {detail['score']}/{detail['max_score']}分")
                print(f"  理由: {detail['reason']}")
                print()
        
        # 显示结构化反馈
        if result.get('summary'):
            print("\n💬 评分反馈 (结构化格式):")
            print("=" * 80)
            print(result['summary'])
            print("=" * 80)
            
            # 检查是否包含结构化标记
            summary = result['summary']
            has_structure = (
                '【总体评价】' in summary or
                '【主要优点】' in summary or
                '【存在问题】' in summary or
                '【改进建议】' in summary
            )
            
            if has_structure:
                print("\n✅ 反馈格式验证: 包含结构化标记")
            else:
                print("\n⚠️  反馈格式验证: 未检测到结构化标记")
                print("   AI可能没有完全按照要求的格式输出")
        
    else:
        print(f"\n❌ 评分失败!")
        print(f"错误信息: {result.get('error', '未知错误')}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_structured_feedback()
