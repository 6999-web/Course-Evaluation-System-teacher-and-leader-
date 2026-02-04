#!/usr/bin/env python3
"""
测试AI评分修复 - 验证task_id可以正常工作
"""

import requests
import json

def test_ai_scoring():
    """测试AI评分功能"""
    print("🧪 测试AI评分修复")
    print("=" * 60)
    
    # 1. 登录获取token
    print("\n1. 登录系统...")
    login_response = requests.post("http://localhost:8001/api/login", json={
        "username": "admin",
        "password": "123456"
    })
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        return False
    
    token = login_response.json()['token']['access_token']
    print("✅ 登录成功")
    
    # 2. 获取任务列表
    print("\n2. 获取考评任务列表...")
    tasks_response = requests.get(
        "http://localhost:8001/api/evaluation-tasks",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "submitted", "page": 1, "page_size": 10}
    )
    
    if tasks_response.status_code != 200:
        print(f"❌ 获取任务失败: {tasks_response.status_code}")
        return False
    
    tasks_data = tasks_response.json()
    tasks = tasks_data.get('tasks', [])
    
    if not tasks:
        print("⚠️  没有已提交的任务可供测试")
        print("   请先在教师端提交一个任务")
        return False
    
    print(f"✅ 找到 {len(tasks)} 个已提交的任务")
    
    # 3. 测试AI评分
    test_task = tasks[0]
    task_id = test_task['task_id']
    print(f"\n3. 测试AI评分...")
    print(f"   任务ID: {task_id}")
    print(f"   教师: {test_task.get('teacher_id')}")
    print(f"   考评表: {test_task.get('template_name')}")
    
    # 调用AI评分接口
    print("\n   调用AI评分接口...")
    scoring_response = requests.post(
        f"http://localhost:8001/api/scoring/score/{task_id}",
        json=[],  # 空的加分项
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   响应状态码: {scoring_response.status_code}")
    
    if scoring_response.status_code == 200:
        result = scoring_response.json()
        if result.get('success'):
            scoring_result = result.get('scoring_result', {})
            print("\n✅ AI评分成功!")
            print(f"   最终得分: {scoring_result.get('final_score')}分")
            print(f"   评定等级: {scoring_result.get('grade')}")
            print(f"   是否触发否决: {scoring_result.get('veto_triggered')}")
            if scoring_result.get('summary'):
                print(f"   AI评价: {scoring_result.get('summary')[:100]}...")
            return True
        else:
            print(f"❌ 评分失败: {result}")
            return False
    else:
        print(f"❌ API调用失败")
        print(f"   错误信息: {scoring_response.text}")
        return False

def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("AI评分修复测试")
    print("🎯" * 30 + "\n")
    
    success = test_ai_scoring()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试通过！AI评分功能已修复！")
        print("\n现在可以在前端点击'AI自动评分'按钮了")
    else:
        print("⚠️  测试未完全通过")
        print("\n可能的原因:")
        print("1. 后端服务需要重启以应用代码更改")
        print("2. 没有已提交的任务可供测试")
        print("3. 文件路径或格式问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
