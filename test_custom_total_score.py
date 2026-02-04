#!/usr/bin/env python3
"""
测试自定义总分的评分系统
"""

import requests
import json

def test_custom_score():
    """测试自定义总分评分"""
    print("🔍 测试自定义总分评分系统")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录...")
    try:
        response = requests.post("http://localhost:8001/api/login", json={
            "username": "admin",
            "password": "123456"
        }, timeout=5)
        
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code}")
            return
        
        data = response.json()
        token = data.get('token', {}).get('access_token') or data.get('access_token')
        print(f"✅ 登录成功")
        
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取已提交的任务
    print("\n2. 获取已提交的任务...")
    try:
        response = requests.get(
            "http://localhost:8001/api/evaluation-tasks",
            headers={"Authorization": f"Bearer {token}"},
            params={"status": "submitted", "page": 1, "page_size": 5},
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"❌ 获取任务失败: {response.status_code}")
            return
        
        data = response.json()
        tasks = data.get('tasks', [])
        
        if not tasks:
            print("⚠️  没有已提交的任务")
            return
        
        print(f"✅ 找到 {len(tasks)} 个已提交的任务")
        
        # 显示任务信息
        for i, task in enumerate(tasks, 1):
            print(f"\n任务 {i}:")
            print(f"  task_id: {task.get('task_id')}")
            print(f"  考评表: {task.get('template_name')}")
            print(f"  总分: {task.get('total_score')}分")
            print(f"  评分标准: {len(task.get('scoring_criteria', []))}个指标")
            
            # 显示评分标准
            if task.get('scoring_criteria'):
                print(f"  指标详情:")
                for criterion in task.get('scoring_criteria', []):
                    print(f"    - {criterion.get('name')}: {criterion.get('max_score')}分")
        
        # 选择第一个任务进行测试
        task = tasks[0]
        task_id = task.get('task_id')
        total_score = task.get('total_score', 100)
        
    except Exception as e:
        print(f"❌ 获取任务异常: {e}")
        return
    
    # 3. 测试AI评分
    print(f"\n3. 测试AI评分（总分: {total_score}分）...")
    print(f"   URL: http://localhost:8001/api/scoring/score/{task_id}")
    
    try:
        response = requests.post(
            f"http://localhost:8001/api/scoring/score/{task_id}",
            json=[],
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ AI评分成功!")
            scoring = result.get('scoring_result', {})
            
            print(f"\n评分结果:")
            print(f"  基础分: {scoring.get('base_score')}分")
            print(f"  加分: {scoring.get('bonus_score')}分")
            print(f"  最终得分: {scoring.get('final_score')}分 / {total_score}分")
            print(f"  得分率: {(scoring.get('final_score', 0) / total_score * 100):.1f}%")
            print(f"  评定等级: {scoring.get('grade')}")
            print(f"  一票否决: {scoring.get('veto_triggered')}")
            
            if scoring.get('score_details'):
                print(f"\n分项得分:")
                for detail in scoring.get('score_details', []):
                    print(f"  - {detail.get('indicator')}: {detail.get('score')}/{detail.get('max_score')}分")
                    print(f"    理由: {detail.get('reason')}")
            
            if scoring.get('summary'):
                print(f"\n总体评价:")
                print(f"  {scoring.get('summary')}")
            
            return True
        else:
            print(f"\n❌ AI评分失败")
            print(f"   响应: {response.text}")
            return False
        
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 评分异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_custom_score()
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过 - 自定义总分评分系统正常工作")
    else:
        print("❌ 测试失败")
