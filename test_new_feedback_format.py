"""测试新的反馈格式"""
import sys
sys.path.insert(0, '评教系统最终版/评教系统管理端/backend_8fMBP/backend')

from app.scoring_engine import ScoringEngine
import os

# DeepSeek API配置
API_KEY = "sk-b6ca926900534f1fa31067d49980ec56"

# 测试内容
test_content = """
教学反思

本学期我担任高等数学课程的教学工作，经过一学期的教学实践，我对《函数极限与连续性》这节课进行了深入反思。

一、教学实践回顾
在本节课中，我采用了"问题导入-概念讲解-例题分析-练习巩固"的教学模式。通过生活中的实例（如物体运动的瞬时速度）引入极限概念，学生的学习兴趣得到了激发。但在概念讲解环节，我发现部分学生对ε-δ语言的理解存在困难，课堂互动不够充分。

二、深层次反思
从教学理论角度分析，我的教学存在以下问题：
1. 建构主义理论应用不足：我过于注重知识的传授，忽视了学生已有的认知结构。学生在高中阶段对极限已有初步认识，但我没有充分利用这一基础进行知识建构。
2. 最近发展区理论把握不准：ε-δ语言对大一学生来说难度较大，我应该设计更多的过渡性问题，帮助学生逐步理解。
3. 以学生为中心的理念落实不够：课堂上我讲解时间过长，学生思考和讨论的时间不足。

三、改进措施
针对上述问题，我制定了以下具体改进措施：
1. 在"改进措施"中，我将：
   - 设计分层练习：基础题（如"设计分层练习"）可进一步具体化，例如简单说明分层的大致标准或题型示例，以增强可操作性。
   - 时间节点：如"1-2周"很好，部分中期和长期计划（如"建立学生学习档案"）若能与具体的课程进度或考核节点结合，则实施路径会更清晰。

2. "后续行动计划"中的时间节点（如"1-2周"）很好，部分中期和长期计划（如"建立学生学习档案"）若能与具体的课程进度或考核节点结合，则实施路径会更清晰。

四、专业发展规划
短期目标（本学期）：
- 完成《建构主义教学理论》的系统学习
- 参加校内教学观摩活动至少3次
- 建立学生学习档案，跟踪学习效果

中期目标（1-2年）：
- 申报校级教改项目，研究"基于建构主义的高等数学教学模式"
- 发表教学研究论文1-2篇
- 指导青年教师2-3名

长期目标（3-5年）：
- 形成个人教学特色和风格
- 成为校级教学名师
- 出版高等数学教学专著

通过本次反思，我深刻认识到教学不仅是知识的传递，更是学生思维能力的培养。我将继续学习教育理论，改进教学方法，努力成为一名优秀的高等数学教师。
"""

print("=" * 80)
print("测试新的反馈格式")
print("=" * 80)

# 创建评分引擎
engine = ScoringEngine(api_key=API_KEY)

# 进行评分
print("\n正在调用DeepSeek API进行评分...")
result = engine.score_file(
    file_type="教学反思",
    content=test_content,
    total_score=100
)

print("\n" + "=" * 80)
print("评分结果")
print("=" * 80)

if result.get("success"):
    print(f"\n✓ 评分成功")
    print(f"  否决项触发: {result.get('veto_triggered', False)}")
    
    if result.get('veto_triggered'):
        print(f"  否决原因: {result.get('veto_reason', '')}")
    else:
        print(f"  基础分: {result.get('base_score', 0)}")
        print(f"  加分: {result.get('bonus_score', 0)}")
        print(f"  最终得分: {result.get('final_score', 0)}")
        print(f"  等级: {result.get('grade', '')}")
        
        print(f"\n各项评分详情:")
        for detail in result.get('score_details', []):
            print(f"  • {detail['indicator']}: {detail['score']}/{detail['max_score']}分")
            print(f"    理由: {detail['reason']}")
        
        print(f"\n评分反馈:")
        print("-" * 80)
        print(result.get('summary', ''))
        print("-" * 80)
else:
    print(f"\n✗ 评分失败")
    print(f"  错误: {result.get('error', '未知错误')}")

print("\n" + "=" * 80)
