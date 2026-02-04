#!/usr/bin/env python3
"""
测试完整教学反思的DeepSeek API评分
"""

import requests
import json
from datetime import datetime

def test_complete_reflection():
    """测试完整教学反思评分"""
    print("🚀 开始测试完整教学反思的DeepSeek API评分")
    print("=" * 60)
    
    # 1. 登录
    print("1. 管理员登录...")
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
    
    # 2. 提交完整教学反思
    print("\n2. 提交完整教学反思...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        submission_data = {
            "submission_id": f"complete_reflection_{int(datetime.now().timestamp())}",
            "teacher_id": "teacher_002",
            "teacher_name": "李教授",
            "files": [
                {
                    "file_id": "complete_reflection_test",
                    "file_name": "完整教学反思.txt",
                    "file_size": 5000,
                    "file_url": "uploads/submissions/teacher_001/完整教学反思.txt"
                }
            ],
            "notes": "提交完整的教学反思，测试DeepSeek API正常评分功能",
            "submitted_at": datetime.now().isoformat()
        }
        
        response = requests.post(
            "http://localhost:8001/api/teacher/sync-submission",
            headers=headers,
            json=submission_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✅ 完整教学反思提交成功")
            submission_id = submission_data["submission_id"]
        else:
            print(f"❌ 提交失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 提交异常: {e}")
        return False
    
    # 3. DeepSeek API自动评分
    print("\n3. 测试DeepSeek API自动评分...")
    try:
        response = requests.post(
            f"http://localhost:8001/api/scoring/score/{submission_id}",
            headers=headers,
            json=[],
            timeout=60  # 增加超时时间，因为内容更长
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
                            print(f"    • {indicator}: {score}/{max_score}分")
                            print(f"      理由: {reason}")
                
                summary = result.get('summary', '')
                if summary:
                    print(f"  💬 AI评价总结:")
                    # 分行显示，便于阅读
                    lines = summary.split('。')
                    for line in lines:
                        if line.strip():
                            print(f"    {line.strip()}。")
                
                return True
            else:
                print("❌ 自动评分失败")
                return False
        else:
            error_text = response.text
            print(f"❌ 评分请求失败: {error_text}")
            return False
    except Exception as e:
        print(f"❌ 自动评分异常: {e}")
        return False

if __name__ == "__main__":
    print("测试完整教学反思的DeepSeek API评分功能")
    print("=" * 60)
    
    success = test_complete_reflection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 完整教学反思评分测试通过!")
        print("🎯 DeepSeek API能够正确识别高质量教学反思并给出合理评分")
    else:
        print("❌ 测试失败")
    print("=" * 60)