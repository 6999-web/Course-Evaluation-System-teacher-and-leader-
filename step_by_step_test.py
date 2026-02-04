#!/usr/bin/env python3
"""
逐步测试考评表流程
"""

import requests
import json
import os
from datetime import datetime

def test_admin_login():
    """测试管理员登录"""
    print("1. 测试管理员登录...")
    try:
        response = requests.post("http://localhost:8001/api/login", json={
            "username": "admin",
            "password": "123456"
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", {}).get("access_token")
            print("✅ 管理员登录成功")
            return token
        else:
            print(f"❌ 管理员登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def create_test_content():
    """创建测试内容"""
    print("\n2. 创建测试内容...")
    
    # 创建一个真实的教案内容
    lesson_plan = """
《函数极限》教学设计

一、教学目标
1. 知识与技能目标
   - 理解函数极限的概念和几何意义
   - 掌握极限的基本性质和运算法则
   - 能够计算简单函数的极限

2. 过程与方法目标
   - 通过图形直观理解极限概念
   - 培养学生的数学思维和逻辑推理能力
   - 学会用数学语言描述极限过程

3. 情感态度价值观目标
   - 感受数学的严谨性和美感
   - 培养探索精神和创新意识
   - 增强学习数学的兴趣和信心

二、教学重点与难点
重点：函数极限的定义、性质和基本计算
难点：ε-δ定义的理解和应用

三、教学方法
采用启发式教学、问题驱动、多媒体辅助等方法，
通过具体实例引入概念，循序渐进地展开教学。

四、教学过程设计

1. 导入新课（5分钟）
   通过实际问题引入极限概念：
   - 圆的面积近似计算
   - 瞬时速度的求解

2. 概念建构（20分钟）
   (1) 函数极限的直观理解
       - 图形演示
       - 数值逼近
   
   (2) 极限的精确定义
       - ε-δ定义
       - 几何意义解释

3. 性质探究（15分钟）
   - 极限的唯一性
   - 局部有界性
   - 保号性
   - 运算法则

4. 例题讲解（15分钟）
   例1：计算 lim(x→2) (x²-4)/(x-2)
   例2：计算 lim(x→0) sin(x)/x
   例3：计算 lim(x→∞) (1+1/x)^x

5. 课堂练习（10分钟）
   学生独立完成练习题，教师巡视指导

6. 课堂小结（5分钟）
   - 回顾本节课主要内容
   - 强调重点难点
   - 预告下节课内容

五、板书设计
左侧：概念定义和性质
中间：例题解答过程
右侧：重要公式和结论

六、作业布置
1. 教材习题：P45 第1-8题
2. 思考题：极限在实际生活中的应用

七、教学反思
本节课通过多种教学方法，帮助学生理解了函数极限的概念。
在今后的教学中，需要更多关注学生的个体差异，
加强对学习困难学生的辅导。
"""
    
    # 创建目录
    os.makedirs("test_materials", exist_ok=True)
    
    # 保存文件
    with open("test_materials/教案.txt", "w", encoding="utf-8") as f:
        f.write(lesson_plan)
    
    print("✅ 测试内容创建成功: test_materials/教案.txt")
    return True

def test_material_submission(token):
    """测试材料提交"""
    print("\n3. 测试材料提交...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 提交材料数据
        submission_data = {
            "submission_id": f"test_sub_{int(datetime.now().timestamp())}",
            "teacher_id": "teacher_001",
            "teacher_name": "张三",
            "files": [
                {
                    "file_id": "test_lesson_plan_001",
                    "file_name": "教案.txt",
                    "file_size": 2048,
                    "file_url": "test_materials/教案.txt"
                }
            ],
            "notes": "提交教学设计方案，请审核评分",
            "submitted_at": datetime.now().isoformat()
        }
        
        response = requests.post(
            "http://localhost:8001/api/teacher/sync-submission",
            headers=headers,
            json=submission_data
        )
        
        print(f"提交状态码: {response.status_code}")
        print(f"提交响应: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ 材料提交成功")
            return submission_data["submission_id"]
        else:
            print("❌ 材料提交失败")
            return None
            
    except Exception as e:
        print(f"❌ 材料提交异常: {e}")
        return None

def test_auto_scoring(token, submission_id):
    """测试自动评分"""
    print("\n4. 测试自动评分...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 如果没有提供submission_id，获取最新的提交
        if not submission_id:
            response = requests.get("http://localhost:8001/api/materials/submissions", headers=headers)
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                if submissions:
                    submission_id = submissions[0].get("submission_id")
                    print(f"使用最新提交: {submission_id}")
                else:
                    print("❌ 没有找到提交记录")
                    return False
            else:
                print("❌ 获取提交列表失败")
                return False
        
        # 执行自动评分
        response = requests.post(
            f"http://localhost:8001/api/scoring/score/{submission_id}",
            headers=headers,
            json=[]
        )
        
        print(f"评分状态码: {response.status_code}")
        print(f"评分响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("scoring_result", {})
                print("✅ 自动评分成功!")
                print(f"  基础分: {result.get('base_score', 0)}")
                print(f"  最终分: {result.get('final_score', 0)}")
                print(f"  等级: {result.get('grade', '')}")
                print(f"  是否触发否决: {result.get('veto_triggered', False)}")
                
                if result.get('veto_triggered'):
                    print(f"  否决原因: {result.get('veto_reason', '')}")
                else:
                    # 显示评分详情
                    score_details = result.get('score_details', [])
                    if score_details:
                        print("  评分详情:")
                        for detail in score_details:
                            print(f"    {detail.get('indicator', '')}: {detail.get('score', 0)}/{detail.get('max_score', 0)}分")
                
                summary = result.get('summary', '')
                if summary:
                    print(f"  评价总结: {summary[:200]}...")
                
                return True
            else:
                print("❌ 自动评分失败")
                return False
        else:
            print("❌ 自动评分请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 自动评分异常: {e}")
        return False

def test_scoring_record(token, submission_id):
    """测试评分记录查询"""
    print("\n5. 测试评分记录查询...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"http://localhost:8001/api/scoring/records/{submission_id}",
            headers=headers
        )
        
        print(f"查询状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 评分记录查询成功")
            print(f"  提交ID: {data.get('submission_id')}")
            print(f"  教师: {data.get('teacher_name')}")
            print(f"  审核状态: {data.get('review_status')}")
            
            scoring_result = data.get('scoring_result', {})
            if scoring_result:
                print(f"  最终得分: {scoring_result.get('final_score', 0)}分")
                print(f"  评定等级: {scoring_result.get('grade', '')}")
            
            return True
        else:
            print("❌ 评分记录查询失败")
            return False
            
    except Exception as e:
        print(f"❌ 评分记录查询异常: {e}")
        return False

def main():
    print("🚀 逐步测试考评表流程")
    print("=" * 50)
    
    # 1. 管理员登录
    token = test_admin_login()
    if not token:
        return
    
    # 2. 创建测试内容
    if not create_test_content():
        return
    
    # 3. 提交材料
    submission_id = test_material_submission(token)
    if not submission_id:
        return
    
    # 4. 自动评分
    if not test_auto_scoring(token, submission_id):
        return
    
    # 5. 查询评分记录
    if not test_scoring_record(token, submission_id):
        return
    
    print("\n" + "=" * 50)
    print("🎉 所有测试步骤完成!")
    print("✅ DeepSeek API自动评分系统工作正常")
    print("=" * 50)

if __name__ == "__main__":
    main()