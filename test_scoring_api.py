#!/usr/bin/env python3
"""
测试评分API
"""

import requests
import json

def test_scoring_api():
    """测试评分API"""
    print("🔍 测试评分API")
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
            params={"status": "submitted", "page": 1, "page_size": 1},
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
        
        task = tasks[0]
        task_id = task.get('task_id')
        print(f"✅ 找到任务: {task_id}")
        print(f"   教师: {task.get('teacher_id')}")
        print(f"   考评表: {task.get('template_name')}")
        
    except Exception as e:
        print(f"❌ 获取任务异常: {e}")
        return
    
    # 3. 调用评分API
    print(f"\n3. 调用评分API...")
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
            print(f"\n✅ 评分成功!")
            scoring = result.get('scoring_result', {})
            print(f"   最终得分: {scoring.get('final_score')}分")
            print(f"   评定等级: {scoring.get('grade')}")
            print(f"   一票否决: {scoring.get('veto_triggered')}")
            if scoring.get('veto_triggered'):
                print(f"   否决原因: {scoring.get('veto_reason')}")
        else:
            print(f"\n❌ 评分失败")
            print(f"   响应: {response.text}")
        
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
    except Exception as e:
        print(f"❌ 评分异常: {e}")

if __name__ == "__main__":
    test_scoring_api()
