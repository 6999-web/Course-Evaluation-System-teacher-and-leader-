#!/usr/bin/env python3
"""
简化的DeepSeek API测试
"""

import requests
import json
import os
from datetime import datetime

def test_basic_flow():
    """测试基本流程"""
    print("🚀 开始DeepSeek API自动评分测试")
    print("=" * 50)
    
    # 1. 登录测试
    print("1. 测试管理员登录...")
    try:
        response = requests.post("http://localhost:8001/api/login", json={
            "username": "admin",
            "password": "123456"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", {}).get("access_token")
            print("✅ 管理员登录成功")
        else:
            print(f"❌ 管理员登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    # 2. 创建测试文件
    print("\n2. 创建测试教案文件...")
    test_content = """
高等数学教学设计

课程名称：函数极限与连续性
授课对象：大学一年级学生
学时：2学时

一、教学目标
1. 知识目标：
   - 理解函数极限的概念和性质
   - 掌握极限的计算方法
   - 了解函数连续性的定义

2. 能力目标：
   - 培养学生的逻辑思维能力
   - 提高数学分析和解决问题的能力
   - 增强数学建模意识

3. 情感目标：
   - 激发学生对数学的兴趣
   - 培养严谨的学习态度
   - 增强团队合作精神

二、教学重点与难点
重点：函数极限的定义、性质和基本计算方法
难点：ε-δ定义的理解和应用

三、教学内容与过程
1. 导入环节（10分钟）
   - 通过实际问题引入极限概念
   - 复习相关预备知识

2. 新课讲授（60分钟）
   - 函数极限的直观理解
   - 极限的精确定义
   - 极限的性质和运算法则
   - 典型例题分析

3. 练习巩固（20分钟）
   - 课堂练习
   - 学生讨论交流

4. 总结提升（10分钟）
   - 知识点梳理
   - 布置课后作业

四、教学方法
采用启发式教学、问题驱动、多媒体辅助等方法，
注重理论与实践相结合，培养学生的创新思维。

五、教学评价
通过课堂表现、练习完成情况、课后作业等多种方式
进行综合评价，及时反馈学生学习效果。

六、教学反思
本教学设计注重学生的主体地位，通过多种教学方法
激发学生学习兴趣，提高教学效果。在实际教学中，
需要根据学生的具体情况灵活调整教学策略。
"""
    
    os.makedirs("test_materials", exist_ok=True)
    with open("test_materials/高等数学教案.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    print("✅ 测试教案文件创建成功")
    
    # 3. 提交材料测试
    print("\n3. 测试材料提交...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        submission_data = {
            "submission_id": f"deepseek_test_{int(datetime.now().timestamp())}",
            "teacher_id": "teacher_001",
            "teacher_name": "张教授",
            "files": [
                {
                    "file_id": "test_lesson_plan_deepseek",
                    "file_name": "高等数学教案.txt",
                    "file_size": len(test_content),
                    "file_url": "uploads/submissions/teacher_001/高等数学教案.txt"
                }
            ],
            "notes": "提交高等数学教学设计，请使用DeepSeek API进行自动评分",
            "submitted_at": datetime.now().isoformat()
        }
        
        response = requests.post(
            "http://localhost:8001/api/teacher/sync-submission",
            headers=headers,
            json=submission_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✅ 材料提交成功")
            submission_id = submission_data["submission_id"]
        else:
            print(f"❌ 材料提交失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 材料提交异常: {e}")
        return False
    
    # 4. DeepSeek API自动评分测试
    print("\n4. 测试DeepSeek API自动评分...")
    try:
        response = requests.post(
            f"http://localhost:8001/api/scoring/score/{submission_id}",
            headers=headers,
            json=[],
            timeout=30  # DeepSeek API可能需要更长时间
        )
        
        print(f"评分状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("scoring_result", {})
                print("🎉 DeepSeek API自动评分成功!")
                print(f"  📊 基础分数: {result.get('base_score', 0)}")
                print(f"  🏆 最终得分: {result.get('final_score', 0)}")
                print(f"  📈 评定等级: {result.get('grade', '')}")
                print(f"  ⚠️  触发否决: {result.get('veto_triggered', False)}")
                
                if result.get('veto_triggered'):
                    print(f"  🚫 否决原因: {result.get('veto_reason', '')}")
                else:
                    # 显示详细评分
                    score_details = result.get('score_details', [])
                    if score_details:
                        print("  📋 详细评分:")
                        for detail in score_details:
                            indicator = detail.get('indicator', '')
                            score = detail.get('score', 0)
                            max_score = detail.get('max_score', 0)
                            reason = detail.get('reason', '')
                            print(f"    • {indicator}: {score}/{max_score}分 - {reason}")
                
                summary = result.get('summary', '')
                if summary:
                    print(f"  💬 AI评价总结:")
                    print(f"    {summary}")
                
                return True
            else:
                print("❌ 自动评分失败")
                return False
        else:
            error_text = response.text
            print(f"❌ 评分请求失败: {error_text}")
            
            # 分析错误类型
            if "API" in error_text or "DeepSeek" in error_text:
                print("💡 这可能是DeepSeek API相关的问题")
            elif "文件" in error_text:
                print("💡 这可能是文件处理相关的问题")
            
            return False
    except Exception as e:
        print(f"❌ 自动评分异常: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 DeepSeek API自动评分测试完成!")
    return True

if __name__ == "__main__":
    success = test_basic_flow()
    if success:
        print("✅ 所有测试通过 - DeepSeek API自动评分系统工作正常!")
    else:
        print("❌ 测试失败 - 请检查系统配置")