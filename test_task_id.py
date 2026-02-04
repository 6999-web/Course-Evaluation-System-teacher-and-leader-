#!/usr/bin/env python3
"""
测试task_id格式
"""

import requests
import json

def test_task_id():
    """测试task_id"""
    print("🔍 测试task_id格式")
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
    
    # 2. 获取任务列表
    print("\n2. 获取任务列表...")
    try:
        response = requests.get(
            "http://localhost:8001/api/evaluation-tasks",
            headers={"Authorization": f"Bearer {token}"},
            params={"status": "submitted", "page": 1, "page_size": 10},
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
        
        print(f"✅ 找到 {len(tasks)} 个任务")
        
        # 显示每个任务的task_id
        for i, task in enumerate(tasks, 1):
            print(f"\n任务 {i}:")
            print(f"  task_id: {task.get('task_id')}")
            print(f"  teacher_id: {task.get('teacher_id')}")
            print(f"  template_name: {task.get('template_name')}")
            print(f"  status: {task.get('status')}")
            print(f"  submitted_files: {json.dumps(task.get('submitted_files', []), ensure_ascii=False, indent=4)}")
        
    except Exception as e:
        print(f"❌ 获取任务异常: {e}")
        return

if __name__ == "__main__":
    test_task_id()
