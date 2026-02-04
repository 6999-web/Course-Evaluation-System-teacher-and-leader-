#!/usr/bin/env python3
"""
诊断AI评分错误
"""

import requests
import json

def diagnose_scoring_issue():
    """诊断评分问题"""
    print("🔍 诊断AI评分错误")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录系统...")
    try:
        login_response = requests.post("http://localhost:8001/api/login", json={
            "username": "admin",
            "password": "123456"
        }, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"   响应: {login_response.text}")
            return
        
        token_data = login_response.json()
        token = token_data.get('token', {}).get('access_token') or token_data.get('access_token')
        
        if not token:
            print(f"❌ 无法获取token")
            print(f"   响应: {json.dumps(token_data, indent=2, ensure_ascii=False)}")
            return
        
        print(f"✅ 登录成功")
        print(f"   Token: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 获取任务列表
    print("\n2. 获取考评任务...")
    try:
        tasks_response = requests.get(
            "http://localhost:8001/api/evaluation-tasks",
            headers={"Authorization": f"Bearer {token}"},
            params={"status": "submitted", "page": 1, "page_size": 10},
            timeout=10
        )
        
        if tasks_response.status_code != 200:
            print(f"❌ 获取任务失败: {tasks_response.status_code}")
            print(f"   响应: {tasks_response.text}")
            return
        
        tasks_data = tasks_response.json()
        tasks = tasks_data.get('tasks', [])
        
        if not tasks:
            print("⚠️  没有已提交的任务")
            return
        
        print(f"✅ 找到 {len(tasks)} 个已提交的任务")
        
        # 显示第一个任务的详细信息
        task = tasks[0]
        print(f"\n📋 任务详情:")
        print(f"   task_id: {task.get('task_id')}")
        print(f"   teacher_id: {task.get('teacher_id')}")
        print(f"   template_name: {task.get('template_name')}")
        print(f"   status: {task.get('status')}")
        print(f"   submitted_files: {json.dumps(task.get('submitted_files', []), indent=4, ensure_ascii=False)}")
        
        task_id = task.get('task_id')
        
    except Exception as e:
        print(f"❌ 获取任务异常: {e}")
        return
    
    # 3. 测试AI评分
    print(f"\n3. 测试AI评分...")
    print(f"   URL: http://localhost:8001/api/scoring/score/{task_id}")
    
    try:
        scoring_response = requests.post(
            f"http://localhost:8001/api/scoring/score/{task_id}",
            json=[],  # 空的加分项
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        print(f"   状态码: {scoring_response.status_code}")
        
        if scoring_response.status_code == 200:
            result = scoring_response.json()
            print(f"\n✅ AI评分成功!")
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"\n❌ AI评分失败")
            print(f"   状态码: {scoring_response.status_code}")
            print(f"   响应: {scoring_response.text}")
            
            # 尝试解析错误详情
            try:
                error_data = scoring_response.json()
                print(f"\n错误详情:")
                print(f"   {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                pass
        
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（60秒）")
    except Exception as e:
        print(f"❌ 评分异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("AI评分错误诊断")
    print("🎯" * 30 + "\n")
    
    diagnose_scoring_issue()
    
    print("\n" + "=" * 60)
    print("📝 诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
